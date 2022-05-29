<?php
	@session_start();

	// set headers
	header('Content-Type: application/json; charset=utf-8');
	header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
	header("Cache-Control: post-check=0, pre-check=0", false);
	header("Pragma: no-cache");

	// set respond function
	function respond($type = "success", $msg, $data = null) {
		$res = array();
		$res["type"] = $type;
		$res["message"] = $msg;
		if (!empty($data)) {
			$res["data"] = $data;
		}
		echo json_encode($res, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
		die();
	}

	// include authorization methods
	require_once("auth.php");

	// TODO: authenticate user somehow! Building times should not be accessible to non-42 people.

	if (!isset($_GET["username"]) || empty($_GET["username"])) {
		http_response_code(400);
		respond("error", "GET key 'username' is not set, but is required");
	}

	// do some security checks before checking server files...
	if ($_GET["username"] == "null" || $_GET["username"] == "undefined") {
		http_response_code(403);
		respond("warning", "Invalid username");
	}
	if (preg_match('/[^a-z\-]/', $_GET["username"])) {
		http_response_code(406);
		respond("warning", "Invalid characters in username");
	}

	// check if user is okay with sharing building times...
	$settings_file = "settings/" . $_GET["username"] . ".json";
	if (!file_exists($settings_file)) {
		http_response_code(403);
		respond("success", "Building times of user are private", new stdClass);
		// settings file actually not found, but do not report this to client for privacy reasons
	}
	$settings_raw = file_get_contents($settings_file);
	if (!$settings_raw) {
		http_response_code(500);
		respond("error", "Settings file read error");
	}
	$settings = json_decode($settings_raw, true);
	if (!isset($settings["codam-buildingtimes-public"]) || $settings["codam-buildingtimes-public"] !== true) {
		http_response_code(403);
		respond("success", "Building times of user are private", new stdClass);
	}

	$times_file = "db/buildingtimes/" . $_GET["username"] . ".json";
	if (!file_exists($times_file)) {
		http_response_code(404);
		respond("success", "Building times not being recorded for user", new stdClass);
	}
	else {
		$times_raw = file_get_contents($times_file);
		if (!$times_raw) {
			http_response_code(500);
			respond("error", "Building times file read error");
		}
		$times = json_decode($times_raw, true);
		if (isset($_GET["parsed"])) {
			foreach ($times as $date => $time) {
				$parsed_time = strtotime($time);
				if (!$parsed_time) {
					$times[$date] = 0;
					continue;
				}
				$times[$date] = floor(($parsed_time - strtotime('TODAY')) / 60);
			}
		}
		http_response_code(200);
		respond("success", "Building times retrieved for user", $times);
	}
?>
