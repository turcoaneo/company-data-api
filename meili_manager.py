# meili_manager.py

import subprocess
import time

import meilisearch
import requests

MEILI_URL = "http://localhost:7700"
INDEX_NAME = "companies"


class MeiliManager:
    def __init__(self, url: str = MEILI_URL, index_name: str = INDEX_NAME):
        self.url = url
        self.index_name = index_name
        self.client = None
        self.index = None

    # ---------------------------------------------------------
    # 1) HEALTH CHECK
    # ---------------------------------------------------------
    def is_running(self) -> bool:
        try:
            r = requests.get(f"{self.url}/health", timeout=0.5)
            return r.status_code == 200
        except Exception as e:
            print(f"Cannot access {self.url} health endpoint: {e}")
            return False

    # ---------------------------------------------------------
    # 2) AUTO-START MEILI VIA DOCKER
    # ---------------------------------------------------------
    @staticmethod
    def start_meili():
        print("Starting Meilisearch via Docker...")
        subprocess.Popen([
            "docker", "run", "--rm",
            "-p", "7700:7700",
            "-e", "MEILI_NO_ANALYTICS=true",
            "getmeili/meilisearch:v1.7"
        ])
        print("Meilisearch container started.")

    # ---------------------------------------------------------
    # 3) WAIT UNTIL MEILI IS READY
    # ---------------------------------------------------------
    def wait_until_ready(self, timeout: int = 20):
        print("Waiting for Meilisearch to become ready...")
        start = time.time()
        while time.time() - start < timeout:
            if self.is_running():
                print("Meilisearch is ready.")
                return True
            time.sleep(0.5)
        raise RuntimeError("Meilisearch did not become ready in time.")

    # ---------------------------------------------------------
    # 4) CONNECT CLIENT + INDEX
    # ---------------------------------------------------------
    def connect(self):
        self.client = meilisearch.Client(self.url)
        self.index = self.client.index(self.index_name)

    # ---------------------------------------------------------
    # 5) CREATE + CONFIGURE INDEX
    # ---------------------------------------------------------
    def create_and_configure_index(self):
        print("Creating/configuring Meili index...")

        # 1) Create index if missing
        try:
            self.client.create_index(self.index_name, {"primaryKey": "id"})
            print("Index created.")
        except Exception as e:
            print(f"Index {self.index_name} already exists: {e}")

        # Always refresh index handle
        self.index = self.client.index(self.index_name)

        # 2) Searchable fields
        self.index.update_searchable_attributes([
            "company_commercial_name",
            "company_legal_name",
            "company_all_available_names",
            "domain",
            "phones",
            "socials",
        ])

        # 3) Filterable fields
        self.index.update_filterable_attributes([
            "domain",
            "phones",
            "socials",
            "phones_count",
            "socials_count",
        ])

        # 4) Sortable fields (for per-query sort, not ranking rules)
        self.index.update_sortable_attributes([
            "phones_count",
            "socials_count",
        ])

        # 5) Base ranking rules ONLY (no desc(...) here)
        self.index.update_ranking_rules([
            "words",
            "typo",
            "proximity",
            "attribute",
            "exactness",
            "sort",
        ])

        print("Index configured successfully.")

    # ---------------------------------------------------------
    # 6) INGEST DOCUMENTS (NDJSON)
    # ---------------------------------------------------------

    def ingest_ndjson(self, file_path: str):
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{self.url}/indexes/{self.index_name}/documents",
                params={"primaryKey": "id"},
                data=f,
                headers={"Content-Type": "application/x-ndjson"}
            )

        print("Status:", resp.status_code)
        print("Response:", resp.text)

    # ---------------------------------------------------------
    # 7) FULL BOOTSTRAP (start + configure)
    # ---------------------------------------------------------
    def bootstrap(self):
        if not self.is_running():
            self.start_meili()
        self.wait_until_ready()
        self.connect()
        self.create_and_configure_index()
        print("Meili bootstrap complete.")
