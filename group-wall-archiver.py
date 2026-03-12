from database import Database, Message
from typing import TypedDict
from requests import get
from time import sleep
import utils

# ── Config ────────────────────────────────────────────────────────────────── #

GROUP_ID = 1
API_VERSION = 2 # 1|2
WAIT_TIME_BETWEEN_CALLS = 5 # Seconds
MESSAGES_PER_CALL = 100 # 10|25|50|100

# ── Variables ─────────────────────────────────────────────────────────────── #

ARCHIVE = Database()
CREDENTIAL_MANAGER = utils.CredentialManager()
WALL_API = f"https://groups.roblox.com/v{API_VERSION}/groups/{GROUP_ID}/wall/posts?limit={MESSAGES_PER_CALL}&sortOrder=Asc"

# ── Parsing ───────────────────────────────────────────────────────────────── #

class User(TypedDict):
    userId: int
    username: str
    displayName: str
    hasVerifiedBadge: bool
class Role(TypedDict):
    id: int
    name: str
    rank: int
class Poster(TypedDict):
    user: User
    role: Role
class RawMessage(TypedDict):
	id: int
	poster: Poster|None
	body: str
	created: str
	updated: str
class WallResponse(TypedDict):
	previousPageCursor: str|None
	nextPageCursor: str|None
	data: list[RawMessage]

def parse_message(data: RawMessage, group_id: int) -> Message:
	poster = data.get("poster")

	if poster:
		user = poster.get("user", {})
		has_verified_badge = user.get("hasVerifiedBadge")
		user_id = user.get("userId")
		username = user.get("username")
		display_name = user.get("displayName")
		
		role = poster.get("role", {})
		role_id = role.get("id")
		role_name = role.get("name")
		role_rank = role.get("rank")
	else:
		has_verified_badge = None
		user_id = None
		username = None
		display_name = None
		
		role_id = None
		role_rank = None
		role_name = None
	
	return Message(
		id = data["id"],
		group_id = group_id,

		user_id            = user_id,
		username           = username,
		display_name       = display_name,
		has_verified_badge = has_verified_badge,

		role_id   = role_id,
		role_rank = role_rank,
		role_name = role_name,

		body = data["body"],
		created = data["created"],
		updated = data["updated"],
	)

# ── Main Method ───────────────────────────────────────────────────────────── #

def get_group_messages(group_id: int):
	total_messages = 0
	cursor = ""
	
	while True:
		try:
			url = f"https://groups.roblox.com/v{API_VERSION}/groups/{group_id}/wall/posts?limit={MESSAGES_PER_CALL}&sortOrder=Asc&cursor={cursor}"

			response = get(url, cookies = {".ROBLOSECURITY": CREDENTIAL_MANAGER.rotate_cookie()})
			if not response.ok:
				print(f"[get_group_messages] Failed ({response.status_code}) for group {group_id}")
				print(response.json())
				break

			data = response.json()
			if not data or "data" not in data: break

			for message in data.get("data", []):
				message = parse_message(message, group_id)
				ARCHIVE.add_message(message)
			
			total_messages += len(data["data"])
			print(f"{total_messages} entries.")
			sleep( WAIT_TIME_BETWEEN_CALLS )

			cursor = data.get("nextPageCursor", None)
			if not cursor: break
		except Exception as err:
			print(f"[get_group_messages] Unexpected Error: {err}")
			break

def main():
	print("🟢", utils.g("Connection Established"))

	try:
		get_group_messages(GROUP_ID)
	except Exception as err:
		print(err)

# ── Initialize ────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
	print("🔨 Initializing")
	try: main()
	except KeyboardInterrupt:
		print("⭕", utils.r("Disconnected"))
ARCHIVE.close()