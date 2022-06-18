<?php
	require_once("nogit.php");

	// obtain shared memory space
	$shm = shm_attach(43);

	function token_expired($createdAt, $expiresIn) {
		// 7200 seconds less: say it expired 2 hours in advance.
		// For just in case Intra API f*cked up the timezones and $createdAt is not UTC.
		return ($createdAt + $expiresIn < time() - 7200);
	}

	function get_client_token() {
		global $shm, $clientID, $clientSecret;

		if (shm_has_var($shm, 0x01)) {
			$full_auth = json_decode(unserialize(shm_get_var($shm, 0x01)), true);
			if (!token_expired(intval($full_auth["created_at"]), intval($full_auth["expires_in"]))) {
				return ($full_auth["access_token"]);
			}
		}

		$ch = curl_init();
		$postData = array(
			"client_id" => $clientID,
			"client_secret" => $clientSecret,
			"grant_type" => "client_credentials"
		);
		curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/oauth/token");
		curl_setopt($ch, CURLOPT_POST, true);
		curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$response = curl_exec($ch);

		if ($response !== false) {
			try {
				$json = json_decode($response, true);
				if (array_key_exists("error", $json)) {
					return (null);
				}
				shm_put_var($shm, 0x01, serialize($response));
				return ($json["access_token"]);
			}
			catch (Exception $e) {
				return (null);
			}
		}
		return (null);
	}

	function is_valid_username($username) {
		if ($username == "null" || $username == "undefined") {
			return (false);
		}
		if (preg_match('/[^a-z\-]/', $username)) {
			return (false);
		}
		return (true);
	}

	function get_user_id($token, $login) {
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/v2/users?filter[login]=".urlencode($login));
		curl_setopt($ch, CURLOPT_HTTPHEADER, array( "Content-Type: application/json" , "Authorization: Bearer ".$token ));
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$response = curl_exec($ch);

		if ($response !== false) {
			try {
				$json = json_decode($response, true);
				if (array_key_exists("error", $json))
					return (false);
				if (!array_key_exists("id", $json[0])) {
					return (-1);
				}
				return (intval($json[0]["id"]));
			}
			catch (Exception $e) {
				return (false);
			}
		}
		return (false);
	}

	// returns an object containing all teamIDs per projectUser
	function get_team_ids($token, $userID) {
		$teamIDs = array();
		$page = 1;
		while (true) { // infinitely loop until all evaluations are fetched
			$ch = curl_init();
			$headers = array();
			curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/v2/users/".strval($userID)."/projects_users?filter[status]=finished&page[size]=100&page[number]=".$page);
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
					foreach ($json as &$projectsUser) {
						if ($projectsUser["validated?"]) {
							$projUID = $projectsUser["id"];
							$teamIDs[$projUID] = array();
							$teamIDs[$projUID]["current"] = $projectsUser["current_team_id"];
							$teamIDsInProj = array();
							$highestMark = -INF;
							$highestMarkTeam = $projectsUser["current_team_id"]; // placeholder, will get overwritten in upcoming foreach
							foreach ($projectsUser["teams"] as &$team) {
								array_push($teamIDsInProj, $team["id"]);
								if ($team["final_mark"] > $highestMark) {
									$highestMark = $team["final_mark"];
									$highestMarkTeam = $team["id"];
								}
							}
							$teamIDs[$projUID]["best"] = $highestMarkTeam;
							$teamIDs[$projUID]["all"] = array_reverse($teamIDsInProj); // in reverse order, assuming a higher ID means team was created later
						}
					}
				}
				catch (Exception $e) {
					return (false);
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
				return (false);
			}
		}
		return ($teamIDs);
	}

	// for finding the ProjectUserID from an object returned by get_team_ids
	function get_project_user_id_from_team_ids($teamIDs, $teamID) {
		foreach ($teamIDs as $projectsUserID => &$projectsUserTeamIDs) {
			if (in_array($teamID, $projectsUserTeamIDs["all"])) {
				return ($projectsUserID);
			}
		}
		return (false);
	}
?>
