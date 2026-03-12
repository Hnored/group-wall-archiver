from datetime import datetime, timedelta
from pathlib import Path

OFFSET = timedelta(hours = 5)

def iso_to_unix(iso: str) -> int:
	datetime_object = datetime.strptime(iso[:-1].split('.')[0], "%Y-%m-%dT%H:%M:%S") - OFFSET
	return int(datetime_object.timestamp())

class CredentialManager:
	def __init__(self, cookies_path: str = "cookies.txt", proxies_path: str = "proxies.txt"):
		cookies_file = Path(cookies_path)
		cookies_file.touch(exist_ok=True)
		self.cookies = self._load_lines(cookies_file)
		self.cookie_index = 0
		del cookies_file

		proxies_file = Path(proxies_path)
		proxies_file.touch(exist_ok=True)
		self.proxies = self._load_lines(proxies_file)
		self.proxy_index = 0
		del proxies_file

	def _load_lines(self, path: Path) -> list[str]:
		lines: list[str] = []
		with open(path) as file:
			for line in file:
				line = line.strip()
				if not line or line.startswith("#"):
					continue
				lines.append(line)
		return lines

	def rotate_cookie(self) -> str:
		if not self.cookies: raise RuntimeError("No cookies loaded.")

		cookie = self.cookies[self.cookie_index]
		self.cookie_index = (self.cookie_index + 1) % len(self.cookies)
		return cookie

	def rotate_proxy(self) -> str | None:
		if not self.proxies: return None

		proxy = self.proxies[self.proxy_index]
		self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
		return proxy

def r(text: str) -> str: # Red
	"""Display console text as red"""
	return "\033[31m" + text + "\033[0m"

def y(text: str) -> str: # Yellow
	"""Display console text as yellow"""
	return "\033[33m" + text + "\033[0m"

def g(text: str) -> str: # Green
	"""Display console text as green"""
	return "\033[32m" + text + "\033[0m"