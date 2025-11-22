import json
import numpy as np
import os
import pickle
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-large"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_documents(path):
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
                docs.append(obj)
            except json.JSONDecodeError as e:
                print(f"  Greška u liniji {line_num}: {e}")
                continue
    
    print(f" Učitano {len(docs)} dokumenata iz {path}")
    return docs


def prepare_text(doc, max_chars=30000):

    parts = []
    post = doc.get("post", {})
    comments = doc.get("comments", [])
    
    if "title" in post:
        parts.append(f"Title: {post['title']}")

    if "text" in post and post["text"].strip():
        parts.append(f"Post: {post['text']}")

    if comments:
        comments_texts = []
        for i, comment in enumerate(comments, start=1):
            comment_text = comment.get("text", "").strip()
            if comment_text:
                comments_texts.append(f"Comment {i}: {comment_text}")
        
        if comments_texts:
            parts.append("Comments:\n" + "\n".join(comments_texts))
    
    full_text = "\n\n".join(parts)
    
    if len(full_text) > max_chars:
        return None
    
    return full_text


def get_embeddings_batch_incremental(texts, docs, output_dir, global_index_start, batch_size=100):

    output_path = Path(output_dir)
    embeddings_npy = output_path / "embeddings.npy"
    metadata_pkl = output_path / "metadata.pkl"
    

    if embeddings_npy.exists():
        existing_embeddings = list(np.load(embeddings_npy))
    else:
        existing_embeddings = []
    
    if metadata_pkl.exists():
        with open(metadata_pkl, "rb") as f:
            existing_metadata = pickle.load(f)
    else:
        existing_metadata = []
    
    total_processed = 0
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_docs = docs[i:i + batch_size]
        
        print(f"   Batch {i//batch_size + 1}: embedujem {len(batch_texts)} tekstova...")
        
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch_texts
            )
            
            if len(response.data) != len(batch_texts):
                print(f"     OpenAI vratio {len(response.data)}/{len(batch_texts)} - preskačem ovaj batch")
                continue
            
            batch_embeddings = [item.embedding for item in response.data]
            
            # ODMAH dodaj embeddings
            existing_embeddings.extend(batch_embeddings)
            
            # ODMAH dodaj metadata
            for j, (doc, text) in enumerate(zip(batch_docs, batch_texts)):
                post = doc.get("post", {})
                idx = global_index_start + total_processed + j
                
                meta = {
                    "idx": idx,
                    "submission_id": post.get("id"),
                    "subreddit": post.get("subreddit"),
                    "title": post.get("title"),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "text_preview": text[:300] + "..." if len(text) > 300 else text,
                    "full_doc": doc
                }
                existing_metadata.append(meta)
            
            total_processed += len(batch_texts)
            
            # CHECKPOINT: piši nakon svakog batch-a
            np.save(embeddings_npy, np.array(existing_embeddings, dtype=np.float32))
            with open(metadata_pkl, "wb") as f:
                pickle.dump(existing_metadata, f)
            
            print(f"    Batch sačuvan (ukupno: {len(existing_metadata)} dokumenata)")
            
        except Exception as e:
            print(f"    Greška u batch-u {i//batch_size + 1}: {e}")
            print(f"    Preskačem ovaj batch, nastavljam dalje...")
            continue
    
    return total_processed


def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def save_metadata(metadata_list, output_path):
    with open(output_path, "wb") as f:
        pickle.dump(metadata_list, f)
    
    print(f" Metadata sačuvan u {output_path} ({len(metadata_list)} dokumenata)")


def load_metadata(metadata_path):
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return metadata


def build_embeddings(input_paths, output_dir, limit=None, batch_size=100, checkpoint_every=100):

    print(" Kreiranje embeddinga...")
    print("="*60 + "\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
 
    embeddings_npy = output_path / "embeddings.npy"
    faiss_index_path = output_path / "embeddings.index"
    metadata_pkl = output_path / "metadata.pkl"
    
    if metadata_pkl.exists():
        with open(metadata_pkl, "rb") as f:
            existing_metadata = pickle.load(f)
        resume_from_index = len(existing_metadata)
        print(f" Pronađen postojeći progres: {resume_from_index} dokumenata")
        print(f" Nastavljam odakle sam stao...\n")
    else:
        resume_from_index = 0
    
    global_index = resume_from_index
   
    all_metadata = []
    
    if isinstance(input_paths, str):
        if "*" in input_paths:
            input_paths = sorted(Path().glob(input_paths))
        else:
            input_paths = [input_paths]
    
    last_checkpoint = 0
    
    for file_path in input_paths:
        print(f"\n Procesiranje: {file_path}")
        docs = load_documents(file_path)

        if resume_from_index > 0:
            skip_count = min(resume_from_index, len(docs))
            if skip_count > 0:
                print(f"  ⏩ Preskačem prvih {skip_count} dokumenata (već obrađeni)")
                docs = docs[skip_count:]
                resume_from_index -= skip_count
        
        if len(docs) == 0:
            print(f"   Svi dokumenti iz ovog fajla su već obrađeni")
            continue
        
        if limit and global_index >= limit:
            print(f"  Dostignut limit od {limit} dokumenata")
            break
        
        if limit:
            remaining = limit - global_index
            docs = docs[:remaining]
        
        print(f" Pripremam tekstove...")
        texts = []
        valid_docs = []
        skipped = 0
        
        for doc in docs:
            text = prepare_text(doc)
            if text is None:
                skipped += 1
                continue
            texts.append(text)
            valid_docs.append(doc)
        
        if skipped > 0:
            print(f"   Preskočeno {skipped} dokumenata (preko 30k chars / 8k tokena)")
        
        if len(texts) == 0:
            print(f"   Nema validnih dokumenata u ovom fajlu, preskačem...")
            continue
        
        print(f" Embedujem {len(texts)} dokumenata u batch-evima od {batch_size}...")
        
        num_processed = get_embeddings_batch_incremental(
            texts=texts,
            docs=valid_docs,
            output_dir=output_dir,
            global_index_start=global_index,
            batch_size=batch_size
        )
        
        global_index += num_processed
        print(f"  Fajl obrađen: {num_processed} dokumenata (ukupno: {global_index})")
    
    print(f"\n ZAVRŠENO! Ukupno obrađeno: {global_index} dokumenata")
    
    if not embeddings_npy.exists():
        print(f"  Nema embeddings-a!")
        return
    
    all_embeddings = np.load(embeddings_npy)
    
    if len(all_embeddings) == 0:
        print(f"  Nema embeddings-a za kreiranje indexa!")
        return
    
    print(f"\n Kreiram FAISS index...")
    try:
        import faiss
        
        embeddings_arr = all_embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings_arr)
        
        index = faiss.IndexFlatIP(embeddings_arr.shape[1]) 
        index.add(embeddings_arr)

        faiss.write_index(index, str(faiss_index_path))
        print(f" FAISS index sačuvan u {faiss_index_path}")
    except ImportError:
        print("  FAISS nije instaliran. Instaluj: pip install faiss-cpu")
        print("   Index se neće kreirati, ali numpy embeddings su sačuvani.")
    
    print("\n" + "="*60)
    print(f" GOTOVO!")
    print(f"   Embedovano: {global_index} dokumenata")
    print(f"   Dimenzija: {all_embeddings.shape}")
    print(f"\n Output fajlovi (PREBACIVI na drugi računar):")
    print(f"   - {embeddings_npy} (numpy embeddings - {all_embeddings.nbytes / 1024**2:.1f} MB)")
    print(f"   - {faiss_index_path} (FAISS index za brzu pretragu)")
    print(f"   - {metadata_pkl} (Pickle sa CELIM dokumentima)")
    print("="*60 + "\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print(" GREŠKA: OPENAI_API_KEY nije postavljen!")
        print("   Napravi .env fajl sa: OPENAI_API_KEY=tvoj-key")
        exit(1)
    
    
    build_embeddings(
        input_paths="data/documents_part*.jsonl", 
        output_dir="data/index",
        limit=None,
        batch_size=100
    )
