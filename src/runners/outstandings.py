import logging

from src.models.models import User, Runner, Team, Evaluation
from sqlalchemy.sql import func
from src.lib.db import session
from datetime import datetime
from src.lib.intra import ic

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
BEGINNING_OF_TIME = 1262300400 # 2010-01-01


class OutstandingsRunner:
	def get_teams(self, user:User, since:str, now:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, now) }
		try:
			projects_users = ic.pages_threaded('users/{}/projects_users'.format(user.intra_id), params=payload)
		except Exception as e:
			logging.error('Error fetching outstandings for user {}'.format(user.login))
			logging.error(str(e))
			return
		logging.info('Fetched {} projects_users'.format(len(projects_users)))
		for projects_user in projects_users:
			try:
				# Create or update all teams
				for team in projects_user['teams']:
					db_team:Team = session.query(Team).filter_by(intra_id=team['id'], user_id=user.intra_id).first()
					if not db_team:
						db_team = Team(intra_id=team['id'], user_id=user.intra_id, projects_user_id=projects_user['id'])
					db_team.final_mark = int(team['final_mark']) if team['final_mark'] else 0
					db_team.current = False
					db_team.best = False
					session.merge(db_team)
					session.commit()

				# Set current team
				current_teams:list[Team] = session.query(Team).filter_by(intra_id=projects_user['current_team_id']).all()
				for current_team in current_teams:
					current_team.current = True

				# Set best team
				if not projects_user['teams'] or len(projects_user['teams']) == 0:
					logging.warning('No teams found for user {} in project {}'.format(user.login, projects_user['project']['name']))
					continue
				highest_mark = projects_user['teams'][0]['final_mark']
				highest_mark_id = projects_user['teams'][0]['id']
				for team in projects_user['teams']:
					if team['final_mark'] and team['final_mark'] > highest_mark:
						highest_mark = team['final_mark']
						highest_mark_id = team['id']
				best_teams:list[Team] = session.query(Team).filter_by(intra_id=highest_mark_id).all()
				for best_team in best_teams:
					best_team.best = True
				session.commit()
			except Exception as e:
				logging.error('Error creating team in DB: {}'.format(str(e)))
				session.rollback()
		session.flush()


	def get_evaluations(self, user:User, since:str, now:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, now), 'filter[future]': 'false', 'filter[filled]': 'true' }
		try:
			evaluations = ic.pages_threaded('users/{}/scale_teams/as_corrected'.format(user.intra_id), params=payload)
		except Exception as e:
			logging.error('Error fetching evaluations for user {}'.format(user.login))
			logging.error(str(e))
			return
		logging.info('Fetched {} evaluations'.format(len(evaluations)))
		for eval in evaluations:
			# Create or update all evaluations
			try:
				db_eval:Evaluation = session.query(Evaluation).filter_by(intra_id=eval['id']).first()
				if not db_eval:
					db_eval = Evaluation(intra_id=eval['id'], intra_team_id=eval['team']['id'], evaluator_id=eval['corrector']['id'], evaluated_at=eval['begin_at'])
				db_eval.mark = int(eval['final_mark']) if eval['final_mark'] else 0
				db_eval.outstanding = (eval['flag']['id'] == 9)
				db_eval.success = eval['flag']['positive']
				session.merge(db_eval)
				session.commit()
			except Exception as e:
				logging.error('Error creating evaluation in DB: {}'.format(str(e)))
				session.rollback()
		session.flush()


	def fetch_for_user(self, user:User, fetch_all:bool = False):
		db_runner:Runner = session.query(Runner).filter_by(user_id = user.intra_id).one()
		last_fetch_time = BEGINNING_OF_TIME
		if db_runner.outstandings and not fetch_all:
			last_fetch_time = int(db_runner.outstandings.timestamp())
		last_fetch_str = datetime.utcfromtimestamp(last_fetch_time).strftime(DATE_FORMAT)
		fetch_start = datetime.utcnow()
		fetch_start_str = fetch_start.strftime(DATE_FORMAT)
		logging.info('Fetching changes in projects_users since {}'.format(last_fetch_str))
		self.get_teams(user, last_fetch_str, fetch_start_str)
		self.get_evaluations(user, last_fetch_str, fetch_start_str)
		if not fetch_all:
			db_runner:Runner = session.query(Runner).filter_by(user_id=user.intra_id).one()
			db_runner.outstandings = fetch_start
		session.commit()
		session.flush()


	def run(self):
		users:list[User] = session.query(User.intra_id, User.login).all()

		i = 1
		amount_users = len(users)
		for user in users:
			logging.info('Fetching outstandings for {} ({}) --- {} of {} users...'.format(user.login, str(user.intra_id), str(i), amount_users))
			self.fetch_for_user(user)
			i += 1


	def run_for_user(self, login:str):
		user:User = session.query(User).filter_by(login=login).one_or_none()
		if not user:
			logging.error('User with login {} not found'.format(login))
			return

		logging.info('Fetching outstandings for user {}'.format(user.login))
		self.fetch_for_user(user, fetch_all=True)


outstandingsRunner = OutstandingsRunner()
