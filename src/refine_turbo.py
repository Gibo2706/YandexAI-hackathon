import orjson
import os
import glob
import multiprocessing
from collections import defaultdict
from config import (
    TARGET_KEYWORDS,
    # MIN_COMMENT_POSITIVE_SCORE 
)

# --- KONFIGURACIJA ---
INPUT_PATTERN = "./dataset/output/documents/final_docs_part_*.jsonl"
OUTPUT_DIR = "./dataset/output/refined"
DOCUMENTS_PER_FILE = 100000

# --- LIMITI (ROMANI STOP) ---
# 8192 tokena * 4 karaktera = ~32k karaktera. 
# Stavicemo malo manje da budemo sigurni.
MAX_CHAR_LIMIT = 30000 

# --- OPTIMIZACIJA KEYWORDS ---
TARGET_KEYWORDS_BYTES = [k.encode('utf-8') for k in TARGET_KEYWORDS]

def get_chunk_filename(output_dir, part_number):
    return os.path.join(output_dir, f"refined_docs_part_{part_number:03d}.jsonl")

def is_review_spam(title, text):
    """Vraća True ako je post verovatno spam/šum (ima samo 'review' bez 'scam')."""
    content = (title + " " + text).lower().encode('utf-8')
    found = [k for k in TARGET_KEYWORDS_BYTES if k in content]
    
    if not found: return True 
    if len(found) == 1 and found[0] == b"review": return True
        
    return False

def process_document(line):
    """
    Worker funkcija: Filtrira romane, pravi stablo, bira top komentare.
    """
    try:
        doc = orjson.loads(line)
        post = doc["post"]
        
        # 1. FILTER: DUŽINA POSTA (ROMANI) [NOVO]
        # Spajamo title i text da vidimo ukupnu dužinu
        post_title = post.get("title", "") or ""
        post_text = post.get("text", "") or ""
        
        if (len(post_title) + len(post_text)) > MAX_CHAR_LIMIT:
            return None # Predugačak post, verovatno smeće -> BACAMO DOKUMENT

        # 2. FILTER: Review Spam
        if is_review_spam(post_title, post_text):
            return None

        raw_comments = doc.get("comments", [])
        
        # Ako nema komentara, vraćamo samo post (ako je prošao filtere)
        if not raw_comments:
            return orjson.dumps(doc)

        # 3. IZGRADNJA STABLA (uz filtriranje predugačkih komentara)
        children_map = defaultdict(list)
        post_id = post["id"]
        
        valid_comments_count = 0
        
        for c in raw_comments:
            # 1. FILTER KOMENTARA: DUŽINA [NOVO]
            c_text = c.get("text", "") or ""
            if len(c_text) > MAX_CHAR_LIMIT:
                continue # Preskačemo ovaj komentar, predugačak je
                
            pid = c.get("parent_id")
            if not pid: continue
            
            children_map[pid].append(c)
            valid_comments_count += 1

        # Ako su svi komentari bili romani i otpali, vraćamo post bez komentara
        if valid_comments_count == 0:
            doc["comments"] = []
            return orjson.dumps(doc)

        # 4. SORTIRANJE DECE (Sortiramo svaku listu dece po Score-u descending)
        for pid in children_map:
            children_map[pid].sort(key=lambda x: x.get("score", 0), reverse=True)

        # 5. SELEKCIJA (Top 7 Root + Deep Dive)
        final_comments = []
        
        # Uzimamo direktne odgovore na post (Root comments)
        root_comments = children_map.get(post_id, [])
        
        # Uzimamo TOP 7 root komentara (najbitnija diskusija)
        top_roots = root_comments[:7]
        
        for root in top_roots:
            final_comments.append(root)
            
            # --- NIVO 1 (Deca od Root-a) ---
            level1_children = children_map.get(root['id'], [])
            
            for l1 in level1_children:
                final_comments.append(l1)
                
                # --- NIVO 2 (Deca od Nivoa 1) --- MAX DUBINA
                level2_children = children_map.get(l1['id'], [])
                for l2 in level2_children:
                    final_comments.append(l2)
                    # Ovde stajemo (Depth 2 reached)

        # Ažuriramo dokument
        doc["comments"] = final_comments
        
        return orjson.dumps(doc)

    except Exception:
        return None

def main():
    # Pronađi ulazne fajlove
    files = sorted(glob.glob(INPUT_PATTERN))
    if not files:
        print(f"❌ Nema fajlova na putanji: {INPUT_PATTERN}")
        return

    print(f"🚀 Počinjem rafiniranje {len(files)} fajlova (Filter romana: >{MAX_CHAR_LIMIT} char)...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Konfiguracija Pool-a
    num_workers = multiprocessing.cpu_count()
    print(f"⚙️  Koristim {num_workers} jezgara.")

    current_part = 1
    current_count = 0
    f_out = open(get_chunk_filename(OUTPUT_DIR, current_part), 'wb')
    
    total_saved = 0
    total_processed = 0

    with multiprocessing.Pool(processes=num_workers) as pool:
        
        for file_path in files:
            print(f"📄 Obrađujem: {os.path.basename(file_path)}")
            
            with open(file_path, 'rb') as f_in:
                # Chunksize povecan za bolji throughput
                for result in pool.imap_unordered(process_document, f_in, chunksize=2000):
                    total_processed += 1
                    
                    if result:
                        f_out.write(result)
                        f_out.write(b'\n')
                        
                        total_saved += 1
                        current_count += 1
                        
                        if current_count >= DOCUMENTS_PER_FILE:
                            f_out.close()
                            print(f"✅ Završen {os.path.basename(f_out.name)}")
                            
                            current_part += 1
                            current_count = 0
                            f_out = open(get_chunk_filename(OUTPUT_DIR, current_part), 'wb')

            print(f"   -> Trenutno sačuvano: {total_saved}")

    f_out.close()
    print(f"✨ ZAVRŠENO! Ukupno {total_saved} čistih dokumenata.")

if __name__ == "__main__":
    main()