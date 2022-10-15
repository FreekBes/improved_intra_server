from flask import render_template, session, redirect, url_for
from src.models.models import Campus
from ...oauth import authstart
from ... import app


@app.route('/v2/options')
def options():
	if not 'uid' in session:
		return authstart()
	return redirect(url_for('options_section', section='improvements'))


@app.route('/v2/options/<section>')
def options_section(section):
	if not 'uid' in session:
		return authstart()
	if section == 'campus':
		return render_campus_settings()
	return render_template(f"v2/options/{section}.j2")


# Campus-specific settings
def render_campus_settings():
	campus:Campus = Campus.query.filter_by(intra_id=int(session['campus'])).first()
	if not campus:
		return 'Campus not found', 404
	if campus.intra_id == 14: # Codam, Amsterdam
		return render_template('v2/options/codam.j2')
	return render_template('v2/options/no_campus_settings.j2', campus=campus.name)
