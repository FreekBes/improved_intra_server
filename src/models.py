from sqlalchemy import Column as Col, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from src import db

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


class BannerPosition(db.Model):
	__tablename__ = 'banner_positions'
	id = Column(Integer, primary_key=True)
	css_val = Column(String, unique=True)
	name = Column(String, unique=True)


class Campus(db.Model):
	__tablename__ = 'campuses'
	intra_id = Column(Integer, primary_key=True, autoincrement=False)
	name = Column(String)
	country = Column(String)


class ColorSchemes(db.Model):
	__tablename__ = 'color_schemes'
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	enabled = Column(Boolean, default=True)
	internal_name = Column(String, unique=True)


class Evaluation(db.Model):
	__tablename__ = 'evaluations'
	intra_id = Column(Integer, primary_key=True, autoincrement=False)
	intra_team_id = Column(Integer, ForeignKey('teams.id'))
	success = Column(Boolean, default=False)
	outstanding = Column(Boolean, default=False)
	mark = Column(Integer, default=0)
	evaluator_id = Column(Integer)
	evaluated_at = Column(DateTime(timezone=False))


class Profile(db.Model):
	__tablename__ = 'profiles'
	user_id = Column(Integer, ForeignKey('users.intra_id'), primary_key=True)
	banner_img = Column(Integer, ForeignKey('banner_imgs.id'), nullable=True, default=None)
	banner_pos = Column(Integer, default=1)
	link_git = Column(String, nullable=True, default=None)
	link_web = Column(String, nullable=True, default=None)
	updated_at = Column(DateTime(timezone=False), onupdate=func.now(), default=func.now())


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


class Team(db.Model):
	__tablename__ = 'teams'
	id = Column(Integer, primary_key=True)
	intra_id = Column(Integer) # Intra ID, is not unique - teams here are tied to users instead of Intra teams
	user_id = Column(Integer, ForeignKey('users.intra_id'))
	projects_user_id = Column(Integer)
	current = Column(Boolean, default=False)
	best = Column(Boolean, default=False)
	final_mark = Column(Integer, default=0)


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
