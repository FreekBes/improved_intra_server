import logging

from src.models.models import User, Profile, Settings, BannerImg, Team, Evaluation, Event, UserToken, OAuth2Token, Runner
from src.lib.db import session
from src.lib.banners import banner_exists, delete_banner
from datetime import datetime
from src import app
from time import sleep


class AnonymizationRunner:
	def anonymize_user(self, user:User):
		try:
			# Delete runners for this user
			runners:list[Runner] = session.query(Runner).filter_by(user_id=user.intra_id).all()
			for runner in runners:
				session.delete(runner)
				logging.info('Deleted runner for user {} from DB due to anonymization'.format(user.intra_id))

			# Delete all user's settings from database
			settings = session.query(Settings).filter_by(user_id=user.intra_id).all()
			for setting in settings:
				session.delete(setting)
				logging.info('Deleted settings for user {} from DB due to anonymization'.format(user.intra_id))

			# Delete all user's profile information from database
			profiles = session.query(Profile).filter_by(user_id=user.intra_id).all()
			for profile in profiles:
				session.delete(profile)
				logging.info('Deleted profile for user {} from DB due to anonymization'.format(user.intra_id))

			# Delete all user's banners from database and disk
			banners = session.query(BannerImg).filter_by(user_id=user.intra_id).all()
			for banner in banners:
				# Delete file from disk
				if banner.url.startswith(app.config['IINTRA_URL']):
					# Get banner file name from url
					banner_file = banner.url.split('/')[-1]
					if banner_exists(banner_file): # If banner exists locally on disk, delete it
						if not delete_banner(banner_file):
							raise Exception('Could not delete banner file: {}'.format(banner_file))

				# Delete banner from database
				session.delete(banner)
				logging.info('Deleted banner of user {} from DB due to anonymization'.format(user.intra_id))

			# Delete user's teams from database
			teams:list[Team] = session.query(Team).filter_by(user_id=user.intra_id).all()
			for team in teams:
				session.delete(team)
				logging.info('Deleted team {} of user {} from DB due to anonymization'.format(team.intra_id, user.intra_id))

				# Check if the team appears twice, if so, another Improved Intra user has the same team.
				# In that case, we should not delete the evaluations, as they are still relevant for the other user.
				# NOTE: Teams in the Improved Intra DB are tied to users instead of Intra teams (they could appear twice)
				if session.query(Team).filter_by(intra_id=team.intra_id).count() > 1:
					logging.info('Team {} of user {} appears more than once in the DB, skipping evaluation deletion due to anonymization'.format(team.intra_id, user.intra_id))
					continue
				evaluations = session.query(Evaluation).filter_by(intra_team_id=team.intra_id).all()
				for evaluation in evaluations:
					session.delete(evaluation)
					logging.info('Deleted evaluation {} of team {} from DB due to anonymization of user {}'.format(evaluation.intra_id, team.intra_id, user.intra_id))

			# Delete user's events from database
			events = session.query(Event).filter_by(user_id=user.intra_id).all()
			for event in events:
				session.delete(event)
				logging.info('Deleted event {} of user {} from DB due to anonymization'.format(event.intra_id, user.intra_id))

			# Delete user's tokens from database
			user_tokens = session.query(UserToken).filter_by(user_id=user.intra_id).all()
			for token in user_tokens:
				session.delete(token)
				logging.info('Deleted user token of user {} from DB due to anonymization'.format(user.intra_id))

			# Delete user's OAuth2 tokens from database
			oauth_tokens = session.query(OAuth2Token).filter_by(user_id=user.intra_id).all()
			for token in oauth_tokens:
				session.delete(token)
				logging.info('Deleted OAuth2 token of user {} from DB due to anonymization'.format(user.intra_id))

			# Finally, delete the user from the database
			session.delete(user)
			logging.info('Deleted user {} from DB due to anonymization'.format(user.intra_id))
			session.commit()

		except Exception as e:
			logging.error('Error anonymizing user {}: {}'.format(user.intra_id, str(e)))
			session.rollback()

	def run(self):
		users:list[User] = session.query(User).all()

		for user in users:
			# Check if user is set to be anonymized and if the anonymization date has passed
			if not user.anonymize_date or user.anonymize_date > datetime.now().date():
				continue
			logging.info('Anonymizing user {} ({}), anonymization date passed ({})'.format(user.login, user.intra_id, user.anonymize_date))
			self.anonymize_user(user)

		session.flush()

	def run_for_user(self, login:str):
		user:User = session.query(User).filter_by(login=login).one_or_none()
		if not user:
			logging.error('User with login {} not found'.format(login))
			return

		# Check if user is set to be anonymized and if the anonymization date has passed
		if not user.anonymize_date or user.anonymize_date > datetime.now().date():
			print('User {} is not set to be anonymized or the anonymization date has not passed yet! Sleeping for 5 seconds to allow user to cancel...'.format(user.intra_id))
			sleep(5) # Sleep for a bit to allow user to cancel

		try:
			self.anonymize_user(user)
		except Exception as e:
			logging.error('Error anonymizing user {}: {}'.format(user.intra_id, str(e)))
			session.rollback()


anonymizationRunner = AnonymizationRunner()
