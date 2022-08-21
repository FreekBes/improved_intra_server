-- we don't know how to generate root <with-no-name> (class Root) :(
create table banner_positions
(
	id      INTEGER not null
		constraint banner_positions_pk
			primary key autoincrement,
	css_val TEXT    not null,
	name    TEXT    not null
);

create unique index banner_positions_css_val_uindex
	on banner_positions (css_val);

create unique index banner_positions_name_uindex
	on banner_positions (name);

create table campuses
(
	intra_id INTEGER not null
		constraint campuses_pk
			primary key autoincrement,
	name     TEXT    not null,
	country  TEXT
);

create table color_schemes
(
	id            INTEGER not null
		constraint color_schemes_pk
			primary key autoincrement,
	name          TEXT    not null,
	enabled       BOOLEAN default 1 not null,
	internal_name TEXT    not null
);

create unique index color_schemes_internal_name_uindex
	on color_schemes (internal_name);

create unique index color_schemes_name_uindex
	on color_schemes (name);

CREATE TRIGGER color_scheme_update
	AFTER UPDATE ON color_schemes
	WHEN NEW.enabled=0
BEGIN
	UPDATE settings SET colors=1 WHERE colors=NEW.id;
END;

create table users
(
	intra_id       INTEGER not null
		constraint users_pk
			primary key autoincrement,
	login          TEXT    not null,
	first_name     TEXT    default '' not null,
	campus_id      INTEGER
		constraint campus_id
			references campuses
			on update cascade on delete set null,
	email          TEXT    not null,
	staff          BOOLEAN default 0 not null,
	last_name      TEXT    default '' not null,
	display_name   TEXT    default login not null,
	anonymize_date TEXT
);

create table banner_imgs
(
	id      INTEGER not null
		constraint banner_imgs_pk
			primary key autoincrement,
	user_id INTEGER
		constraint user_id
			references users
			on update cascade on delete set null,
	url     TEXT    not null,
	width   INTEGER default 0 not null,
	height  INTEGER default 0 not null,
	size    INTEGER default 0 not null
);

create table profiles
(
	user_id    INTEGER not null
		constraint profiles_pk
			primary key
		constraint id
			references users
			on update cascade on delete cascade,
	banner_img INTEGER
		constraint banner_img
			references banner_imgs
			on update cascade on delete set null,
	banner_pos INTEGER default 1 not null
		constraint banner_pos
			references banner_positions
			on update cascade on delete set default,
	link_git   TEXT,
	link_web   TEXT,
	updated_at TEXT    not null
);

CREATE TRIGGER profiles_update
	AFTER UPDATE ON profiles
BEGIN
	UPDATE profiles SET updated_at=DATETIME('NOW') WHERE user_id=NEW.user_id;
END;

create table settings
(
	user_id                    INTEGER not null
		constraint settings_pk
			primary key
		constraint id
			references users
			on update cascade on delete cascade,
	updated_at                 TEXT    not null,
	updated_ver                TEXT,
	theme                      INTEGER default 1 not null,
	colors                     INTEGER default 1 not null
		constraint color_scheme_id
			references color_schemes
			on update cascade on delete set default,
	show_custom_profiles       BOOLEAN default 1 not null,
	hide_broadcasts            BOOLEAN default 0 not null,
	logsum_month               BOOLEAN default 1 not null,
	logsum_week                BOOLEAN default 1 not null,
	outstandings               BOOLEAN default 1 not null,
	hide_goals                 BOOLEAN default 0 not null,
	holygraph_more_cursuses    BOOLEAN default 0 not null,
	old_blackhole              BOOLEAN default 0 not null,
	clustermap                 BOOLEAN default 1 not null,
	codam_monit                BOOLEAN default 1 not null,
	codam_auto_equip_coa_title BOOLEAN default 0 not null
);

CREATE TRIGGER settings_update
	AFTER UPDATE ON settings
BEGIN
	UPDATE settings SET updated_at=DATETIME('NOW') WHERE user_id=new.user_id;
end;

create table teams
(
	id               INTEGER not null
		constraint teams_pk
			primary key autoincrement,
	user_id          INTEGER not null
		constraint user_id
			references users
			on update cascade on delete cascade,
	projects_user_id INTEGER not null,
	current          BOOLEAN default 0 not null,
	best             BOOLEAN default 0 not null,
	final_mark       INTEGER,
	intra_id         INTEGER not null
);

create table evaluations
(
	intra_id      INTEGER not null
		constraint evaluations_pk
			primary key autoincrement,
	intra_team_id INTEGER not null
		constraint evaluations_teams_intra_id_fk
			references teams (intra_id)
			on update cascade on delete cascade,
	success       BOOLEAN default 0 not null,
	outstanding   BOOLEAN default 0 not null,
	mark          INTEGER default 0,
	evaluator_id  INTEGER not null,
	evaluated_at  TEXT    not null
);

create unique index users_login_uindex
	on users (login);

CREATE TRIGGER users_create
	AFTER INSERT ON users
BEGIN
	INSERT INTO settings (user_id, updated_at) VALUES (NEW.intra_id, DATETIME('NOW'));
	INSERT INTO profiles (user_id, updated_at) VALUES (NEW.intra_id, DATETIME('NOW'));
END;

--- default banner positions
INSERT INTO banner_positions (css_val, name) VALUES ('center center', 'Centered (default)');
INSERT INTO banner_positions (css_val, name) VALUES ('center top', 'Top');
INSERT INTO banner_positions (css_val, name) VALUES ('center bottom', 'Bottom');

--- default color schemes
INSERT INTO color_schemes (internal_name, name) VALUES ('default', 'Intra (default)');
INSERT INTO color_schemes (internal_name, name) VALUES ('cetus', 'Blue');
INSERT INTO color_schemes (internal_name, name) VALUES ('vela', 'Red');
INSERT INTO color_schemes (internal_name, name) VALUES ('pyxis', 'Purple');
INSERT INTO color_schemes (internal_name, name) VALUES ('green', 'Green');
INSERT INTO color_schemes (internal_name, name) VALUES ('yellow', 'Yellow');
INSERT INTO color_schemes (internal_name, name) VALUES ('windows', 'Windows');
