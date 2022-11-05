from ....models.models import Campus
from werkzeug.datastructures import CombinedMultiDict
from flask import session, request
from .forms.forms import *
from .... import app, db


# Table distribution
# This dictionary specifies which user setting is saved in which table
# and how the POST body request value should be translated to a database value
TABLE_DISTRIBUTION = {
	'settings': {
		'theme': 'theme',
		'colors': 'colors',
		'show_custom_profiles': 'boolean',
		'hide_broadcasts': 'boolean',
		'logsum_month': 'boolean',
		'logsum_week': 'boolean',
		'outstandings': 'boolean',
		'hide_goals': 'boolean',
		'holygraph_more_cursuses': 'boolean',
		'old_blackhole': 'boolean',
		'clustermap': 'boolean',
		'codam_monit': 'boolean',
		'codam_auto_equip_coa_title': 'boolean',
	},
	'profiles': {
		'banner_img': 'banner_img',
		'banner_pos': 'banner_pos',
		'link_git': 'url_git',
		'link_web': 'url_all'
	}
}


def get_wtform(section:str):
	if section == 'improvements':
		return ImprovementsForm(CombinedMultiDict((request.files, request.form)))
	elif section == 'appearance':
		return AppearanceForm(CombinedMultiDict((request.files, request.form)))
	elif section == 'profile':
		return ProfileForm(CombinedMultiDict((request.files, request.form)))
	elif section == 'campus':
		user_campus_id = int(session['campus'])
		if user_campus_id == 14: # Codam, Amsterdam
			return CodamForm(CombinedMultiDict((request.files, request.form)))
	return None # The section given does not have any form associated with it


@app.route('/v2/options/<section>/save', methods=['POST'])
def options_section_save(section:str):
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'Unauthorized' }, 401

	# Get the correct form to use for this section
	form = get_wtform(section)

	# If no form was returned, return a response immediately
	if not form:
		if section == 'campus':
			return { 'type': 'error', 'message': 'There are no custom settings available for the logged in user\'s campus at this time' }, 400
		else:
			return { 'type': 'error', 'message': f"Section '{section}' is not a valid options section" }, 400

	# Validate and save form
	if form.validate():
		return { 'type': 'error', 'message': 'Not implemented' }, 501
		# if set_v1_settings(form):
		# 	return { 'type': 'success', 'message': 'Settings saved', 'data': get_v1_settings(form.username.data) }, 201
		# else:
		# 	return { 'type': 'error', 'message': 'Could not save settings', 'data': get_v1_settings(form.username.data) }, 500

	# Gather form errors if not validated
	form_errors = dict()
	for field_name, error_msgs in form.errors.items():
		form_errors[field_name] = list()
		for error_msg in error_msgs:
			form_errors[field_name].append(error_msg)
	return { 'type': 'error', 'message': 'Settings could not be saved due to invalid input', 'form_errors': form_errors }, 400
