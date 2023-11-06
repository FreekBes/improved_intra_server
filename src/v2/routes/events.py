import json

from src.lib.auth.decorators import session_required_json
from src.models.models import Event, Runner
from flask import session, Response
from src import app


@app.route('/v2/events', methods=['GET'])
@session_required_json
def events_overview():
	# Retrieve last fetch date from runner
	runner:Runner = Runner.query.filter_by(user_id=session['uid']).first()
	if not runner or not runner.events:
		return { 'type': 'error', 'message': 'No data found' }, 404

	# Retrieve all events for the user
	events:list[Event] = Event.query.filter_by(user_id=session['uid']).all()
	events_dict = []
	for event in events:
		events_dict.append({
			'id': event.intra_id,
			'is_exam': event.is_exam,
			'name': bytes.fromhex(event.name).decode('utf-8', 'ignore'),
			'description': bytes.fromhex(event.description).decode('utf-8', 'ignore'),
			'location': bytes.fromhex(event.location).decode('utf-8', 'ignore'),
			'kind': event.kind,
			'max_people': event.max_people,
			'nbr_subscribers': event.nbr_subscribers,
			'cursus_ids': json.loads(event.cursus_ids),
			'campus_ids': json.loads(event.campus_ids),
			'begin_at': event.begin_at,
			'end_at': event.end_at,
			'created_at': event.created_at,
			'updated_at': event.updated_at,
		})
	# Create response with additional headers
	resp = Response(
		response = { 'type': 'success', 'message': 'Fetched all events to which user is subscribed', 'data': events_dict },
		status = 200,
		mimetype = 'application/json'
	)
	resp.headers['Last-Modified'] = runner.events.strftime('%a, %d %b %Y %H:%M:%S GMT')
	return (resp.response, resp.status_code, resp.headers.items())
