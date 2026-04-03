import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
MAX_TOPICS_PER_DAY = int(os.getenv("MAX_TOPICS_PER_DAY", "20"))
MIN_TOPIC_SCORE = int(os.getenv("MIN_TOPIC_SCORE", "70"))
MAX_SEARCH_RESULTS_PER_QUERY = int(os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", "10"))

DATA_DIR = "data"
TOPIC_QUEUE_FILE = os.path.join(DATA_DIR, "topic_queue.json")
USED_TOPICS_FILE = os.path.join(DATA_DIR, "used_topics.json")
RESEARCH_LOG_FILE = os.path.join(DATA_DIR, "research_log.json")
LAST_RUN_FILE = os.path.join(DATA_DIR, "last_run.json")
