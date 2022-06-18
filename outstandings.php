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

	// TODO: store and check db/outstandings/username.json

	$token = get_client_token();

	$userID = get_user_id($token, $_GET["username"]);
	if ($userID === false) {
		http_response_code(502);
		respond("error", "Intra API error");
	}
	if ($userID < 0) {
		http_response_code(404);
		respond("error", "User not found");
	}

	// sleep to prevent 429
	// ugly but it works for now
	sleep(1);

	$retrieveFromTeamIDs = array();
	$teamIDs = get_team_ids($token, $userID);
	$projectsUserIDs = array_keys($teamIDs);
	if ($teamIDs === false) {
		http_response_code(502);
		respond("error", "Intra API error");
	}
	if (count($projectsUserIDs) == 0) {
		http_response_code(200);
		respond("success", "User hasn't finished any projects yet", array());
	}

	$outstandings = $teamIDs; // = deep clone!

	// set all outstanding amounts to 0
	foreach ($outstandings as &$projectsUser) {
		$projectsUser["current"] = 0; // init outstandings amount for current team
		$projectsUser["best"] = 0; // init outstandings amount for best team
		$teamAmount = count($projectsUser["all"]);
		for ($i = 0; $i < $teamAmount; $i++) {
			array_push($retrieveFromTeamIDs, $projectsUser["all"][$i]); // add this teamID to list of teamIDs to retrieve the mark from
			$projectsUser["all"][$i] = 0; // init outstandings amount for one of user's teams
		}
	}

	$page = 1;
	while (true) { // infinitely loop until all evaluations are fetched
		$ch = curl_init();
		$headers = array();
		curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/v2/users/".strval($userID)."/scale_teams/as_corrected?page[size]=100&page[number]=".$page);
		curl_setopt($ch, CURLOPT_HTTPHEADER, array( "Content-Type: application/json" , "Authorization: Bearer ".$token ));
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_HEADERFUNCTION, function($ch, $header) use(&$headers) {
			$len = strlen($header);
			$header = explode(':', $header, 2);
			if (count($header) < 2) { // ignore invalid headers
				return $len;
			}
			$headers[strtolower(trim($header[0]))] = trim($header[1]);
			return $len;
		});
		$response = curl_exec($ch);

		if ($response !== false) {
			try {
				$json = json_decode($response, true);
				foreach ($json as &$eval) {
					// retrieve the projectsUser ID from this evaluation. If we did not wish to retrieve outstanding flags for this projectsUser, continue.
					$projectsUserID = get_project_user_id_from_team_ids($teamIDs, $eval["team"]["id"]);
					if ($projectsUserID === false) {
						continue;
					}
					// echo "projectsUserID: ".$projectsUserID.", teamID: ".$eval["team"]["id"].", Flag: " . $eval["flag"]["id"] . "\n";
					if ($eval["flag"]["id"] == 9) { // id 9 is the key of an Outstanding flag.
						$teamIDsForProj = &$teamIDs[$projectsUserID];
						$outstandingsForProj = &$outstandings[$projectsUserID];

						if ($eval["team"]["id"] == $teamIDsForProj["current"]) { // this evaluation was done for the current team
							// echo "Increased CURRENT of " . $projectsUserID . " by one\n";
							$outstandingsForProj["current"]++; // increase its outstanding amount by 1
						}

						if ($eval["team"]["id"] == $teamIDsForProj["best"]) { // this evaluation was done for the team with the highest mark
							// echo "Increased BEST of " . $projectsUserID . " by one\n";
							$outstandingsForProj["best"]++; // increase its outstanding amount by 1
						}

						$teamIndex = array_search($eval["team"]["id"], $teamIDsForProj["all"]);
						if ($teamIndex !== false) { // team is listed in list of teamIDs for this user's projects
							// echo "Increased ALL index " . $teamIndex . " (" . $teamIDsForProj["all"][$teamIndex] . ") of " . $projectsUserID . " by one\n";
							$outstandingsForProj["all"][$teamIndex]++; // increase its outstanding amount by 1
						}
					}
				}

			}
			catch (Exception $e) {
				http_response_code(500);
				respond("error", "An error occurred while parsing the outstanding marks");
			}

			// check if we've gone through all pages
			$itemsFetched = intval($headers["x-per-page"]) * intval($headers["x-page"]);
			if ($itemsFetched >= intval($headers["x-total"])) {
				break; // we have! quit the infinite loop
			}
			$page++;
			sleep(1); // sleep to prevent 429
		}
		else {
			http_response_code(502);
			respond("error", "Intra API unreachable");
		}
	}

	http_response_code(200);
	respond("success", "Outstandings for user, per projectsUser", $outstandings);
?>
