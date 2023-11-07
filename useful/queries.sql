--- Get an overview of users per campus
SELECT COUNT(users.intra_id), campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id GROUP BY campuses.name;

--- Get an overview of active users in the past month
SELECT users.login, users.created_at, user_tokens.last_used_at, settings.updated_ver, campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id LEFT JOIN settings ON settings.user_id = users.intra_id LEFT JOIN user_tokens ON user_tokens.user_id = users.intra_id WHERE user_tokens.last_used_at > date_trunc('month', current_date - interval '1'month) ORDER BY campuses.name;

--- See which staff used the extension
SELECT users.login, users.created_at, user_tokens.last_used_at, settings.updated_ver, campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id LEFT JOIN settings ON settings.user_id = users.intra_id LEFT JOIN user_tokens ON user_tokens.user_id = users.intra_id WHERE staff='t' ORDER BY users.created_at;
