import json

from src.lib.auth.decorators import ext_token_preferred_json
from src.lib.auth.tokens import parse_ext_token, create_ext_token
from flask import session, request, redirect, Response
from src.models.models import Event, Runner
from ics import Calendar, Event as IcsEvent
from src import app, __version__


@app.route('/v2/events', methods=['GET'])
@ext_token_preferred_json
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


@app.route('/v2/events.ics', methods=['GET'])
@ext_token_preferred_json
def redir_to_ics():
	# Generate ext_token for user and redirect to events_ics endpoint
	ext_token = create_ext_token(session['uid'])
	return redirect("{}v2/events/{}.ics".format(request.url_root, ext_token.encode().hex()), code=302)


# Get iCal calendar for events a user is subscribed to
# User is authenticated based on an ext_token (this URL should thus never be shared, as it would allow anyone to access the user's session)
@app.route('/v2/events/<hextoken>.ics', methods=['GET'])
def events_ics(hextoken:str):
	# Convert hex token to ext_token
	try:
		ext_token = bytes.fromhex(hextoken).decode('utf-8', 'strict')
	except:
		return "400 Bad Request", 400

	# Check if ext_token belongs to user
	try:
		user, user_token = parse_ext_token(ext_token)
	except:
		return "401 Unauthorized", 401

	# Retrieve last fetch date from runner
	runner:Runner = Runner.query.filter_by(user_id=session['uid']).first()
	if not runner or not runner.events:
		return "404 Not Found", 404

	# Retrieve all events for the user
	events:list[Event] = Event.query.filter_by(user_id=user.intra_id).all()

	# Create iCal calendar
	cal = Calendar(creator='-//Improved Intra Server v{}//NONSGML v1.0//EN'.format(__version__))
	for event in events:
		cal.events.add(IcsEvent(
			name = bytes.fromhex(event.name).decode('utf-8', 'ignore'),
			begin = event.begin_at,
			end = event.end_at,
			uid = str(event.intra_id),
			description = bytes.fromhex(event.description).decode('utf-8', 'ignore').replace('\r\n', '\n'),
			created = event.created_at,
			last_modified = event.updated_at,
			location = bytes.fromhex(event.location).decode('utf-8', 'ignore'),
			url = "https://profile.intra.42.fr/{}/{}".format(("exams" if event.is_exam else "events"), event.intra_id),
			categories = [event.kind],
			transparent = False,
			status = 'CONFIRMED',
			classification = 'PRIVATE',
		))

	# Create response with additional headers
	return cal.serialize(), 200, {'Content-Type': 'text/calendar', 'Last-Modified': runner.events.strftime('%a, %d %b %Y %H:%M:%S GMT'), 'Content-Disposition': 'attachment; filename="events-{}.ics"'.format(user.login)}
	# Use the line below for debugging plaintext
	# return cal.serialize(), 200, {'Content-Type': 'text/plain', 'Last-Modified': runner.events.strftime('%a, %d %b %Y %H:%M:%S GMT')}
