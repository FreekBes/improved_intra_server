"""Legacy routes.

Everything the v3 extension used is gone. What remains are redirects for the
two paths that later releases still request, kept until no installs ask for
them any more.
"""

from flask import redirect, request, url_for
from src import app


@app.route('/outstandings.php', methods=['GET'])
def old_outstandings():
	# Extension releases up to 4.4.x request this path with ?username=
	username = request.args.get('username')
	if not username:
		return { 'type': 'error', 'message': 'GET key \'username\' is not set, but is required' }, 400
	return redirect(url_for('outstandings', login=username), 301)


@app.route('/imagery.php', methods=['GET'])
def old_imagery():
	return redirect(url_for('banners'), 301)
