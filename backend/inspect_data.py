import pickle
import json

# Load metadata to see structure
with open('data/index/metadata.pkl', 'rb') as f:
    metadata = pickle.load(f)

# Print first document structure
if metadata:
    print("Total documents:", len(metadata))
    print("\n" + "="*80)
    print("FIRST DOCUMENT STRUCTURE:")
    print("="*80)
    print(json.dumps(metadata[0], indent=2, default=str))
    
    # Check full_doc structure
    if 'full_doc' in metadata[0]:
        full_doc = metadata[0]['full_doc']
        print("\n" + "="*80)
        print("FULL_DOC FIELDS:")
        print("="*80)
        print("Keys:", list(full_doc.keys()))
        
        if 'post' in full_doc:
            print("\nPOST fields:", list(full_doc['post'].keys()))
            
        if 'comments' in full_doc:
            print(f"\nTotal comments: {len(full_doc['comments'])}")
            if full_doc['comments']:
                print("First comment fields:", list(full_doc['comments'][0].keys()))
                print("\nFirst 3 comments:")
                for i, c in enumerate(full_doc['comments'][:3], 1):
                    print(f"\n  Comment {i}:")
                    print(f"    author: {c.get('author')}")
                    print(f"    score: {c.get('score')}")
                    print(f"    parent_id: {c.get('parent_id')}")
                    print(f"    text: {c.get('text', '')[:100]}...")
