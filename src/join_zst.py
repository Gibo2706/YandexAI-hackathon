import zstandard as zstd
import orjson
import os
import glob
import multiprocessing
import time
import gc
from tqdm import tqdm
from config import (
    MAX_COMMENTS_PER_POST, 
    MIN_COMMENT_POSITIVE_SCORE,
    TARGET_KEYWORDS
)

# --- KONFIGURACIJA ---
OUTPUT_DIR = "./dataset/output/documents"
DOCUMENTS_PER_FILE = 100000 
BATCH_SIZE = 5000  # Koliko linija worker uzima odjednom
QUEUE_SIZE = 50    # Buffer za redove

# Globalna promenljiva koja će držati set ID-jeva
# Na Linuxu se ovo efikasno deli sa child procesima (Copy-on-Write)
VALID_PARENT_IDS = None

# Crna lista
BLACKLIST_SUBREDDITS = {
    b"skincareaddiction", b"makeupaddiction", b"beauty", b"movies", b"gaming", 
    b"books", b"anime", b"kpop", b"fashion", b"cats", b"dogs", b"food", b"music"
}

def get_chunk_filename(output_dir, part_number):
    return os.path.join(output_dir, f"final_docs_part_{part_number:03d}.jsonl")

def load_submissions_master(pattern):
    """Učitava postove i vraća Mapu."""
    submissions = {}
    files = sorted(glob.glob(pattern))
    print(f"📥 [RAM] Učitavam postove...")
    
    stats = {"kept": 0}
    
    for file_path in files:
        with open(file_path, 'rb') as f:
            for line in f:
                try:
                    data = orjson.loads(line)
                    
                    # TVOJA ŽELJA: Svi filteri su isključeni da bi pokupio sve postove
                    # koje si već pripremio u filtered_submissions fazi.
                    
                    clean_obj = {
                        "post": {
                            "id": data["id"],
                            "title": data.get("title", ""),
                            "text": data.get("text", ""),
                            "subreddit": data.get("subreddit"),
                            "score": data.get("score", 0),
                            "num_comments": data.get("num_comments", 0)
                        },
                        "comments": [] 
                    }
                    submissions[data["id"]] = clean_obj
                    stats["kept"] += 1
                except:
                    continue

    print(f"✅ RAM napunjen: {stats['kept']} postova.")
    return submissions

# --- PROCESI ---

def reader_process(zst_path, input_queue, num_workers):
    """
    Čita ZST fajl i šalje batcheve linija.
    Samo JEDAN proces ovo radi, tako da je čitanje bezbedno i sekvencijalno.
    """
    print(f"📖 [Reader] Počinjem čitanje: {zst_path}")
    try:
        with open(zst_path, 'rb') as fh:
            dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
            with dctx.stream_reader(fh) as reader:
                import io
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                
                batch = []
                count = 0
                for line in text_stream:
                    batch.append(line)
                    count += 1
                    
                    # Šaljemo batch kad se napuni
                    if len(batch) >= BATCH_SIZE:
                        input_queue.put(batch)
                        batch = []
                    
                    if count % 500000 == 0:
                        print(f"   -> [Reader] Pročitano {count:,} linija...")
                
                # Pošalji ostatak
                if batch:
                    input_queue.put(batch)
                    
    except Exception as e:
        print(f"❌ Greška u Readeru: {e}")
    
    # Signaliziraj kraj svima
    for _ in range(num_workers):
        input_queue.put(None)
    print("📖 [Reader] Završio čitanje fajla.")

def worker_process(input_queue, output_queue):
    """
    Parsuje JSON i traži komentare koji pripadaju našim postovima.
    VALID_PARENT_IDS je dostupan globalno.
    """
    local_matches = []
    
    while True:
        batch = input_queue.get()
        if batch is None:
            break
        
        for line in batch:
            try:
                # orjson je ključ brzine
                c_data = orjson.loads(line)
                
                link_id = c_data.get("link_id", "")
                
                # 1. Izvuci parent_id (skini t3_)
                if link_id.startswith("t3_"):
                    parent_id = link_id[3:]
                else:
                    parent_id = link_id
                
                # 2. Proveri da li nam treba ovaj komentar (O(1) lookup u globalnom setu)
                if parent_id in VALID_PARENT_IDS:
                    
                    # SKLONJENI FILTERI PO TVOJOJ ŽELJI (da uhvatimo sve)
                    # score = c_data.get("score", 0)
                    # if score < MIN_COMMENT_POSITIVE_SCORE:
                    #     continue
                    
                    # 3. Pakuj rezultat
                    comment_obj = {
                        "id": c_data.get("id"),
                        "text": c_data.get("body", ""),
                        "score": c_data.get("score", 0),
                        "subreddit": c_data.get("subreddit"),
                        "parent_id": parent_id # <--- OVO SI TRAŽIO
                    }
                    local_matches.append(comment_obj)
                    
            except:
                continue
        
        # Šalji rezultate nazad u main proces ako ih ima
        if local_matches:
            output_queue.put(local_matches)
            local_matches = []

    # Kraj workera
    output_queue.put(None)

# --- MAIN ---

def main():
    global VALID_PARENT_IDS # Koristimo globalnu promenljivu za deljenje seta

    # PUTANJE
    SUBMISSIONS_PATTERN = "./dataset/filtered_submissions_part_*.jsonl"
    RAW_COMMENTS_ZST = "./dataset/RC_2022-09.zst"
    
    # 1. Učitaj postove u Main procesu
    submissions_map = load_submissions_master(SUBMISSIONS_PATTERN)
    
    if not submissions_map:
        print("❌ Nema postova.")
        return

    # Inicijalizujemo globalni set ID-jeva PRE kreiranja procesa
    # Ovo omogućava child procesima da ga naslede bez kopiranja memorije (na Linuxu)
    VALID_PARENT_IDS = set(submissions_map.keys())
    print(f"🔒 Set validnih ID-jeva pripremljen ({len(VALID_PARENT_IDS)}).")

    # 2. Konfiguracija Procesa
    num_cores = multiprocessing.cpu_count()
    # Ostavljamo 1 jezgro za Readera i 1 za Main proces (Aggregator)
    num_workers = max(1, num_cores - 2) 
    
    print(f"⚙️  Startujem: 1 Reader + {num_workers} Workera")
    
    input_queue = multiprocessing.Queue(maxsize=QUEUE_SIZE)
    output_queue = multiprocessing.Queue(maxsize=QUEUE_SIZE*2)
    
    # Start Reader (samo on dira disk za čitanje)
    p_reader = multiprocessing.Process(target=reader_process, args=(RAW_COMMENTS_ZST, input_queue, num_workers))
    p_reader.start()
    
    # Start Workers
    workers = []
    for _ in range(num_workers):
        # Ne trebaju nam initargs jer koristimo globalni VALID_PARENT_IDS
        p = multiprocessing.Process(target=worker_process, args=(input_queue, output_queue))
        p.start()
        workers.append(p)
        
    # 3. Aggregation Loop (Main Process)
    print("🔗 [Main] Čekam rezultate i spajam...")
    
    workers_finished = 0
    total_matched = 0
    
    # Progress bar za spajanje
    pbar = tqdm(desc="Spajanje komentara", unit="batch")
    
    while workers_finished < num_workers:
        result_batch = output_queue.get()
        
        if result_batch is None:
            workers_finished += 1
            continue
            
        for comment in result_batch:
            pid = comment["parent_id"]
            # Znamo da pid postoji jer je worker proverio VALID_PARENT_IDS
            if pid in submissions_map:
                submissions_map[pid]["comments"].append(comment)
                total_matched += 1
            
        pbar.update(1)
            
    pbar.close()
    p_reader.join()
    for p in workers:
        p.join()
        
    print(f"✅ Spajanje gotovo! Ukupno povezano: {total_matched:,} komentara.")

    # 4. Snimanje (Chunked)
    print(f"💾 Snimam rezultate u: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    part = 1
    count = 0
    
    f = open(get_chunk_filename(OUTPUT_DIR, part), 'wb')
    
    total_saved = 0
    
    for sub_data in tqdm(submissions_map.values(), desc="Exporting"):
        
        # Sortiranje komentara po score-u
        if sub_data["comments"]:
            sub_data["comments"].sort(key=lambda x: x["score"], reverse=True)
            if len(sub_data["comments"]) > MAX_COMMENTS_PER_POST:
                sub_data["comments"] = sub_data["comments"][:MAX_COMMENTS_PER_POST]
        
        f.write(orjson.dumps(sub_data))
        f.write(b"\n")
        
        count += 1
        total_saved += 1
        
        if count >= DOCUMENTS_PER_FILE:
            f.close()
            part += 1
            count = 0
            f = open(get_chunk_filename(OUTPUT_DIR, part), 'wb')
            
    f.close()
    print(f"✨ SVE ZAVRŠENO! {total_saved} dokumenata.")

if __name__ == "__main__":
    # Forsiramo 'fork' jer je najbrži na Linuxu i deli memoriju
    try:
        multiprocessing.set_start_method('fork', force=True)
    except RuntimeError:
        pass # Već setovano
    
    main()