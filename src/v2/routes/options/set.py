from werkzeug.datastructures import CombinedMultiDict
from .forms.handlers import set_v2_settings
from flask import session, request
from .forms.forms import *
from .... import app


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
		(saved, message, updated_settings) = set_v2_settings(form, int(session['uid']))
		if saved:
			return { 'type': 'success', 'message': message, 'updated_settings': updated_settings }, 200
		else:
			return { 'type': 'error', 'message': 'Could not save settings due to a server error', 'details': message }, 500

	# Gather form errors if not validated
	form_errors = dict()
	for field_name, error_msgs in form.errors.items():
		form_errors[field_name] = list()
		for error_msg in error_msgs:
			form_errors[field_name].append(error_msg)
	return { 'type': 'error', 'message': 'Settings could not be saved due to invalid input', 'form_errors': form_errors }, 400
