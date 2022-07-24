<?php
	// Runner script. Run this on boot, it will retrieve data for the database.
	// This is not the best solution. Some day I will upgrade it to something better.
	// It is also horrible code. One day! One day it will be better. Todo?

	require_once("cli.php");
	if (!is_cli()) {
		http_response_code(403);
		echo "Run this file from a CLI, not through the browser.";
		die();
	}

	require_once("api.php");

	function renew_access_tokens() {
		global $tokens;
		$tokens = get_client_tokens(); // TODO: replace with actual renewal
	}

	// returns an object containing all teamIDs per projectUser
	function get_team_ids($userName, $userID) {
		global $tokens;

		$teamIDs = array();
		$page = 1;
		$ch = curl_init();
		while (true) { // infinitely loop until all evaluations are fetched
			$headers = array();
			curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/v2/users/".strval($userID)."/projects_users?filter[status]=finished&page[size]=100&page[number]=".$page);
			curl_setopt($ch, CURLOPT_HTTPHEADER, array( "Content-Type: application/json" , "Authorization: Bearer ".$tokens["access_token"] ));
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

			if (!curl_errno($ch)) {
				$info = curl_getinfo($ch);
				if ($info['http_code'] == 200) {
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
					$xTotal = intval($headers["x-total"]);
					$xPage = intval($headers["x-page"]);
					$xPerPage = intval($headers["x-per-page"]);
					$itemsFetched = min($xPerPage * $xPage, $xTotal);
					echo "$userName: teamID fetching: gathered $itemsFetched of $xTotal \n";
					if ($itemsFetched >= $xTotal) {
						break; // we have! quit the infinite loop
					}
					$page++;
					sleep(1); // sleep to prevent 429
				}
				else if ($info['http_code'] == 429) {
					// sleep the requested time to prevent more 429 errors, then try again
					// warning: only does seconds
					$server_time = strtotime($headers["date"]);
					$now = time();
					$elapsed = max($now - $server_time, 0);
					$retry_after = intval($headers["retry-after"]);
					$wait = $retry_after - $elapsed;
					echo "$userName: error 429, waiting $wait seconds...\n";
					sleep($wait);
				}
				else if ($info['http_code'] == 401) {
					echo "$userName: access token expired, refreshing...\n";
					renew_access_tokens();
				}
				else {
					return (false);
				}
			}
			else {
				echo "$userName: curl error: " . curl_error($ch) . "\n";
				return (false);
			}
		}
		curl_close($ch);
		return ($teamIDs);
	}

	function get_outstandings($userName, $userID) {
		global $tokens;

		$retrieveFromTeamIDs = array();
		$teamIDs = get_team_ids($userName, $userID);
		$projectsUserIDs = array_keys($teamIDs);
		if ($teamIDs === false) {
			echo "$userName: error fetching teamIDs\n";
			return (false); // likely an API error
		}
		if (count($projectsUserIDs) == 0) {
			echo "$userName: user has not finished any projects yet\n";
			return (array());
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

		$ch = curl_init();
		$page = 1;
		while (true) { // infinitely loop until all evaluations are fetched
			$headers = array();
			curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/v2/users/".strval($userID)."/scale_teams/as_corrected?page[size]=100&page[number]=".$page);
			curl_setopt($ch, CURLOPT_HTTPHEADER, array( "Content-Type: application/json" , "Authorization: Bearer ".$tokens["access_token"] ));
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

			if (!curl_errno($ch)) {
				$info = curl_getinfo($ch);
				if ($info['http_code'] == 200) {
					try {
						$json = json_decode($response, true);
						foreach ($json as &$eval) {
							// retrieve the projectsUser ID from this evaluation. If we did not wish to retrieve outstanding flags for this projectsUser, continue.
							$projectsUserID = get_project_user_id_from_team_ids($teamIDs, $eval["team"]["id"]);
							if ($projectsUserID === false) {
								continue;
							}
							// echo "$userName: projectsUserID: ".$projectsUserID.", teamID: ".$eval["team"]["id"].", Flag: " . $eval["flag"]["id"] . "\n";
							if ($eval["flag"]["id"] == 9) { // id 9 is the key of an Outstanding flag.
								$teamIDsForProj = &$teamIDs[$projectsUserID];
								$outstandingsForProj = &$outstandings[$projectsUserID];

								if ($eval["team"]["id"] == $teamIDsForProj["current"]) { // this evaluation was done for the current team
									// echo "$userName: Increased CURRENT of " . $projectsUserID . " by one\n";
									$outstandingsForProj["current"]++; // increase its outstanding amount by 1
								}

								if ($eval["team"]["id"] == $teamIDsForProj["best"]) { // this evaluation was done for the team with the highest mark
									// echo "$userName: Increased BEST of " . $projectsUserID . " by one\n";
									$outstandingsForProj["best"]++; // increase its outstanding amount by 1
								}

								$teamIndex = array_search($eval["team"]["id"], $teamIDsForProj["all"]);
								if ($teamIndex !== false) { // team is listed in list of teamIDs for this user's projects
									// echo "$userName: Increased ALL index " . $teamIndex . " (" . $teamIDsForProj["all"][$teamIndex] . ") of " . $projectsUserID . " by one\n";
									$outstandingsForProj["all"][$teamIndex]++; // increase its outstanding amount by 1
								}
							}
						}

						// check if we've gone through all pages
						$xTotal = intval($headers["x-total"]);
						$xPage = intval($headers["x-page"]);
						$xPerPage = intval($headers["x-per-page"]);
						$itemsFetched = min($xPerPage * $xPage, $xTotal);
						echo "$userName: projects: processed $itemsFetched of $xTotal \n";
						if ($itemsFetched >= $xTotal) {
							break; // we have! quit the infinite loop
						}
						$page++;
					}
					catch (Exception $e) {
						echo "$userName: error: " . $e->getMessage() . "\n";
						return (false);
					}
				}
				else if ($info['http_code'] == 429) {
					// sleep the requested time to prevent more 429 errors, then try again
					// warning: only does seconds
					$server_time = strtotime($headers["date"]);
					$now = time();
					$elapsed = max($now - $server_time, 0);
					$retry_after = intval($headers["retry-after"]);
					$wait = $retry_after - $elapsed;
					echo "$userName: error 429, waiting $wait seconds...\n";
					sleep($wait);
				}
				else if ($info['http_code'] == 401) {
					echo "$userName: access token expired, refreshing...\n";
					renew_access_tokens();
				}
				else {
					echo "$userName: response code " . $info['http_code'] . " from Intra API for scale_teams/as_corrected on page $page\n";
					return (false);
				}
			}
			else {
				echo "$userName: curl error: " . curl_error($ch) . "\n";
				return (false);
			}

			// sleep to prevent 429
			sleep(1);
		}
		curl_close($ch);
		echo "$userName: done!\n";
		return ($outstandings);
	}

	$tokens = get_client_tokens();
	if (!$tokens) {
		echo "Unable to fetch client token";
		die();
	}

	$userFiles = glob("../settings/*.json", GLOB_NOSORT);
	shuffle($userFiles);
	if ($userFiles === false) {
		echo "Error fetching user settings files\n";
		die();
	}
	if (empty($userFiles)) {
		echo "No user settings files found\n";
		die();
	}
	$amount = count($userFiles);

	foreach ($userFiles as $i=>$userFile) {
		$login = pathinfo($userFile, PATHINFO_FILENAME);
		if (!is_valid_username($login)) {
			echo "Invalid username $login\n";
			continue;
		}

		$userID = get_user_id($tokens["access_token"], $login);
		if ($userID === false) {
			echo "Unable to fetch userID for user $login\n";
		}
		else if ($userID < 0) {
			echo "User $login not found on Intra\n";
		}
		else {
			echo "Fetching outstandings for $login ($userID) --- ".($i+1)." of $amount users...\n";
			$outstandings = get_outstandings($login, $userID);
			if (!file_put_contents("../db/outstandings/$login.json", json_encode($outstandings, JSON_UNESCAPED_UNICODE))) {
				echo "$login: error writing outstandings to file\n";
			}
			echo "\n";
		}

		// sleep to prevent 429
		sleep(1);
	}
?>
