from src.runners.anonymization import anonymizationRunner
from src.lib.auth.decorators import session_required_redirect
from wtforms.validators import DataRequired
from src.models.models import User
from src.lib.db import session as db_session
from flask import redirect, render_template, session, url_for
from wtforms import StringField
from flask_wtf import FlaskForm
from src import app


class DeleteAccountForm(FlaskForm):
	confirmation = StringField('Confirmation', validators=[DataRequired()])


@app.route('/v2/delete', methods=['POST'])
@session_required_redirect
def delete_account():
	form = DeleteAccountForm()
	if not form.validate_on_submit():
		return render_template('v2/options/deleted.j2', error='Could not verify the request. Please try again from the help page.'), 400

	# The browser asks the user to type their login; check it server side too,
	# so the confirmation cannot simply be skipped.
	if form.confirmation.data.strip().lower() != session['login'].lower():
		return render_template('v2/options/deleted.j2', error='The login you typed did not match your own. Nothing was deleted.'), 400

	user:User = db_session.query(User).filter_by(intra_id=session['uid']).one_or_none()
	if not user:
		session.clear()
		return render_template('v2/options/deleted.j2', error='No data was found for your account. There is nothing left to delete.'), 404

	if not anonymizationRunner.anonymize_user(user):
		return render_template('v2/options/deleted.j2', error='Something went wrong while deleting your data. Please try again later, or send an e-mail.'), 500

	session.clear()
	return render_template('v2/options/deleted.j2', error=None)
