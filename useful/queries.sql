--- Get an overview of users per campus
SELECT COUNT(users.intra_id), campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id GROUP BY campuses.name;

--- See which staff is using the extension
SELECT users.login, campuses.name FROM users JOIN campuses ON campuses.intra_id = users.campus_id WHERE staff='t';
