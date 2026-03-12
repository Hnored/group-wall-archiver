from dataclasses import dataclass
from pathlib import Path
import sqlite3

@dataclass
class Message:
	id: int
	group_id: int

	user_id: int|None
	username: str|None
	display_name: str|None
	has_verified_badge: bool|None

	role_id: int|None
	role_rank: int|None
	role_name: str|None

	body: str
	created: str
	updated: str
# This is not optimized, for now we are just dumping everything raw

class Database:
	def __init__(self, path: str = "archive.db"):
		self.path = Path(path)
		self.connection = sqlite3.connect(self.path)
		self.connection.row_factory = sqlite3.Row
		self.connection.execute("PRAGMA journal_mode=WAL;")
		self._create_schema()
	
	def _create_schema(self):
		"""Create the table if it doesn't exist."""
		
		self.connection.execute("""
		CREATE TABLE IF NOT EXISTS messages (
			message_id INTEGER PRIMARY KEY,
			group_id INTEGER NOT NULL,
			
			user_id INTEGER,
			username TEXT,
			display_name TEXT,
			has_verified_badge BOOLEAN,	  

			role_id INTEGER,
			role_rank INTEGER,
			role_name TEXT,
				  
			body TEXT NOT NULL,
			created TEXT NOT NULL,
			updated TEXT NOT NULL
		)
		""")

		self.connection.execute("CREATE INDEX IF NOT EXISTS idx_group ON messages(group_id)")
		self.connection.execute("CREATE INDEX IF NOT EXISTS idx_user ON messages(user_id)")

		self.connection.commit()

	def add_message(self, message: Message):
		self.connection.execute("""
			INSERT OR IGNORE INTO messages
			(message_id, group_id, user_id, username, display_name, has_verified_badge, role_id, role_rank, role_name, body, created, updated)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			""", (
				message.id,
				message.group_id,

				message.user_id,
				message.username,
				message.display_name,
				message.has_verified_badge,

				message.role_id,
				message.role_rank,
				message.role_name,
				
				message.body,
				message.created,
				message.updated
			),
		)
		self.connection.commit()

	def close(self):
		self.connection.close()

if __name__ == "__main__":
	db = Database()
	print("Database initialized.")
	db.close()