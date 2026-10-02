from src.lib.auth.decorators import session_required_redirect, staff_acc_required_json
from src.models.models import BannerImg, User, Campus
from flask import request
from sqlalchemy import func
from src import app, db

@app.route('/v2/banners/<offset>', methods=['GET'])
@session_required_redirect
@staff_acc_required_json
def bannersoffset(offset):
	try:
		n_offset = int(offset)
		if not 0 <= n_offset <= 9223372036854775807:
			raise ValueError
	except ValueError:
		return { 'type': 'error', 'message': 'Invalid offset' }, 400
	query = db.session.query(BannerImg, User, Campus.name).outerjoin(User, User.intra_id == BannerImg.user_id).outerjoin(Campus, Campus.intra_id == User.campus_id).filter(BannerImg.url != '')
	campus_id = request.args.get('campus_id', '').strip()
	if campus_id:
		try:
			campus_id = int(campus_id)
			if not 0 < campus_id <= 2147483647:
				raise ValueError
		except ValueError:
			return { 'type': 'error', 'message': 'Invalid campus' }, 400
		query = query.filter(User.campus_id == campus_id)
	login = request.args.get('login', '').strip()
	if login:
		query = query.filter(func.lower(User.login).contains(login.lower(), autoescape=True))
	banner_imgs = query.order_by(BannerImg.created_at.desc(), BannerImg.id.desc()).offset(n_offset).limit(100).all()
	banners = []
	for banner_img, user, campus_name in banner_imgs:
		banner_dict = banner_img.to_dict()
		banner_dict['user'] = {
			'campus': campus_name,
			'login': user.login if user else None,
			'staff': user.staff if user else False
		}
		banners.append(banner_dict)
	if len(banners) > 0:
		return { 'type': 'success', 'message': 'Banners retrieved', 'data': banners }, 200
	return { 'type': 'success', 'message': 'No more banners to retrieve', 'data': [] }, 204
