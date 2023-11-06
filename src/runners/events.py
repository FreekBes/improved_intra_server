import logging
import json

from src.models.models import Campus, Runner, Event
from src.lib.db import session
from datetime import datetime
from src.lib.intra import ic

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
BEGINNING_OF_TIME = 1262300400 # 2010-01-01


class EventsRunner:
	def get_events_for_campus(self, campus:Campus, since:str, now:str):
		payload = { 'range[updated_at]': '{},{}'.format(since, now) }
		events = ic.pages_threaded('campus/{}/events'.format(campus.intra_id), params=payload)
		logging.info('Fetched {} events'.format(len(events)))
		for event in events:
			try:
				# Create or update all events
				db_event:Event = session.query(Event).filter_by(intra_id=event['id'], campus_id=campus.intra_id).first()
				if not db_event:
					db_event = Event(
						intra_id=int(event['id']),
						campus_id=campus.intra_id,
						name=event['name'],
						description=event['description'] if event['description'] else "",
						location=event['location'] if event['location'] else "",
						kind=event['kind'] if event['kind'] else "event",
						max_people=int(event['max_people']) if event['max_people'] else 0,
						nbr_subscribers=int(event['nbr_subscribers']) if event['nbr_subscribers'] else 0,
						cursus_ids=json.dumps(event['cursus_ids']) if (event['cursus_ids'] and len(event['cursus_ids']) > 0) else "[]",
						begin_at=datetime.strptime(event['begin_at'], DATE_FORMAT),
						end_at=datetime.strptime(event['end_at'], DATE_FORMAT),
						created_at=datetime.strptime(event['created_at'], DATE_FORMAT),
						updated_at=datetime.strptime(event['updated_at'], DATE_FORMAT)
					)
			except Exception as e:
				logging.error('Error creating event in DB: {}'.format(str(e)))
				session.rollback()
		session.flush()


	def get_last_updated_event_timestamp(self, campus:Campus) -> int:
		db_event:Event = session.query(Event).filter_by(campus_id=campus.intra_id).order_by(Event.updated_at.desc()).first()
		return db_event.updated_at if db_event else BEGINNING_OF_TIME


	def run(self):
		campuses:list[Campus] = session.query(Campus.name, Campus.intra_id).all()

		fetch_start = datetime.utcnow()
		fetch_start_str = fetch_start.strftime(DATE_FORMAT)

		i = 1
		amount_campuses = len(campuses)
		for campus in campuses:
			logging.info('Fetching events for campus {} ({}) --- {} of {} campuses...'.format(campus.name, str(campus.intra_id), str(i), amount_campuses))
			# We do not store in the DB when this runner was last run, assume last updated event is the last time it was run
			last_updated_timestamp = self.get_last_updated_event_timestamp(campus)
			last_updated_str = datetime.utcfromtimestamp(last_updated_timestamp).strftime(DATE_FORMAT)
			self.get_events_for_campus(campus, last_updated_str, fetch_start_str)
			i += 1
