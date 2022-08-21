from flask import session
import logging
from .. import app
from ..oauth import authstart

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG, format=app.config['LOG_FORMAT'])


@app.route('/connect.php', methods=['GET'])
def oldConnect():
	if not 'login' in session:
		return authstart(1)
	return 'Connected V1', 200
