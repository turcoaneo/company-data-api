# scripts/start_meili.py

import subprocess

subprocess.Popen([
    "docker", "run", "--rm",
    "-p", "7700:7700",
    "-e", "MEILI_NO_ANALYTICS=true",
    "getmeili/meilisearch:v1.7"
])
