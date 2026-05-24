# meili_manager.py
import subprocess
import time
import meilisearch
import requests

from app.utils.env_vars import MEILI, APP_ENV

MEILI_URL = MEILI["url"]
INDEX_NAME = MEILI["index"]
TOP_RESULT_INDEX_NAME = MEILI["top_index"]

CONTAINER_NAME = "ms"


class MeiliManager:
    def __init__(self, url: str = MEILI_URL, index_name: str = INDEX_NAME, top_index_name: str = TOP_RESULT_INDEX_NAME):
        self.url = url
        self.index_name = index_name
        self.top_index_name = top_index_name
        self.client = None
        self.index = None
        self.top_index = None

    # ---------------------------------------------------------
    # 1) HEALTH CHECK
    # ---------------------------------------------------------
    def is_running(self) -> bool:
        try:
            r = requests.get(f"{self.url}/health", timeout=0.5)
            return r.status_code == 200
        except Exception as e:
            print(f"Could not access meili manager, maybe stopped / paused: {e}")
            return False

    # ---------------------------------------------------------
    # 2) DOCKER STATE HELPERS
    # ---------------------------------------------------------
    @staticmethod
    def _get_container_status() -> str | None:
        """
        Returns one of:
        - "running"
        - "paused"
        - "exited"
        - None (container does not exist)
        """
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )
        status = result.stdout.strip()

        if not status:
            return None  # container does not exist

        status_lower = status.lower()

        if "paused" in status_lower:
            return "paused"
        if "up" in status_lower:
            return "running"
        if "exited" in status_lower:
            return "exited"

        return None

    # ---------------------------------------------------------
    # 3) AUTO-START MEILI VIA DOCKER (RESPECT EXISTING CONTAINER)
    # ---------------------------------------------------------
    @staticmethod
    def start_meili():
        status = MeiliManager._get_container_status()

        if status == "running":
            print(f"✔ Meilisearch container '{CONTAINER_NAME}' is already running.")
            return

        if status == "paused":
            print(f"⏸ Meilisearch container '{CONTAINER_NAME}' is paused. Un-pausing...")
            subprocess.run(["docker", "unpause", CONTAINER_NAME])
            return

        if status == "exited":
            print(f"🔄 Starting existing stopped container '{CONTAINER_NAME}'...")
            subprocess.run(["docker", "start", CONTAINER_NAME])
            return

        print(f"🚀 Creating new Meilisearch container '{CONTAINER_NAME}'...")
        subprocess.Popen([
            "docker", "run", "-d",
            "--name", CONTAINER_NAME,
            "-p", "7700:7700",
            "-e", "MEILI_NO_ANALYTICS=true",
            "getmeili/meilisearch:v1.7"
        ])
        print("Meilisearch container started.")

    # ---------------------------------------------------------
    # 4) WAIT UNTIL MEILI IS READY
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
    # 5) CONNECT CLIENT + INDEX
    # ---------------------------------------------------------
    def connect_to_meili(self):
        self.client = meilisearch.Client(self.url)
        self.index = self.client.index(self.index_name)
        self.top_index = self.client.index(self.top_index_name)

    # ---------------------------------------------------------
    # 6) CREATE + CONFIGURE INDEX
    # ---------------------------------------------------------
    def create_and_configure_indexes(self):
        self._create_and_configure_index(self.index_name)
        self._create_and_configure_index(self.top_index_name)

    def _create_and_configure_index(self, index_name: str):
        print(f"Creating/configuring Meili index '{index_name}'...")

        try:
            self.client.create_index(index_name, {"primaryKey": "id"})
            print(f"Index '{index_name}' created.")
        except Exception as e:
            print(f"Index '{index_name}' already exists... {e}")

        index = self.client.index(index_name)

        index.update_searchable_attributes([
            "company_commercial_name",
            "company_legal_name",
            "company_all_available_names",
            "domain",
            "phones",
            "socials",
        ])

        index.update_filterable_attributes([
            "domain",
            "phones",
            "socials",
            "phones_count",
            "socials_count",
        ])

        index.update_sortable_attributes([
            "phones_count",
            "socials_count",
        ])

        index.update_ranking_rules([
            "words",
            "typo",
            "proximity",
            "attribute",
            "exactness",
            "sort",
        ])

        print(f"Index '{index_name}' configured successfully.")

    # ---------------------------------------------------------
    # 7) INGEST DOCUMENTS (NDJSON)
    # ---------------------------------------------------------
    def ingest_ndjson(self, file_path: str):
        from app.utils.meili_ingest_helper import ingest_ndjson
        return ingest_ndjson(self.url, self.index_name, file_path)

    # ---------------------------------------------------------
    # 8) FULL BOOTSTRAP
    # ---------------------------------------------------------
    def bootstrap(self):
        # Skip Docker logic in AWS
        if APP_ENV not in ("uat", "prod"):
            if not self.is_running():
                self.start_meili()
        else:
            print(f"APP_ENV={APP_ENV}: Skipping Docker startup logic.")

        self.wait_until_ready()
        self.connect_to_meili()
        self.create_and_configure_indexes()
        print("Meili bootstrap complete.")


if __name__ == "__main__":
    MeiliManager().bootstrap()
