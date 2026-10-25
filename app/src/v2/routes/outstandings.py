from src.models.models import Evaluation, Runner, Team, User
from flask import Response, request
from src.lib.auth.decorators import *
from sqlalchemy.sql import func
from sqlalchemy import case
from src import app, db


@app.route('/v2/outstandings/<login>', methods=['GET'])
def outstandings(login):
	# Retrieve user and check if outstanding runner already fetched outstandings for this user
	db_user = db.session.query(User.intra_id, Runner.outstandings).join(Runner).filter(User.login == login).first()
	if not db_user or not db_user.outstandings:
		return { 'type': 'success', 'message': 'No data exists for this user', 'data': [] }, 200

	outstandings = dict()

	# Retrieve outstandings for each project user and fetch the amount of outstanding evaluations for each team
	# Outer join, to make sure even teams without evaluations are returned
	db_q = db.session.query(Team, func.sum(case((Evaluation.outstanding == True, 1), else_ = 0)).label('outstandings')).outerjoin(Evaluation, Evaluation.intra_team_id == Team.intra_id).filter(Team.user_id == db_user.intra_id).order_by(Team.projects_user_id.desc(), Team.intra_id.desc()).group_by(Team.id)
	db_res:list = db_q.all()

	handled_team_ids:list[int] = []

	for db_row in db_res:
		# Sometimes the same team is returned twice in the query, so we need to skip it
		# This is because a Team can appear multiple times in the table: once per user in the team!
		# Makes it easier to handle other data, but it is sort of a pain here... Maybe a postgres view would one day be better?
		if db_row.Team.intra_id in handled_team_ids:
			continue
		if not str(db_row.Team.projects_user_id) in outstandings:
			pu_outstandings = dict()
			pu_outstandings['current'] = 0
			pu_outstandings['best'] = 0
			pu_outstandings['all'] = list()
			outstandings[str(db_row.Team.projects_user_id)] = pu_outstandings
		else:
			pu_outstandings = outstandings[str(db_row.Team.projects_user_id)]
		if db_row.Team.current:
			pu_outstandings['current'] = db_row.outstandings
		if db_row.Team.best:
			pu_outstandings['best'] = db_row.outstandings
		pu_outstandings['all'].append(db_row.outstandings)
		handled_team_ids.append(db_row.Team.intra_id)

	# Create response with additional headers
	resp = Response(
		response = { 'type': 'success', 'message': 'Outstandings for user, per projectsUser', 'data': outstandings },
		status = 200,
		mimetype = 'application/json'
	)
	resp.headers['Last-Modified'] = db_user.outstandings.strftime('%a, %d %b %Y %H:%M:%S GMT')
	return (resp.response, resp.status_code, resp.headers.items())
