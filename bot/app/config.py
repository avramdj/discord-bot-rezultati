from dotenv import load_dotenv
import os

load_dotenv()

assert "DISCORD_TOKEN" in os.environ
assert "DB_URI" in os.environ
assert "DB_NAME" in os.environ
assert "LOG_CHANNEL_ID" in os.environ

token = os.environ["DISCORD_TOKEN"]
db_uri = os.environ["DB_URI"]
db_name = os.environ["DB_NAME"]
log_channel_id = int(os.environ["LOG_CHANNEL_ID"])
sleep_duration = 5 * 60  # seconds
prune_period = 30 * 60  # seconds
page_size_max = 1000000  # bytes
watch_check_timer = float(sleep_duration * 2)
