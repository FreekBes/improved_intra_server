<?php
	require_once("include/respond.php");

	@session_start();

	// include authorization methods
	require_once("include/auth.php");

	// trim entire post array
	$_POST = array_map("trim", $_POST);

	if (!isset($_POST["username"]) || empty($_POST["username"])) {
		http_response_code(400);
		respond("error", "POST key 'username' is not set, but is required to delete the settings of a user");
	}
	else {
		// do some security checks before modifiying files...
		if (!is_valid_username($_POST["username"])) {
			http_response_code(403);
			respond("warning", "Invalid username");
			die();
		}

		// check if username matches the one found using the access token provided...
		// line below is commented out since front-end of extension handles access token refreshing (by calling testkey.php)
		// refresh_access_token_if_needed($userSettings["refresh_token"], intval($userSettings["created_at"]), intval($userSettings["expires_in"]));
		$userInfoFromIntra = get_user_info($userSettings["access_token"]);
		if ($userSettings["username"] != $userInfoFromIntra["login"]) {
			http_response_code(403);
			respond("error", "Username does not match the one found using the access token provided");
			die();
		}

		// delete settings of user
		if (unlink("settings/".strval($_POST["username"]).".json") === true) {
			http_response_code(200);
			respond("success", "User settings have been deleted");
		}
		else {
			http_response_code(500);
			respond("error", "Could not delete user settings");
		}
	}
?>
