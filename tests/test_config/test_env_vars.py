import os
import importlib
import pytest
from pathlib import Path


class TestEnvVars:

    @pytest.fixture
    def env_files(self, tmp_path, monkeypatch):
        """
        Creates temporary .env and .env.local files and patches CWD
        so env_vars.py loads them.
        """
        # Create .env
        (tmp_path / ".env").write_text(
            "LOG_LEVEL=warning\n"
            "SCRAPER_JOB_LOOPED=False\n"
            "SCRAPER_SLEEPING_TIME=99\n"
            "SCRAPER_INTERVAL_SECONDS=99\n"
        )

        # Create .env.local
        (tmp_path / ".env.local").write_text(
            "LOG_LEVEL=debug\n"
            "SCRAPER_JOB_LOOPED=True\n"
            "SCRAPER_SLEEPING_TIME=10\n"
            "SCRAPER_INTERVAL_SECONDS=5\n"
        )

        # Patch working directory so dotenv_values(".env") loads from tmp_path
        monkeypatch.chdir(tmp_path)

        return tmp_path

    # ---------------------------------------------------------
    # Test 1: .env.local overrides .env when APP_ENV=local
    # ---------------------------------------------------------
    def test_env_local_overrides_env(self, env_files, monkeypatch):
        # Set APP_ENV=local
        monkeypatch.setenv("APP_ENV", "local")

        # Reload module to re-evaluate dotenv loading
        import app.utils.env_vars as env_vars
        importlib.reload(env_vars)

        assert env_vars.APP_ENV == "local"
        assert env_vars.LOG_LEVEL == "debug"  # from .env.local
        assert env_vars.SCRAPER_CONFIG["looped"] is True
        assert env_vars.SCRAPER_CONFIG["sleep_time"] == 10
        assert env_vars.SCRAPER_CONFIG["interval"] == 5

    # ---------------------------------------------------------
    # Test 2: .env.test overrides .env when APP_ENV=test
    # ---------------------------------------------------------
    def test_env_test_overrides_env(self, env_files, monkeypatch):
        # Create .env.test
        (env_files / ".env.test").write_text(
            "LOG_LEVEL=info\n"
            "SCRAPER_JOB_LOOPED=True\n"
        )

        monkeypatch.setenv("APP_ENV", "test")

        import app.utils.env_vars as env_vars
        importlib.reload(env_vars)

        assert env_vars.APP_ENV == "test"
        assert env_vars.LOG_LEVEL == "info"  # from .env.test
        assert env_vars.SCRAPER_CONFIG["looped"] is True

    # ---------------------------------------------------------
    # Test 3: OS environment overrides everything
    # ---------------------------------------------------------
    def test_os_env_overrides_all(self, env_files, monkeypatch):
        monkeypatch.setenv("APP_ENV", "local")
        monkeypatch.setenv("LOG_LEVEL", "error")  # OS override

        import app.utils.env_vars as env_vars
        importlib.reload(env_vars)

        assert env_vars.LOG_LEVEL == "error"  # OS wins

    # ---------------------------------------------------------
    # Test 4: default APP_ENV=test when not set
    # ---------------------------------------------------------
    def test_default_app_env(self, env_files, monkeypatch):
        monkeypatch.delenv("APP_ENV", raising=False)

        import app.utils.env_vars as env_vars
        importlib.reload(env_vars)

        assert env_vars.APP_ENV == "test"
