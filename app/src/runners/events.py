import logging
import json

from src.models.models import Runner, Event, User, Campus
from src.lib.db import session
from datetime import datetime
from src.lib.intra import ic

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
BEGINNING_OF_TIME = 1262300400 # 2010-01-01


def create_or_update_event(event, user_intra_id:int):
	try:
		# Create or update event
		db_event:Event = session.query(Event).filter_by(intra_id=event['id'], user_id=user_intra_id, is_exam=False).first()
		if not db_event:
			db_event = Event(int(event['id']), user_intra_id, event['name'].encode().hex()[:1024], is_exam=False)
		db_event.description = event['description'].encode().hex()[:16384] if event['description'] else ""
		db_event.location = event['location'].encode().hex()[:1024] if event['location'] else ""
		db_event.kind = event['kind'] if event['kind'] else "event"
		db_event.max_people = int(event['max_people']) if event['max_people'] else 0
		db_event.nbr_subscribers = int(event['nbr_subscribers']) if event['nbr_subscribers'] else 0
		db_event.cursus_ids = json.dumps(event['cursus_ids']) if (event['cursus_ids'] and len(event['cursus_ids']) > 0) else "[]"
		db_event.campus_ids = json.dumps(event['campus_ids']) if (event['campus_ids'] and len(event['campus_ids']) > 0) else "[]"
		db_event.begin_at = datetime.strptime(event['begin_at'], DATE_FORMAT)
		db_event.end_at = datetime.strptime(event['end_at'], DATE_FORMAT)
		db_event.created_at = datetime.strptime(event['created_at'], DATE_FORMAT)
		db_event.updated_at = datetime.strptime(event['updated_at'], DATE_FORMAT)
		session.merge(db_event)
		session.commit()
	except Exception as e:
		logging.error('Error creating non-exam event in DB: {}'.format(str(e)))
		session.rollback()


def update_many_events(event):
	try:
		rows_updated = session.query(Event).filter_by(intra_id=event['id']).update({
			'name': event['name'].encode().hex()[:1024],
			'description': event['description'].encode().hex()[:16384] if event['description'] else "",
			'location': event['location'].encode().hex()[:1024] if event['location'] else "",
			'kind': event['kind'] if event['kind'] else "event",
			'max_people': int(event['max_people']) if event['max_people'] else 0,
			'nbr_subscribers': int(event['nbr_subscribers']) if event['nbr_subscribers'] else 0,
			'cursus_ids': json.dumps(event['cursus_ids']) if (event['cursus_ids'] and len(event['cursus_ids']) > 0) else "[]",
			'campus_ids': json.dumps(event['campus_ids']) if (event['campus_ids'] and len(event['campus_ids']) > 0) else "[]",
			'begin_at': datetime.strptime(event['begin_at'], DATE_FORMAT),
			'end_at': datetime.strptime(event['end_at'], DATE_FORMAT),
			'created_at': datetime.strptime(event['created_at'], DATE_FORMAT),
			'updated_at': datetime.strptime(event['updated_at'], DATE_FORMAT),
		})
		logging.info('Updated {} events with intra_id {}'.format(str(rows_updated), str(event['id'])))
		session.commit()
	except Exception as e:
		logging.error('Error updating event in DB: {}'.format(str(e)))
		session.rollback()


def create_or_update_exam(exam, user:User):
	try:
		# Create or update exam
		db_event:Event = session.query(Event).filter_by(intra_id=exam['id'], user_id=user.intra_id, is_exam=True).first()
		if not db_event:
			db_event = Event(int(exam['id']), user.intra_id, exam['name'].encode().hex()[:1024], is_exam=True)
		# List all projects in the event description
		if exam['projects'] and len(exam['projects']) > 0:
			exam_projects = []
			for project in exam['projects']:
				exam_projects.append(project['name'])
			db_event.description = "For exams: {}".format(", ".join(exam_projects)).encode().hex()[:16384]
		else:
			db_event.description = "" # This should never happen
		db_event.location = exam['location'].encode().hex()[:1024] if exam['location'] else ""
		db_event.kind = "exam"
		db_event.max_people = int(exam['max_people']) if exam['max_people'] else 0
		db_event.nbr_subscribers = int(exam['nbr_subscribers']) if exam['nbr_subscribers'] else 0
		cursus_ids = [cursus['id'] for cursus in exam['cursus']]
		db_event.cursus_ids = json.dumps(cursus_ids) if (cursus_ids and len(cursus_ids) > 0) else "[]"
		db_event.campus_ids = json.dumps([user.campus_id]) if user.campus_id else "[]"
		db_event.begin_at = datetime.strptime(exam['begin_at'], DATE_FORMAT)
		db_event.end_at = datetime.strptime(exam['end_at'], DATE_FORMAT)
		db_event.created_at = datetime.strptime(exam['created_at'], DATE_FORMAT)
		db_event.updated_at = datetime.strptime(exam['updated_at'], DATE_FORMAT)
		session.merge(db_event)
		session.commit()
	except Exception as e:
		logging.error('Error creating exam event in DB: {}'.format(str(e)))
		session.rollback()


class EventsRunner:
	def get_events(self, user:User, since:str, fetch_start_str:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, fetch_start_str) }

		# Fetch events_users
		# To watch for any new or updated registrations
		try:
			events_users = ic.pages_threaded('users/{}/events_users'.format(user.intra_id), params=payload)
		except Exception as e:
			logging.error('Error fetching events_users for user {}'.format(user.login))
			logging.error(str(e))
			return

		logging.info('Fetched {} events_users'.format(len(events_users)))
		for events_user in events_users:
			create_or_update_event(events_user['event'], user.intra_id)
		session.flush()

		# And now, surprise, also fetch exams!
		# We always fetch all though (no payload), since there is no way to fetch exams_users without staff credentials.
		# It shouldn't be too many anyways.
		try:
			exams = ic.pages_threaded('users/{}/exams'.format(user.intra_id), params={})
		except Exception as e:
			logging.error('Error fetching exams for user {}'.format(user.login))
			logging.error(str(e))
			return
		logging.info('Fetched {} exams'.format(len(exams)))
		for exam in exams:
			create_or_update_exam(exam, user)
		session.flush()


	def fetch_for_user(self, user:User, fetch_start:datetime):
		db_runner:Runner = session.query(Runner).filter_by(user_id = user.intra_id).one()
		last_fetch_time = BEGINNING_OF_TIME
		if db_runner.events:
			last_fetch_time = int(db_runner.events.timestamp())
		last_fetch_str = datetime.utcfromtimestamp(last_fetch_time).strftime(DATE_FORMAT)
		fetch_start_str = fetch_start.strftime(DATE_FORMAT)
		logging.info('Fetching changes in events (and exams) for user since {}'.format(last_fetch_str))
		self.get_events(user, last_fetch_str, fetch_start_str)
		db_runner:Runner = session.query(Runner).filter_by(user_id=user.intra_id).one()
		db_runner.events = fetch_start
		session.commit()
		session.flush()


	def get_events_for_campus(self, campus:Campus, since:str, fetch_start_str:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, fetch_start_str) }

		# Fetch events
		# To watch for any updates to events (updates to events do not update events_users)
		try:
			events = ic.pages_threaded('campus/{}/events'.format(campus.intra_id), params=payload)
		except Exception as e:
			logging.error('Error fetching events for campus {}'.format(campus.name))
			logging.error(str(e))
			return

		logging.info('Fetched {} events'.format(len(events)))
		for event in events:
			logging.info('Updating or creating events with intra_id {}'.format(str(event['id'])))
			update_many_events(event)
		session.flush()


	def fetch_for_campuses(self, fetch_start:datetime):
		# Create last fetch string based on the last updated_at event
		last_fetch_time = BEGINNING_OF_TIME
		last_updated_event:Event = session.query(Event).order_by(Event.updated_at.desc()).first()
		if last_updated_event:
			last_fetch_time = int(last_updated_event.updated_at.timestamp())
		last_fetch_time -= 43200 * 12 # Take a day off from the last fetch time, to make sure we don't miss any events
		last_fetch_str = datetime.utcfromtimestamp(last_fetch_time).strftime(DATE_FORMAT)
		fetch_start_str = fetch_start.strftime(DATE_FORMAT)

		campuses:list[Campus] = session.query(Campus).all()
		i = 1
		amount_campuses = len(campuses)
		for campus in campuses:
			logging.info('Fetching events for campus {} ({}) --- {} of {} campuses...'.format(campus.name, str(campus.intra_id), str(i), amount_campuses))
			self.get_events_for_campus(campus, last_fetch_str, fetch_start_str)
			i += 1


	def run(self):
		fetch_start = datetime.utcnow()

		# First fetch all events for campuses (to update any previously existing events)
		self.fetch_for_campuses(fetch_start)

		# And now for the users (to update any new events and registrations)
		users:list[User] = session.query(User.intra_id, User.login, User.campus_id).all()
		i = 1
		amount_users = len(users)
		for user in users:
			logging.info('Fetching events (and exams) for {} ({}) --- {} of {} users...'.format(user.login, str(user.intra_id), str(i), amount_users))
			self.fetch_for_user(user, fetch_start)
			i += 1


	def run_for_user(self, login:str):
		user:User = session.query(User).filter_by(login=login).one_or_none()
		if not user:
			logging.error('User with login {} not found'.format(login))
			return

		fetch_start = datetime.utcnow()

		# First fetch all events for campuses (to update any previously existing events)
		logging.info('Preparing to fetch events (and exams) for user {} ({}), first fetching all campus events...'.format(user.login, str(user.intra_id)))
		self.fetch_for_campuses(fetch_start)

		# And now for the user
		logging.info('Fetching events (and exams) for user {} ({})'.format(user.login, str(user.intra_id)))
		self.fetch_for_user(user, fetch_start)


eventsRunner = EventsRunner()
