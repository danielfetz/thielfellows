import json
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

fellows = []
with open('data/fellows-embedded.json', 'r') as embeddings_file:
    fellows = json.load(embeddings_file)
    fellows.sort(key=lambda f: f['year'], reverse=True)

all_fellow_years = list(set(f['year'] for f in fellows))
all_fellow_years.sort(reverse=True)

all_names_and_desc = [[f['name'], f['company'] or f['one_liner'] or f['long_description'] or ''] for f in fellows]

def all_years():
    return all_fellow_years

def all_names_desc():
    return all_names_and_desc

def similarity(x, y):
    return cosine(x, y)

def search(query):
    fellows_with_embeddings = [f for f in fellows if f.get('description_embedding')]
    if not fellows_with_embeddings:
        # No embeddings yet — return all fellows
        results = [f.copy() for f in fellows]
        for f in results:
            f.pop('description_embedding', None)
        return results

    query_embedding = model.encode(query)
    by_similarity = fellows_with_embeddings[:]
    by_similarity.sort(key=lambda f: similarity(f['description_embedding'], query_embedding))

    results = [f.copy() for f in by_similarity]
    for f in results:
        f.pop('description_embedding', None)
    return results

def all():
    results = [f.copy() for f in fellows]
    for f in results:
        f.pop('description_embedding', None)
    return results
