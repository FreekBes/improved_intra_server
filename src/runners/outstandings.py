import logging

from ..models.models import User, Runner, Team, Evaluation
from sqlalchemy.sql import func
from datetime import datetime
from ..lib.db import session
from ..lib.intra import ic

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'


class OutstandingsRunner:
	def __init__(self):
		self.now = datetime.utcnow()

	def get_teams(self, user:User, since:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, self.now.strftime(DATE_FORMAT)) }
		projects_users = ic.pages_threaded('users/{}/projects_users'.format(user.intra_id), params=payload)
		logging.info('Fetched {} projects_users'.format(len(projects_users)))
		try:
			for projects_user in projects_users:
				# Create or update all teams
				for team in projects_user['teams']:
					db_team = session.query(Team).filter_by(intra_id=team['id'], user_id=user.intra_id, projects_user_id=projects_user['id']).first()
					if not db_team:
						db_team = Team(intra_id=team['id'], user_id=user.intra_id, projects_user_id=projects_user['id'])
					db_team.final_mark = int(team['final_mark']) if team['final_mark'] else 0
					db_team.current = False
					db_team.best = False
					session.merge(db_team)

				# Set current team
				current_team:Team = session.query(Team).filter_by(intra_id=projects_user['current_team_id']).first()
				if current_team:
					current_team.current = True

				# Set best team
				highest_mark = projects_user['teams'][0]['final_mark']
				highest_mark_id = projects_user['teams'][0]['id']
				for team in projects_user['teams']:
					if team['final_mark'] and team['final_mark'] > highest_mark:
						highest_mark = team['final_mark']
						highest_mark_id = team['id']
				best_team:Team = session.query(Team).filter_by(intra_id=highest_mark_id).first()
				if best_team:
					best_team.best = True
			session.flush()
		except Exception as e:
			logging.error('Error creating team in DB: {}'.format(str(e)))
			session.rollback()
		session.commit()


	def fetch_for_user(self, user:User):
		db_runner:Runner = session.query(Runner).filter_by(user_id = user.intra_id).one()
		last_fetch_time = 1262300400 #2010-01-01
		if db_runner.outstandings:
			last_fetch_time = int(db_runner.outstandings.timestamp())
		last_fetch_dt = datetime.utcfromtimestamp(last_fetch_time)
		last_fetch_str = last_fetch_dt.strftime(DATE_FORMAT)
		logging.info('Fetching changes in projects_users since {}'.format(last_fetch_str))
		self.get_teams(user, last_fetch_str)


	def run(self):
		users:list[User] = session.query(User.intra_id, User.login).all()

		i = 1
		amount_users = len(users)
		for user in users:
			logging.info('Fetching outstandings for {} ({}) --- {} of {} users...'.format(user.login, str(user.intra_id), str(i), amount_users))
			self.now = datetime.utcnow()
			self.fetch_for_user(user)
			i += 1


outstandingsRunner = OutstandingsRunner()
