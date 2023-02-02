--- Get an overview of users per campus
SELECT COUNT(users.intra_id), campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id GROUP BY campuses.name;

--- See which staff is using the extension
SELECT users.login, users.created_at, settings.updated_at, settings.updated_ver, campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id JOIN settings ON settings.user_id = users.intra_id WHERE staff='t' ORDER BY users.created_at;
