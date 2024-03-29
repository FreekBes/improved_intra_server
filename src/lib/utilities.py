from src import app

# Context processor for Jinja2 templates
@app.context_processor
def utility_processor():
	def git_to_url(git:str):
		if not git or not '@' in git:
			return ''
		git_split = git.split('@')
		if git_split[0] == 'github.com':
			return 'https://github.com/' + git_split[1]
		elif git_split[0] == 'gitlab.com':
			return 'https://gitlab.com/' + git_split[1]
		elif git_split[0] == 'bitbucket.org':
			return 'https://bitbucket.org/' + git_split[1]
		elif git_split[0] == 'codeberg.org':
			return 'https://codeberg.org/' + git_split[1]
		elif git_split[0] == 'sr.ht':
			return 'https://sr.ht/' + git_split[1]
		else:
			return ''

	return dict(git_to_url=git_to_url)
