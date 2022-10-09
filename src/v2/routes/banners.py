from ...models.models import BannerImg, User, Campus
from flask import session
from ... import app

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
