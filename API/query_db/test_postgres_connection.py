from API.query_db import get_pg_connection
from API.logging.send_telegram_alert import send_telegram_alert
import logging
import time

logger = logging.getLogger(__name__)

def test_postgres_connection(POSTGRES_DATA) -> bool:
    try:
        conn = get_pg_connection(*POSTGRES_DATA)
        conn.close()
        return True
    except Exception as e:
        send_telegram_alert(f"roi calculator api: Postgres DB connection failed")
        logger.exception(f"Postgres connection failed")
        time.sleep(120)
        return False