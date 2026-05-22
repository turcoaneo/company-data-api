#!/usr/bin/env bash

# ============================================
# Meili Bootstrap Script (Bash)
# ============================================

MEILI_URL="http://localhost:7700"
INDEX_MAIN="companies"
INDEX_TOP="companies_top"

echo "🛑 Removing old Meili container (if exists)..."
docker rm -f ms >/dev/null 2>&1

echo "🚀 Starting Meilisearch..."
docker run -d --name ms -p 7700:7700 -e MEILI_NO_ANALYTICS=true getmeili/meilisearch:v1.7 >/dev/null

# --------------------------------------------
# Wait until Meili is ready
# --------------------------------------------
echo "⏳ Waiting for Meilisearch to become ready..."
for i in {1..60}; do
    if curl -s "$MEILI_URL/health" | grep -q '"status":"available"'; then
        echo "✅ Meilisearch is ready - iteration $i."
        break
    fi
    sleep 0.5
done

# --------------------------------------------
# Create index helper
# --------------------------------------------
create_index() {
    local index="$1"

    echo "📁 Creating index '$index'..."
    curl -s -X POST "$MEILI_URL/indexes" \
        -H "Content-Type: application/json" \
        --data "{\"uid\":\"$index\",\"primaryKey\":\"id\"}" >/dev/null

    echo "⚙️ Configuring index '$index'..."

    curl -s -X PATCH "$MEILI_URL/indexes/$index/settings/searchable-attributes" \
        -H "Content-Type: application/json" \
        --data '["company_commercial_name","company_legal_name","company_all_available_names","domain","phones","socials"]' >/dev/null

    curl -s -X PATCH "$MEILI_URL/indexes/$index/settings/filterable-attributes" \
        -H "Content-Type: application/json" \
        --data '["domain","phones","socials","phones_count","socials_count"]' >/dev/null

    curl -s -X PATCH "$MEILI_URL/indexes/$index/settings/sortable-attributes" \
        -H "Content-Type: application/json" \
        --data '["phones_count","socials_count"]' >/dev/null

    curl -s -X PATCH "$MEILI_URL/indexes/$index/settings/ranking-rules" \
        -H "Content-Type: application/json" \
        --data '["words","typo","proximity","attribute","exactness","sort"]' >/dev/null

    echo "✅ Index '$index' configured."
}

# --------------------------------------------
# Create + configure both indexes
# --------------------------------------------
create_index "$INDEX_MAIN"
create_index "$INDEX_TOP"

echo "🎉 Meili bootstrap complete!"
