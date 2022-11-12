from ..models.models import Campus, User, Settings, Profile, Runner, UserToken
from .. import app, db
from .intra import ic

def add_mod_user(user:dict):
	# Add campus(es) to DB
	primary_campus_id = None
	if 'campus' in user and 'campus_users' in user:
		for campus in user['campus']:
			if not Campus.query.filter_by(intra_id = campus['id']).first():
				resp = ic.get('campus/{}'.format(campus['id']))
				if resp.status_code != 200:
					return False
				full_campus = resp.json()
				db_campus = Campus(full_campus['id'], full_campus['name'], full_campus['city'], full_campus['country'])
				db.session.add(db_campus)
				db.session.flush()

		# Find primary campus
		for campus_user in user['campus_users']:
			if campus_user['is_primary']:
				primary_campus_id = campus_user['campus_id']
				break

	# Add or modify user in DB
	db_user = User(
		intra_id=user['id'],
		login=user['login'],
		campus_id=primary_campus_id,
		email=user['email'],
		first_name=user['first_name'],
		last_name=user['last_name'],
		display_name=user['displayname'],
		staff=user['staff?'] == True,
		anonymize_date=user['anonymize_date']
	)
	db.session.merge(db_user) # Add if not exist, update if exist
	db.session.flush()

	# Create user token for user if not exist
	if not UserToken.query.filter_by(user_id=db_user.id).first():
		db_token = UserToken(db_user.id)
		db.session.add(db_token)

	# Create settings for user if not exist
	if not Settings.query.filter_by(user_id = user['id']).first():
		db_settings = Settings(user['id'])
		db.session.add(db_settings)

	# Create profile for user if not exist
	if not Profile.query.filter_by(user_id = user['id']).first():
		db_profile = Profile(user['id'])
		db.session.add(db_profile)

	# Create runners for user if not exist
	if not Runner.query.filter_by(user_id = user['id']).first():
		db_runner = Runner(user['id'])
		db.session.add(db_runner)

	# Commit all DB changes
	db.session.commit()
	return True
