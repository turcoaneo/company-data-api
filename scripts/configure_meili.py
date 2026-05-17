# scripts/configure_meili.py

import meilisearch

client = meilisearch.Client("http://localhost:7700")

# 1. Create index with primary key
index_name = "companies"
try:
    client.create_index(index_name, {"primaryKey": "id"})
except Exception as e:
    print(f"Index already exists {index_name}: {e}")

index = client.index(index_name)

# 2. Searchable fields
index.update_searchable_attributes([
    "company_commercial_name",
    "company_legal_name",
    "company_all_available_names",
    "domain",
    "phones",
    "socials"
])

# 3. Filterable fields (optional but recommended)
index.update_filterable_attributes([
    "domain",
    "phones",
    "socials"
])

# 4. Ranking rules
index.update_ranking_rules([
    "typo",
    "words",
    "proximity",
    "attribute",
    "exact",
    "desc(phones)",   # optional boost
    "desc(socials)"   # optional boost
])

print("Meili index configured successfully")
