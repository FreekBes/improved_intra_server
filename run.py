from .src import app, config

if __name__ == '__main__':
	app.run(debug=True, port=config['FLASK_PORT'], host='0.0.0.0')
