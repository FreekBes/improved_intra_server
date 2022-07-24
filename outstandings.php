<?php
	require_once("include/respond.php");
	require_once("include/api.php");

	if (!isset($_GET["username"]) || empty($_GET["username"])) {
		http_response_code(400);
		respond("error", "GET key 'username' is not set");
	}

	// set headers
	header('Content-Type: application/json; charset=utf-8');
	header("Cache-Control: public, max-age=43200, must-revalidate");
	header_remove("Pragma");

	if (!is_valid_username($_GET["username"])) {
		http_response_code(403);
		respond("warning", "Invalid username");
	}

	$fileName = "db/outstandings/".$_GET["username"].".json";

	$outstandings = file_get_contents($fileName);
	if ($outstandings === false) {
		http_response_code(200);
		respond("success", "No data exists for this user", array());
	}

	try {
		$outstandings = json_decode($outstandings, true);
	}
	catch (Exception $e) {
		http_response_code(500);
		respond("error", "JSON decoding failure");
	}

	http_response_code(200);
	header("Last-Modified: " . date("D, d M Y H:i:s", filemtime($fileName)) . " GMT");
	respond("success", "Outstandings for user, per projectsUser", $outstandings);
?>
