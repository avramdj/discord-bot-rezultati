from dotenv import load_dotenv
import os

load_dotenv()

assert "DISCORD_TOKEN" in os.environ
assert "DB_URI" in os.environ
assert "DB_NAME" in os.environ
assert "LOG_CHANNEL_ID" in os.environ
assert "SLEEP_DURATION_MIN" in os.environ
assert "PRUNE_PERIOD_MIN" in os.environ
assert "MAX_PAGE_SIZE" in os.environ

token = os.environ["DISCORD_TOKEN"]
db_uri = os.environ["DB_URI"]
db_name = os.environ["DB_NAME"]
log_channel_id = int(os.environ["LOG_CHANNEL_ID"])
sleep_duration = float(os.environ["SLEEP_DURATION_MIN"]) * 60  # seconds
prune_period = float(os.environ["PRUNE_PERIOD_MIN"]) * 60  # seconds
page_size_max = int(os.environ["MAX_PAGE_SIZE"])  # bytes
watch_check_timer = float(sleep_duration * 2)
