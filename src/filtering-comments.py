import zstandard as zstd
import json
import os
import string
from config import (
    TARGET_KEYWORDS, 
    MIN_TEXT_LENGTH, 
    MIN_POSITIVE_SCORE, 
    MAX_NEGATIVE_SCORE,
    SHORT_TEXT_WHITELIST
)

# Konstanta: Koliko sačuvanih redova ide u jedan fajl pre nego što ga "odsečemo"
# Stavili smo 100k kao što si tražio.
RECORDS_PER_FILE = 100000 

def contains_keywords(text):
    """Proverava da li tekst sadrži ključne reči."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in TARGET_KEYWORDS)

def is_valid_score(score):
    """Proverava skor (pozitivan ili jako negativan)."""
    if score >= MIN_POSITIVE_SCORE:
        return True
    if score <= MAX_NEGATIVE_SCORE:
        return True
    return False

def is_valid_length_content(text):
    """Proverava dužinu ili whitelist kratkih reči."""
    if not text:
        return False
    
    if len(text) >= MIN_TEXT_LENGTH:
        return True
        
    clean_text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = clean_text.split()
    
    if any(word in SHORT_TEXT_WHITELIST for word in words):
        return True
        
    return False

def get_chunk_filename(base_filename, part_number):
    """
    Pravi ime fajla: 'filtered_submissions.jsonl' -> 'filtered_submissions_part_001.jsonl'
    """
    name, ext = os.path.splitext(base_filename)
    return f"{name}_part_{part_number:03d}{ext}"

def stream_and_filter(input_file, output_base_name, item_type="submission"):
    """
    Čita .zst fajl i secka izlaz na više manjih fajlova (chunks).
    """
    
    print(f"🚀 Počinjem obradu: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Greška: Fajl {input_file} ne postoji.")
        return

    stats = {"total_read": 0, "total_kept": 0}
    
    # Promenljive za rotaciju fajlova
    current_part = 1
    current_file_kept_count = 0
    
    # Otvaramo prvi output fajl
    current_output_file = get_chunk_filename(output_base_name, current_part)
    out_f = open(current_output_file, 'w', encoding='utf-8')
    print(f"📂 Kreiram fajl: {current_output_file}")

    try:
        with open(input_file, 'rb') as fh:
            dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
            with dctx.stream_reader(fh) as reader:
                import io
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                
                for line in text_stream:
                    stats["total_read"] += 1
                    
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # --- LOGIKA ZA EKSTRAKCIJU PODATAKA ---
                    if item_type == "submission":
                        text_body = data.get("selftext", "")
                        title = data.get("title", "")
                        full_text = f"{title} {text_body}"
                        score = data.get("score", 0)
                    else: # comment
                        full_text = data.get("body", "")
                        score = data.get("score", 0)

                    # --- FILTERI ---
                    if not is_valid_score(score):
                        continue
                    
                    if not is_valid_length_content(full_text):
                        continue
                        
                    if not contains_keywords(full_text):
                        continue
                    
                    # --- PRIPREMA PODATAKA ---
                    minified_data = {
                        "id": data.get("id"),
                        "subreddit": data.get("subreddit"),
                        "score": score,
                        "text": full_text,
                        "type": item_type
                    }
                    
                    if item_type == "submission":
                        minified_data["num_comments"] = data.get("num_comments", 0)
                        minified_data["title"] = data.get("title", "") 
                    
                    if item_type == "comment":
                        minified_data["link_id"] = data.get("link_id")
                    
                    # --- UPIS I ROTACIJA FAJLOVA ---
                    out_f.write(json.dumps(minified_data) + "\n")
                    stats["total_kept"] += 1
                    current_file_kept_count += 1
                    
                    # Ako smo napunili trenutni fajl (npr. 100k zapisa)
                    if current_file_kept_count >= RECORDS_PER_FILE:
                        out_f.close() # Zatvori stari
                        print(f"✅ Završen {current_output_file} (100k zapisa).")
                        
                        # Otvori novi
                        current_part += 1
                        current_output_file = get_chunk_filename(output_base_name, current_part)
                        out_f = open(current_output_file, 'w', encoding='utf-8')
                        current_file_kept_count = 0 # Resetuj brojač za novi fajl
                        print(f"📂 Kreiram fajl: {current_output_file}")

                    # Log statusa (samo na konzoli)
                    if stats["total_read"] % 100000 == 0:
                        percentage = (stats["total_kept"] / stats["total_read"]) * 100
                        print(f"⏳ Pročitano {stats['total_read']} | Sačuvano ukupno: {stats['total_kept']} ({percentage:.2f}%)")

    finally:
        # Osiguravamo da se fajl zatvori na kraju, čak i ako pukne ili se završi
        if not out_f.closed:
            out_f.close()
            print(f"✅ Zatvoren poslednji fajl: {current_output_file}")

    print(f"🏁 KRAJ! Ukupno pročitano: {stats['total_read']}. Ukupno sačuvano: {stats['total_kept']}.")

if __name__ == "__main__":
    # PRILAGODI PUTANJE OVDE
    
    base_path = "./dataset" 
    
    # 1. Filtriranje SUBMISSIONS
    # submit_input = os.path.join(base_path, "RS_2022-09.zst") 
    # if os.path.exists(submit_input):
    #     stream_and_filter(
    #         submit_input, 
    #         "filtered_submissions.jsonl",  # Skripta će dodati _part_001, _part_002...
    #         item_type="submission"
    #     )
    
    # 2. Filtriranje COMMENTS
    comment_input = os.path.join(base_path, "RC_2022-09.zst")
    if os.path.exists(comment_input):
        stream_and_filter(
            comment_input, 
            "filtered_comments.jsonl",     # Skripta će dodati _part_001, _part_002...
            item_type="comment"
        )