import json
import os
import glob
from tqdm import tqdm
from config import (
    MAX_COMMENTS_PER_POST, 
    MIN_COMMENT_POSITIVE_SCORE,
    TARGET_KEYWORDS # Obavezno da ovo postoji u config.py
)

# KONFIGURACIJA IZLAZA
OUTPUT_DIR = "./dataset/output/documents"
DOCUMENTS_PER_FILE = 100000 

# CRNA LISTA SUBREDDITA 
BLACKLIST_SUBREDDITS = {
    "skincareaddiction", "makeupaddiction", "beauty", "movies", "gaming", 
    "books", "anime", "kpop", "fashion", "cats", "dogs", "food", "music"
}

def get_file_list(pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"⚠️  Nema fajlova za patern: {pattern}")
    return files

def get_chunk_filename(output_dir, part_number):
    return os.path.join(output_dir, f"final_docs_part_{part_number:03d}.jsonl")

def has_valid_keywords_ignore_review(text):
    """
    Vraća True ako tekst sadrži BITNE ključne reči.
    Ako sadrži SAMO 'review' (a nema scam, fraud, fake...), vraća False.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    found_keywords = [k for k in TARGET_KEYWORDS if k in text_lower]
    
    if not found_keywords:
        return False # Nema nikakvih ključnih reči (ovo je možda već filtrirano, ali provera ne škodi)
    
    # Ako je jedina pronađena reč "review", to je šum (verovatno recenzija filma/kreme)
    # Ako ima ["review", "scam"], onda prolazi. Ako ima ["review"], otpada.
    if len(found_keywords) == 1 and "review" in found_keywords:
        return False
        
    return True

def load_submissions(file_pattern):
    submissions = {}
    files = get_file_list(file_pattern)
    
    print(f"📥 Učitavam postove iz {len(files)} fajlova...")
    
    stats = {
        "total_read": 0,
        "dropped_blacklist": 0,
        "dropped_review_only": 0,
        "kept": 0
    }
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stats["total_read"] += 1
                try:
                    data = json.loads(line)
                    
                    # 1. FILTER SUBREDDITA
                    # if data.get("subreddit", "").lower() in BLACKLIST_SUBREDDITS:
                    #     stats["dropped_blacklist"] += 1
                    #     continue
                    
                    # 2. FILTER "REVIEW ONLY"
                    # Spajamo naslov i tekst za proveru keywords-a
                    full_text_check = (data.get("title", "") + " " + data.get("text", "")).strip()
                    
                    if not has_valid_keywords_ignore_review(full_text_check):
                        stats["dropped_review_only"] += 1
                        continue
                        
                    # Ako je prošao filtere, pravimo strukturu
                    # IZBACILI SMO created_utc jer ga nema u inputu
                    clean_sub = {
                        "post": {
                            "id": data["id"],
                            "title": data.get("title", ""),
                            "text": data.get("text", ""), 
                            "subreddit": data.get("subreddit"),
                            "score": data.get("score", 0),
                            "num_comments": data.get("num_comments", 0)
                        },
                        "comments": [] # Inicijalno prazna lista
                    }
                    submissions[data["id"]] = clean_sub
                    stats["kept"] += 1
                    
                except json.JSONDecodeError:
                    continue
    
    print(f"📊 STATUS POSTOVA:")
    print(f"   - Ukupno pročitano: {stats['total_read']}")
    print(f"   - Odbijeno (Blacklist): {stats['dropped_blacklist']}")
    print(f"   - Odbijeno (Samo 'Review'): {stats['dropped_review_only']}")
    print(f"   - SAČUVANO U RAM: {stats['kept']}")
    
    return submissions

def process_comments(submissions, file_pattern):
    files = get_file_list(file_pattern)
    print(f"🔗 Povezujem komentare iz {len(files)} fajlova...")
    
    stats = {
        "total_read": 0,
        "matched": 0,
        "orphaned": 0 # Komentari koji nemaju tatu
    }
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc=os.path.basename(file_path), leave=False):
                stats["total_read"] += 1
                try:
                    c_data = json.loads(line)
                    
                    # --- FIX ZA T3_ PREFIX ---
                    link_id = c_data.get("link_id", "")
                    
                    # Reddit ID-evi u 'link_id' su obično "t3_xxxxx". 
                    # ID posta u submissions mapi je samo "xxxxx".
                    if link_id.startswith("t3_"):
                        parent_id = link_id[3:] 
                    else:
                        parent_id = link_id
                        
                    # --- LOGIKA SPAJANJA ---
                    # Da li imamo tatu u memoriji?
                    if parent_id in submissions:
                        score = c_data.get("score", 0)
                        
                        # Filter kvaliteta komentara (skor)
                        if score < MIN_COMMENT_POSITIVE_SCORE:
                            continue

                        # Dodajemo komentar u listu 'comments' unutar objekta posta
                        submissions[parent_id]["comments"].append({
                            "id": c_data.get("id"),
                            "text": c_data.get("text", ""),
                            "score": score,
                            "subreddit": c_data.get("subreddit")
                        })
                        stats["matched"] += 1
                    else:
                        # Nema oca -> siroče -> bacamo
                        stats["orphaned"] += 1
                        
                except json.JSONDecodeError:
                    continue

    print(f"📊 STATUS KOMENTARA:")
    print(f"   - Ukupno pročitano: {stats['total_read']}")
    print(f"   - USPEŠNO POVEZANO: {stats['matched']}")
    print(f"   - Bačeno (Nema Posta/Orphaned): {stats['orphaned']}")
    
    if stats["matched"] == 0 and stats["total_read"] > 0:
        print("⚠️  UPOZORENJE: 0 povezanih komentara! Proveri da li ID-evi u submissions fajlu imaju 't3_' (ne bi trebalo) ili da li je filtering previše strog.")

def finalize_and_save_chunked(submissions, output_dir):
    print(f"💾 Generišem JSON strukturu u folder: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    current_part = 1
    current_count = 0
    
    current_file_path = get_chunk_filename(output_dir, current_part)
    f = open(current_file_path, 'w', encoding='utf-8')
    
    total_saved = 0
    
    # Iteriramo kroz sve postove
    # Postovi koji nemaju komentare SU I DALJE OVDE (sa praznom listom) i biće sačuvani.
    for sub_data in tqdm(submissions.values(), desc="Saving JSONs"):
        
        # 1. Sortiraj komentare (Top N po score-u)
        if sub_data["comments"]:
            sub_data["comments"].sort(key=lambda x: x["score"], reverse=True)
            # Sečemo na max broj komentara
            sub_data["comments"] = sub_data["comments"][:MAX_COMMENTS_PER_POST]
        
        # 2. Upis (format je već onakav kakav si tražio: {post:..., comments:[...]})
        f.write(json.dumps(sub_data) + "\n")
        
        current_count += 1
        total_saved += 1
        
        # Rotacija fajlova
        if current_count >= DOCUMENTS_PER_FILE:
            f.close()
            print(f"✅ Završen {os.path.basename(current_file_path)}")
            
            current_part += 1
            current_count = 0
            current_file_path = get_chunk_filename(output_dir, current_part)
            f = open(current_file_path, 'w', encoding='utf-8')

    f.close()
    print(f"✨ GOTOVO! Ukupno {total_saved} dokumenata sačuvano.")

if __name__ == "__main__":
    BASE_DIR = "./dataset" 
    
    # Prilagodi ovo ako su fajlovi u drugom folderu (npr ./dataset/processed)
    subs_pattern = os.path.join(BASE_DIR, "filtered_submissions_part_*.jsonl")
    comms_pattern = os.path.join(BASE_DIR, "filtered_comments_part_*.jsonl")
    
    # 1. Učitaj Postove
    submissions_map = load_submissions(subs_pattern)
    
    if not submissions_map:
        print("❌ Nema postova. Prekidam.")
        exit()
        
    # 2. Poveži Komentare
    process_comments(submissions_map, comms_pattern)
    
    # 3. Snimi Finalni Format
    finalize_and_save_chunked(submissions_map, OUTPUT_DIR)