from requests.exceptions import RequestException
from database import Database, Message
from json import load as load_json
from typing import TypedDict, cast
from requests import Session
from pathlib import Path
from time import sleep
import utils

# ── Config ────────────────────────────────────────────────────────────────── #

GROUP_ID = 35815907
STOP_AT_MESSAGE_ID = 6374685646

MAX_RETRIES = 6
NEWEST_FIRST = True
SECONDS_BETWEEN_CALLS = 3

# ── Variables ─────────────────────────────────────────────────────────────── #

SESSION = Session()
ARCHIVE = Database()
CREDENTIAL_MANAGER = utils.CredentialManager()
SORT_ORDER = "Desc" if NEWEST_FIRST else "Asc"
print(SORT_ORDER)

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

def import_json_archive(path: str) -> None:
	print(f'Importing from "{path}"')
	file = Path(path)

	with file.open("r", encoding="utf-8") as f:
		data = load_json(f)

	group_id = data["groupId"]
	messages = [
		parse_message(post, group_id) 
		for post in data["posts"]
	]

	ARCHIVE.add_messages(messages)

def get_json_with_cookie(url: str) -> None:
	for attempt in range(1, MAX_RETRIES + 1):
		try:
			response = SESSION.get( url, 
				cookies = {".ROBLOSECURITY": CREDENTIAL_MANAGER.rotate_cookie()},
                timeout = 30 )
			if response.status_code == 429:
				print( utils.y("⚠ Rate limited, sleeping 10s") )
				sleep(10)
				continue
			response.raise_for_status()
			return response.json()
		except RequestException as err:
			print(f"[retry {attempt}/{MAX_RETRIES}] {err}")
			if attempt == MAX_RETRIES: raise
			sleep(2 ** attempt)

def get_group_messages(group_id: int) -> None:
	total_messages = 0
	cursor: str|None = ""
	found_message_id = False

	print(f"Starting archive for group: {group_id}")
	
	while not found_message_id:
		url = f"https://groups.roblox.com/v2/groups/{group_id}/wall/posts?limit=100&sortOrder={SORT_ORDER}&cursor={cursor}"

		try:
			data = cast(WallResponse, get_json_with_cookie(url))
		except Exception as err:
			print(f"[get_group_messages] Unexpected Error: {err}")
			print("\t", url)
			break
		
		messages: list[Message] = []
		for raw_message in data.get("data", []):
			message = parse_message(raw_message, group_id)
			messages.append(message)
			if message.id == STOP_AT_MESSAGE_ID:
				found_message_id = True
				print( utils.g("FOUND TARGET MESSAGE ID") )
		ARCHIVE.add_messages(messages)

		total_messages += len(data["data"])
		first_message_date = messages[1].created[:10] if messages[1] else "XXXX-XX-XX"
		print(f"{first_message_date}\t{total_messages}")
		sleep(SECONDS_BETWEEN_CALLS)

		cursor = data.get("nextPageCursor", None)
		if not cursor:
			print( utils.g("Archive Complete") )
			break

def main() -> None:
	print("🟢", utils.g("Connection Established"))

	try:
		get_group_messages(GROUP_ID)
	except Exception as err:
		print(err)

# ── Initialize ────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
	print("🔨 Initializing")
	try:
		main()
		# import_json_archive("archives\\group_1_wall_archive.json")
	except KeyboardInterrupt:
		print("⭕", utils.r("Disconnected"))
ARCHIVE.close()