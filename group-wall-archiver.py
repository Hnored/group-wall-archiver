from database import Database
from pprint import pprint
from requests import get
import utils

# ── Config ────────────────────────────────────────────────────────────────── #

GROUP_ID = 4084597
API_VERSION = 2 # 1|2
MESSAGES_PER_CALL = 10 # 10|25|50|100

# ── Variables ─────────────────────────────────────────────────────────────── #

ARCHIVE = Database()
WALL_API = f"https://groups.roblox.com/v{API_VERSION}/groups/{GROUP_ID}/wall/posts?limit={MESSAGES_PER_CALL}&sortOrder=Asc"

# ── Main Method ───────────────────────────────────────────────────────────── #

def main():
	print("🟢", utils.g("Connection Established"))

	response = get(WALL_API)
	pprint(response.json())

# ── Initialize ────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
	print("🔨 Initializing")
	try: main()
	except KeyboardInterrupt:
		print("⭕", utils.r("Disconnected"))
ARCHIVE.close()