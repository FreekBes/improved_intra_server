from flask import session
from .... import app


@app.route('/v2/options/<section>/save', methods=['POST'])
def options_section_save(section:str):
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'Unauthorized' }, 401
	return { 'type': 'error', 'message': 'Not Implemented' }, 501
