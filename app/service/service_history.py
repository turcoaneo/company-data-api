# app/service/service_history.py

from crawler.util.history_summary import load_history_summary


def get_history_summary():
    return load_history_summary()
