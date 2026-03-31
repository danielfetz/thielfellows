import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

with open('data/fellows.json', 'r') as fellows_file:
    fellows = json.load(fellows_file)
    for i, f in enumerate(fellows):
        print(f'{i}/{len(fellows)}', f['name'])
        description = f.get('long_description') or f.get('one_liner')
        if not description:
            print(f'{f["name"]} has no description, skipping semantic indexing')
            continue
        embedding = model.encode(description.strip())
        f['description_embedding'] = embedding.tolist()

    with open('data/fellows-embedded.json', 'w') as embeddings_file:
        json.dump(fellows, embeddings_file)
