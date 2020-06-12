import os


TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_TOKEN_SECRET = os.environ.get("TWITTER_TOKEN_SECRET", "")

RABBIT_USERNAME = os.environ.get("RABBIT_USERNAME", "admin")
RABBIT_PASSWORD = os.environ.get("RABBIT_PASSWORD", "123123")
RABBIT_URL = os.environ.get("RABBIT_URL", "localhost")
RABBIT_CONNECTION = None

MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME", "dbuser")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "dbpassword")
MONGODB_URL = os.environ.get("MONGODB_URL", "localhost:27017")
MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "tw_analyzer")
MOTOR_CONNECTION = None

SEED_KEYWORDS = os.environ.get("SEEDS", "apple,microsoft").split(",")