from datetime import datetime, timedelta

OFFSET = timedelta(hours = 5)

def iso_to_unix(iso: str) -> int:
	datetime_object = datetime.strptime(iso[:-1].split('.')[0], "%Y-%m-%dT%H:%M:%S") - OFFSET
	return int(datetime_object.timestamp())

def r(text: str) -> str: # Red
	"""Display console text as red"""
	return "\033[31m" + text + "\033[0m"

def y(text: str) -> str: # Yellow
	"""Display console text as yellow"""
	return "\033[33m" + text + "\033[0m"

def g(text: str) -> str: # Green
	"""Display console text as green"""
	return "\033[32m" + text + "\033[0m"