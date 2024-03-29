import json

from src.lib.auth.decorators import ext_token_preferred_json
from src.lib.auth.tokens import parse_ical_token, create_ical_token
from flask import session, request, redirect, Response
from src.models.models import Event, Runner
from ics import Calendar, Event as IcsEvent
from ics.grammar.parse import ContentLine
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
	# Generate ical_token for user and redirect to events_ics endpoint
	ical_token = create_ical_token(session['uid'])
	return redirect("{}v2/events/{}.ics".format(request.url_root, ical_token.encode().hex()), code=302)


@app.route('/v2/events/ics.json', methods=['GET'])
@ext_token_preferred_json
def get_ics_link():
	# Generate ical_token for user and redirect to events_ics endpoint
	ical_token = create_ical_token(session['uid'])
	return { 'type': 'success', 'message': 'Generated iCal link', 'data': '{}v2/events/{}.ics'.format(request.url_root, ical_token.encode().hex()) }


# Get iCal calendar for events a user is subscribed to
# User is authenticated based on an ical_token (not to be confused with an ext_token)
@app.route('/v2/events/<hextoken>.ics', methods=['GET'])
def events_ics(hextoken:str):
	# Convert hex token to ical_token
	try:
		ical_token = bytes.fromhex(hextoken).decode('utf-8', 'strict')
	except:
		return "400 Bad Request", 400

	# Check if ical_token belongs to any user
	try:
		user, user_token, expires_at = parse_ical_token(ical_token)
	except:
		return "401 Unauthorized", 401

	# Retrieve last fetch date from runner
	runner:Runner = Runner.query.filter_by(user_id=user.intra_id).first()
	if not runner or not runner.events:
		return "404 Not Found", 404

	# Retrieve all events for the user
	events:list[Event] = Event.query.filter_by(user_id=user.intra_id).all()

	# Create iCal calendar
	cal = Calendar(creator='-//Improved Intra Server v{}//NONSGML Intra Event Calendar//EN'.format(__version__))
	cal.extra.append(ContentLine(name='X-WR-CALNAME', value='Intra {}'.format(user.login)))
	cal.extra.append(ContentLine(name='NAME', value='Intra {}'.format(user.login)))
	cal.extra.append(ContentLine(name='X-WR-CALDESC', value='Intra events and exams {} has registered to'.format(user.login)))
	cal.extra.append(ContentLine(name='DESCRIPTION', value='Intra events and exams {} has registered to'.format(user.login)))
	cal.extra.append(ContentLine(name='X-PUBLISHED-TTL', value='PT3H'))
	cal.extra.append(ContentLine(name='REFRESH-INTERVAL;VALUE=DURATION', value='PT3H'))
	cal.extra.append(ContentLine(name='X-ORIGINAL-URL', value=str(request.url)))
	cal.extra.append(ContentLine(name='URL', value=str(request.url)))
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
			classification = 'PUBLIC', # Otherwise Google Calendar won't show the event
		))

	# Create response with additional headers
	return cal.serialize(), 200, {
		'Content-Type': 'text/calendar',
		'Last-Modified': runner.events.strftime('%a, %d %b %Y %H:%M:%S GMT'),
		'Content-Disposition': 'attachment; filename="events-{}.ics"'.format(user.login),
		'Expires': expires_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
	}
	# Use the line below for debugging plaintext
	# return cal.serialize(), 200, {'Content-Type': 'text/plain', 'Last-Modified': runner.events.strftime('%a, %d %b %Y %H:%M:%S GMT')}
