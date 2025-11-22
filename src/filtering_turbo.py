import zstandard as zstd
import orjson
import os
import string
import multiprocessing
import time
from config import (
    TARGET_KEYWORDS, 
    MIN_TEXT_LENGTH, 
    MIN_POSITIVE_SCORE, 
    MAX_NEGATIVE_SCORE,
    SHORT_TEXT_WHITELIST
)

# --- PODEŠAVANJA PERFORMANSI ---
BATCH_SIZE = 5000       # Broj linija koje Reader šalje Workerima odjednom (smanjuje IPC overhead)
QUEUE_SIZE = 100        # Koliko batcheva može da stoji u memoriji
RECORDS_PER_FILE = 100000 # Rotacija fajlova

# Globalne promenljive za Workere (da ne bi picklovali config svaki put)
# Pretvaramo keywords u set bajtova ili stringova radi brzine, zavisno kako orjson vraća
# orjson vraća stringove po defaultu, ali radi ultra brzo.
TARGET_KEYWORDS_SET = set(TARGET_KEYWORDS) # Set je O(1), lista je O(N) - mada za substring search mora lista
SHORT_TEXT_WHITELIST_SET = set(SHORT_TEXT_WHITELIST)

def get_chunk_filename(base_filename, part_number):
    name, ext = os.path.splitext(base_filename)
    return f"{name}_part_{part_number:03d}{ext}"

def check_filters(text, score):
    """Vraća True ako prolazi filtere."""
    # 1. Score Filter
    valid_score = (score >= MIN_POSITIVE_SCORE) or (score <= MAX_NEGATIVE_SCORE)
    if not valid_score:
        return False

    if not text:
        return False

    # 2. Length / Whitelist Filter
    if len(text) < MIN_TEXT_LENGTH:
        # Provera whitelist-e za kratke tekstove
        # Čišćenje interpunkcije je skupo, radimo samo ako mora
        clean_text = text.lower().translate(str.maketrans('', '', string.punctuation))
        words = clean_text.split()
        if not any(word in SHORT_TEXT_WHITELIST_SET for word in words):
            return False
    
    # 3. Keyword Filter (Najskuplji, radimo na kraju)
    text_lower = text.lower()
    # any() sa generatorom je brz, ali mora da prođe kroz listu
    if not any(keyword in text_lower for keyword in TARGET_KEYWORDS):
        return False
        
    return True

def worker_task(input_queue, output_queue, item_type):
    """
    Proces koji uzima batch sirovih linija, parsuje i filtrira.
    """
    while True:
        batch = input_queue.get()
        if batch is None: # Sentinel value za kraj
            output_queue.put(None)
            break
        
        processed_batch = []
        
        for line in batch:
            try:
                # orjson je mnogo brži od json biblioteke
                data = orjson.loads(line)
                
                # Određivanje polja
                if item_type == "submission":
                    text_body = data.get("selftext", "")
                    title = data.get("title", "")
                    full_text = f"{title} {text_body}"
                    score = data.get("score", 0)
                else: # comment
                    full_text = data.get("body", "")
                    score = data.get("score", 0)
                
                # Provera filtera
                if check_filters(full_text, score):
                    
                    # Priprema podataka
                    minified = {
                        "id": data.get("id"),
                        "subreddit": data.get("subreddit"),
                        "score": score,
                        "text": full_text,
                        "type": item_type
                    }
                    
                    if item_type == "submission":
                        minified["num_comments"] = data.get("num_comments", 0)
                        minified["title"] = data.get("title", "")
                    
                    if item_type == "comment":
                        link_id = data.get("link_id", "")
                        minified["link_id"] = link_id
                        
                        # --- OVO JE NOVO: PARENT_ID LOGIKA ---
                        # t3_xxxxx -> xxxxx
                        if link_id.startswith("t3_"):
                            minified["parent_id"] = link_id[3:]
                        else:
                            minified["parent_id"] = link_id
                    
                    # Serijalizujemo nazad u string (ili bytes) pre slanja writeru
                    # da writer ne troši CPU na serijalizaciju
                    processed_batch.append(orjson.dumps(minified))
                    
            except orjson.JSONDecodeError:
                continue
            except Exception:
                continue
        
        if processed_batch:
            output_queue.put(processed_batch)

def writer_task(output_queue, output_base_name, num_workers):
    """
    Proces koji samo piše u fajl i rotira fajlove.
    """
    current_part = 1
    current_count = 0
    
    filename = get_chunk_filename(output_base_name, current_part)
    f = open(filename, 'wb') # Pišemo bajtove direktno (orjson vraća bytes)
    print(f"📂 [Writer] Kreiram fajl: {filename}")
    
    workers_finished = 0
    total_saved = 0
    
    while True:
        batch = output_queue.get()
        
        if batch is None:
            workers_finished += 1
            if workers_finished == num_workers:
                break
            continue
            
        for record_bytes in batch:
            f.write(record_bytes)
            f.write(b'\n')
            current_count += 1
            total_saved += 1
            
            if current_count >= RECORDS_PER_FILE:
                f.close()
                print(f"✅ [Writer] Završen {filename} ({RECORDS_PER_FILE} zapisa)")
                
                current_part += 1
                current_count = 0
                filename = get_chunk_filename(output_base_name, current_part)
                f = open(filename, 'wb')
                print(f"📂 [Writer] Kreiram fajl: {filename}")
    
    f.close()
    print(f"🏁 [Writer] Gotovo. Ukupno sačuvano: {total_saved}")

def stream_and_filter_turbo(input_file, output_base_name, item_type="submission"):
    print(f"🚀 [Main] Počinjem TURBO obradu: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Greška: Fajl ne postoji.")
        return

    # Podesi broj workera: Broj jezgara - 2 (1 za Reader, 1 za Writer)
    num_cores = multiprocessing.cpu_count()
    num_workers = max(1, num_cores - 2) 
    
    print(f"⚙️  Koristim: {num_workers} Worker procesa + 1 Reader + 1 Writer")

    # Redovi za komunikaciju
    input_queue = multiprocessing.Queue(maxsize=QUEUE_SIZE)
    output_queue = multiprocessing.Queue(maxsize=QUEUE_SIZE)
    
    # Startuj Writer Proces
    writer = multiprocessing.Process(target=writer_task, args=(output_queue, output_base_name, num_workers))
    writer.start()
    
    # Startuj Worker Procese
    workers = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker_task, args=(input_queue, output_queue, item_type))
        p.start()
        workers.append(p)
    
    # --- MAIN PROCESS JE READER ---
    # Čitamo ZST i samo šaljemo batcheve workerima
    total_lines_read = 0
    start_time = time.time()
    
    try:
        with open(input_file, 'rb') as fh:
            dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
            with dctx.stream_reader(fh) as reader:
                import io
                # Buffer size veći za I/O performanse
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                
                batch = []
                for line in text_stream:
                    batch.append(line)
                    total_lines_read += 1
                    
                    if len(batch) >= BATCH_SIZE:
                        input_queue.put(batch)
                        batch = []
                        
                    if total_lines_read % 200000 == 0:
                        elapsed = time.time() - start_time
                        print(f"reading... {total_lines_read} lines read ({int(total_lines_read/elapsed)} lines/sec)")
                
                # Pošalji ostatak
                if batch:
                    input_queue.put(batch)

    except Exception as e:
        print(f"❌ Greška u Readeru: {e}")

    # Signaliziraj kraj workerima
    for _ in range(num_workers):
        input_queue.put(None)
        
    # Čekaj da završe
    for p in workers:
        p.join()
        
    writer.join() # Čekaj writera da zatvori fajl
    
    print(f"✨ [Main] Kompletna obrada završena.")

if __name__ == "__main__":
    # PRILAGODI PUTANJE
    base_path = "./dataset"
    
    # Primer za komentare (pošto ti je to bitno za parent_id)
    comment_input = os.path.join(base_path, "RC_2022-09.zst")
    
    if os.path.exists(comment_input):
        stream_and_filter_turbo(
            comment_input, 
            "filtered_comments-turbo.jsonl", 
            item_type="comment"
        )
    else:
        print("Nisam našao input fajl.")