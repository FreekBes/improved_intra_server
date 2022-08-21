from sqlalchemy import Column as Col, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from src import db
import time
import os


class Column(Col):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('nullable', False) # Default Column to be not nullable
		super().__init__(*args, **kwargs)


class BannerImg(db.Model):
	__tablename__ = 'banner_imgs'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.intra_id'), nullable=True)
	url = Column(String)
	width = Column(Integer, default=0)
	height = Column(Integer, default=0)
	size = Column(Integer, default=0) # File size in bytes
	created_at = Column(DateTime, default=func.now())

	def __repr__(self):
		return "<BannerImg id={}, user_id={}, url='{}', width={}, height={}, size={}, created_at='{}'>"\
			.format(self.id, self.user_id, self.url, self.width, self.height, self.size, self.created_at)

	def __init__(self, user_id, url):
		self.user_id = user_id
		self.url = url
		# TODO: retrieve width, height, size

	def from_file(self, user_id, iintra_url, path):
		self.user_id = user_id
		file_name, file_ext = os.path.splitext(path)
		self.url = iintra_url + '/banners/' + user_id + time.time() + file_ext
		# TODO: retrieve width, height, size


class BannerPosition(db.Model):
	__tablename__ = 'banner_positions'
	id = Column(Integer, primary_key=True)
	css_val = Column(String, unique=True)
	name = Column(String, unique=True)

	def __repr__(self):
		return "<BannerPosition id={}, css_val='{}', name='{}'>"\
			.format(self.id, self.css_val, self.name)

	def __init__(self, css_val, name):
		self.css_val = css_val
		self.name = name


class Campus(db.Model):
	__tablename__ = 'campuses'
	intra_id = Column(Integer, primary_key=True, autoincrement=False)
	name = Column(String)
	country = Column(String)

	def __repr__(self):
		return "<Campus intra_id={}, name='{}', country='{}'>"\
			.format(self.intra_id, self.name, self.country)

	def __init__(self, intra_id, name, country):
		self.intra_id = intra_id
		self.name = name
		self.country = country


class ColorScheme(db.Model):
	__tablename__ = 'color_schemes'
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	enabled = Column(Boolean, default=True)
	internal_name = Column(String, unique=True)

	def __repr__(self):
		return "<ColorScheme id={}, internal_name='{}', name='{}', enabled={}>"\
			.format(self.id, self.internal_name, self.name, str(self.enabled))

	def __init__(self, internal_name, name):
		self.name = name
		self.internal_name = internal_name
		self.enabled = True


class Evaluation(db.Model):
	__tablename__ = 'evaluations'
	intra_id = Column(Integer, primary_key=True, autoincrement=False)
	intra_team_id = Column(Integer, ForeignKey('teams.id'))
	success = Column(Boolean, default=False)
	outstanding = Column(Boolean, default=False)
	mark = Column(Integer, default=0)
	evaluator_id = Column(Integer)
	evaluated_at = Column(DateTime(timezone=False))

	def __repr__(self):
		return "<Evaluation intra_id={}, intra_team_id={}, success={}, outstanding={}, mark={}, evaluator_id={}, evaluated_at={}>"\
			.format(self.intra_id, self.intra_team_id, self.success, self.outstanding, self.mark, self.evaluator_id, self.evaluated_at)


class Profile(db.Model):
	__tablename__ = 'profiles'
	user_id = Column(Integer, ForeignKey('users.intra_id'), primary_key=True)
	banner_img = Column(Integer, ForeignKey('banner_imgs.id'), nullable=True, default=None)
	banner_pos = Column(Integer, default=1)
	link_git = Column(String, nullable=True, default=None)
	link_web = Column(String, nullable=True, default=None)
	updated_at = Column(DateTime(timezone=False), onupdate=func.now(), default=func.now())

	def __repr__(self):
		return "<Profile user_id={}, banner_img={}, banner_pos={}, updated_at='{}'>"\
			.format(self.user_id, self.banner_img, self.banner_pos, self.updated_at)


class Settings(db.Model):
	__tablename__ = 'settings'
	user_id = Column(Integer, ForeignKey('users.intra_id'), primary_key=True)
	updated_at = Column(DateTime(timezone=False), onupdate=func.now(), default=func.now())
	updated_ver = Column(String, nullable=True)
	theme = Column(Integer, default=1)
	colors = Column(Integer, ForeignKey('color_schemes.id'), default=1)
	show_custom_profiles = Column(Boolean, default=True)
	hide_broadcasts = Column(Boolean, default=False)
	logsum_month = Column(Boolean, default=True)
	logsum_week = Column(Boolean, default=True)
	outstandings = Column(Boolean, default=True)
	hide_goals = Column(Boolean, default=False)
	holygraph_more_cursuses = Column(Boolean, default=False)
	old_blackhole = Column(Boolean, default=False)
	clustermap = Column(Boolean, default=True)
	codam_monit = Column(Boolean, default=True)
	codam_auto_equip_coa_title = Column(Boolean, default=False)

	def __repr__(self):
		return "<Settings user_id={}, updated_at='{}', updated_ver='{}', theme={}, colors={}, show_custom_profiles={}, hide_broadcasts={}, logsum_month={}, " + \
			"logsum_week={}, outstandings={}, hide_goals={}, holygraph_more_cursuses={}, old_blackhole={}, codam_monit={}, " + \
			"codam_auto_equip_coa_title={}>"\
			.format(self.user_id, self.updated_at, self.updated_ver, self.theme, self.colors, str(self.show_custom_profiles), str(self.hide_broadcasts),
				str(self.logsum_month), str(self.logsum_week), str(self.outstandings), str(self.hide_goals), str(self.holygraph_more_cursuses),
				str(self.old_blackhole), str(self.codam_monit), str(self.codam_auto_equip_coa_title))


class Team(db.Model):
	__tablename__ = 'teams'
	id = Column(Integer, primary_key=True)
	intra_id = Column(Integer) # Intra ID, is not unique - teams here are tied to users instead of Intra teams
	user_id = Column(Integer, ForeignKey('users.intra_id'))
	projects_user_id = Column(Integer)
	current = Column(Boolean, default=False)
	best = Column(Boolean, default=False)
	final_mark = Column(Integer, default=0)

	def __repr__(self):
		return "<Team id={}, intra_id={}, user_id={}, projects_user_id={}, current={}, best={}, final_mark={}>"\
			.format(self.id, self.intra_id, self.user_id, self.projects_user_id, str(self.current), str(self.best), self.final_mark)


class User(db.Model):
	__tablename__ = 'users'
	intra_id = Column(Integer, primary_key=True, autoincrement=False)
	login = Column(String, unique=True)
	campus_id = Column(Integer, ForeignKey('campuses.intra_id'), nullable=True)
	email = Column(String)
	first_name = Column(String, default='')
	last_name = Column(String, default='')
	display_name = Column(String, default=login)
	staff = Column(Boolean, default=False)
	anonymize_date = Column(Date)
	created_at = Column(DateTime, default=func.now())

	def __repr__(self):
		return "<User intra_id={}, login='{}', campus_id={}, staff={}, email='{}', first_name='{}', last_name='{}', created_at='{}'"\
			.format(self.intra_id, self.login, self.campus_id, str(self.staff), self.email, self.first_name, self.last_name, self.created_at)
