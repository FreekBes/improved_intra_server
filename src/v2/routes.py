from flask import session, redirect, url_for, render_template, jsonify
from ..models.models import BannerImg, User, Campus
from ..oauth import authstart
from .. import app, db
import json


@app.route('/v2/connect', methods=['GET'])
def connect():
	if not 'uid' in session:
		return authstart(2)
	return 'Connected V2', 200


@app.route('/v2/disconnect', methods=['GET'])
def disconnect():
	if not 'uid' in session:
		return 'Already logged out', 200
	session.pop('login')
	session.pop('uid')
	session.pop('staff')
	session.pop('v')
	session.pop('v1_conn_data')
	return 'Logged out', 200


@app.route('/v2/banners/<offset>', methods=['GET'])
def bannersoffset(offset):
	if not 'uid' in session:
		return { 'type': 'error', 'message': 'Unauthorized' }, 401
	if not 'staff' in session or session['staff'] != True:
		return { 'type': 'error', 'message': 'Access denied' }, 403
	try:
		n_offset = int(offset)
	except:
		return { 'type': 'error', 'message': 'Invalid offset' }, 400
	campuses:list[Campus] = db.session.query(Campus.intra_id, Campus.name).all()
	banner_imgs:list[BannerImg] = BannerImg.query.filter(BannerImg.url != '').order_by(BannerImg.created_at.desc()).offset(n_offset).limit(100).all()
	banners = []
	for banner_img in banner_imgs:
		banner_dict = banner_img.to_dict()
		user:User = db.session.query(User.campus_id, User.login, User.staff).filter(User.intra_id == banner_img.user_id).first()
		banner_dict['user'] = {
			'campus': next(campus.name for campus in campuses if campus.intra_id == user.campus_id) if user.campus_id != None else None,
			'login': user.login,
			'staff': user.staff
		}
		banners.append(banner_dict)
	if len(banners) > 0:
		return { 'type': 'success', 'message': 'Banners retrieved', 'data': banners }, 200
	return { 'type': 'success', 'message': 'No more banners to retrieve', 'data': [] }, 204
