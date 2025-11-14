import json

def row_to_dict(row:dict):
	d = {}
	for column in row.__table__.columns:
		d[column.name] = getattr(row, column.name)
	return d


def keyedtuple_row_to_dict(row:dict):
	# You can only use this when querying specific columns: e.g. db.session.query(User.id, User.name).all()
	return row._asdict()


def keyedtuple_rows_to_dict(rows:list[dict]):
	# You can only use this when querying specific columns: e.g. db.session.query(User.id, User.name).all()
	return [row._asdict() for row in rows]


def row_to_json_str(row:dict, indent=2, sort_keys=True):
	return json.dumps(row_to_dict(row), indent=indent, sort_keys=sort_keys, default=str).encode('utf-8')


def rows_to_json_str(rows:list[dict], indent=2, sort_keys=True):
	return json.dumps([row_to_dict(row) for row in rows], indent=indent, sort_keys=sort_keys, default=str).encode('utf-8')
