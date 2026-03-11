from dataclasses import dataclass
from pathlib import Path
import sqlite3

@dataclass
class Message:
	id: int
	group_id: int
	user_id: int
	display_name: str
	role_rank: int
	role_name: str
	message: str
	created: int

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
			group_id INTEGER,
			user_id INTEGER,
			display_name TEXT,
			role_rank INTEGER,
			role_name TEXT,
			message TEXT,
			created INTEGER
		)
		""")

		self.connection.execute("CREATE INDEX IF NOT EXISTS idx_group ON messages(group_id)")
		self.connection.execute("CREATE INDEX IF NOT EXISTS idx_user ON messages(user_id)")

		self.connection.commit()

	def add_message(self, message: Message):
		print(message.id)
		self.connection.execute("""
			INSERT INTO messages
			(message_id, group_id, user_id, display_name, role_rank, role_name, message, created)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?)
			""", (
				message.id,
				message.group_id,
				message.user_id,
				message.display_name,
				message.role_rank,
				message.role_name,
				message.message,
				message.created
			),
		)
		self.connection.commit()

	def close(self):
		self.connection.close()

if __name__ == "__main__":
	db = Database()
	print("Database initialized.")
	db.close()