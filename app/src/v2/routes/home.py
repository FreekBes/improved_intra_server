from src.lib.auth.oauth import authstart
from flask import render_template, session
from src import app


@app.route('/')
def home():
	login = session['login'] if 'login' in session else None
	return render_template('v2/home.j2', login=login)
