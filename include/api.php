<?php
	require_once("nogit.php");

	function token_expired($createdAt, $expiresIn) {
		// 7200 seconds less: say it expired 2 hours in advance.
		// For just in case Intra API f*cked up the timezones and $createdAt is not UTC.
		return ($createdAt + $expiresIn < time() - 7200);
	}

	function get_client_tokens() {
		global $internalClientID, $internalClientSecret;

		$ch = curl_init();
		$postData = array(
			"client_id" => $internalClientID,
			"client_secret" => $internalClientSecret,
			"grant_type" => "client_credentials"
		);
		curl_setopt($ch, CURLOPT_URL,"https://api.intra.42.fr/oauth/token");
		curl_setopt($ch, CURLOPT_POST, true);
		curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
		curl_setopt($ch, CURLOPT_TIMEOUT, 10);
		$response = curl_exec($ch);

		if ($response !== false) {
			try {
				$json = json_decode($response, true);
				if (array_key_exists("error", $json)) {
					return (null);
				}
				return ($json);
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
		if (preg_match('/[^a-z0-9\-]/', $username)) {
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

		if (!curl_errno($ch)) {
			$info = curl_getinfo($ch);
			if ($info['http_code'] == 200) {
				try {
					$json = json_decode($response, true);
					if (empty($json))
						return (false);
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
			else if ($info['http_code'] == 429) {
				sleep(1);
				return get_user_id($token, $login);
			}
			else {
				// TODO 401 error
				return (false);
			}
		}
		return (false);
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
