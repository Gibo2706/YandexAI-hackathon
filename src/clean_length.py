import orjson
import os
import glob
import multiprocessing
from tqdm import tqdm

# --- KONFIGURACIJA ---
# Ulaz: Ono što je izašlo iz refine koraka
INPUT_PATTERN = "./dataset/output/refined/refined_docs_part_*.jsonl"
# Izlaz: Finalni folder spreman za embedding
OUTPUT_DIR = "./dataset/output/final_clean"
DOCUMENTS_PER_FILE = 100000

# --- LOGIKA TOKENA ---
# OpenAI embeding modeli (npr text-embedding-3-large) imaju limit od 8191 tokena.
# Aproksimacija: 1 token ~= 4 karaktera.
# Sigurnosna granica: 7000 tokena * 4 = 28000 karaktera.
MAX_CHAR_LIMIT = 28000 

def get_chunk_filename(output_dir, part_number):
    return os.path.join(output_dir, f"clean_docs_part_{part_number:03d}.jsonl")

def process_line(line):
    """
    Proverava ukupnu dužinu teksta u JSON objektu.
    Vraća originalnu liniju (bytes) ako je OK, ili None ako je predugačko.
    """
    try:
        doc = orjson.loads(line)
        
        # 1. Računamo dužinu posta
        post = doc.get("post", {})
        total_len = len(post.get("title", "") or "") + len(post.get("text", "") or "")
        
        # Brzi prekid: Ako je sam post već predugačak, nema šta da gledamo komentare
        if total_len > MAX_CHAR_LIMIT:
            return None

        # 2. Dodajemo dužinu svih komentara
        comments = doc.get("comments", [])
        for c in comments:
            total_len += len(c.get("text", "") or "")
            
            # Optimizacija: Proveravamo limit u petlji da ne sabiramo džabe ako smo već prešli
            if total_len > MAX_CHAR_LIMIT:
                return None
        
        # Ako smo ovde, dokument je u granicama
        return line 

    except Exception:
        return None

def main():
    files = sorted(glob.glob(INPUT_PATTERN))
    if not files:
        print(f"❌ Nema fajlova na putanji: {INPUT_PATTERN}")
        return

    print(f"🚀 Počinjem proveru dužine (Limit: {MAX_CHAR_LIMIT} karaktera / ~8000 tokena)...")
    print(f"📂 Output folder: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    num_workers = multiprocessing.cpu_count()
    print(f"⚙️  Koristim {num_workers} jezgara.")

    current_part = 1
    current_count = 0
    
    # Otvaramo prvi output fajl u binary modu (wb)
    f_out = open(get_chunk_filename(OUTPUT_DIR, current_part), 'wb')
    
    stats = {
        "kept": 0,
        "dropped": 0
    }

    with multiprocessing.Pool(processes=num_workers) as pool:
        for file_path in files:
            print(f"📄 Skeniram: {os.path.basename(file_path)}")
            
            with open(file_path, 'rb') as f_in:
                # Koristimo imap_unordered za brzinu, chunksize veći jer je operacija lagana
                for result in pool.imap_unordered(process_line, f_in, chunksize=4000):
                    
                    if result:
                        f_out.write(result)
                        # Originalna linija već ima \n na kraju obično, ali za svaki slučaj:
                        if not result.endswith(b'\n'):
                            f_out.write(b'\n')
                        
                        stats["kept"] += 1
                        current_count += 1
                        
                        # Rotacija
                        if current_count >= DOCUMENTS_PER_FILE:
                            f_out.close()
                            current_part += 1
                            current_count = 0
                            f_out = open(get_chunk_filename(OUTPUT_DIR, current_part), 'wb')
                    else:
                        stats["dropped"] += 1

    f_out.close()
    
    print("-" * 40)
    print(f"✅ ZAVRŠENO!")
    print(f"   - Sačuvano: {stats['kept']}")
    print(f"   - Odbačeno (Predugačko): {stats['dropped']}")
    print("-" * 40)

if __name__ == "__main__":
    main()