from ...oauth import authstart
from flask import session
from ... import app


@app.route('/v2/options')
def options():
	if not 'uid' in session:
		return authstart(2)
	return 'Coming soon', 200
