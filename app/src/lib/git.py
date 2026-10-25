import re


def valid_github_username(username:str):
	_rex = re.compile('^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){0,38}$')
	return True if _rex.fullmatch(username.lower()) else False
