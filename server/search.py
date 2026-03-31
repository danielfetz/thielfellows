import json
import os

_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fellows = []
with open(os.path.join(_dir, 'data/fellows-embedded.json'), 'r') as f:
    fellows = json.load(f)
    fellows.sort(key=lambda f: f['year'], reverse=True)

all_fellow_years = sorted(set(f['year'] for f in fellows), reverse=True)
all_names_and_desc = [[f['name'], f['company'] or f['one_liner'] or f['long_description'] or ''] for f in fellows]

# Try to load sentence-transformers for semantic search; fall back to simple search
model = None
try:
    from scipy.spatial.distance import cosine
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
except ImportError:
    pass

def all_years():
    return all_fellow_years

def all_names_desc():
    return all_names_and_desc

def search(query):
    fellows_with_embeddings = [f for f in fellows if f.get('description_embedding')]

    if model and fellows_with_embeddings:
        query_embedding = model.encode(query)
        by_similarity = fellows_with_embeddings[:]
        by_similarity.sort(key=lambda f: cosine(f['description_embedding'], query_embedding))
        results = [f.copy() for f in by_similarity]
        for f in results:
            f.pop('description_embedding', None)
        return results

    # Fallback: simple text matching on name and company
    query_lower = query.lower().strip()
    if not query_lower:
        return all()

    def score(f):
        s = 0
        name = (f.get('name') or '').lower()
        company = (f.get('company') or '').lower()
        hometown = (f.get('hometown') or '').lower()
        desc = (f.get('long_description') or '').lower()
        one = (f.get('one_liner') or '').lower()
        for word in query_lower.split():
            if word in name:
                s += 3
            if word in company:
                s += 2
            if word in hometown:
                s += 1
            if word in desc or word in one:
                s += 1
        return -s  # negative for ascending sort

    results = sorted(fellows, key=score)
    results = [f.copy() for f in results]
    for f in results:
        f.pop('description_embedding', None)
    return results

def all():
    results = [f.copy() for f in fellows]
    for f in results:
        f.pop('description_embedding', None)
    return results
