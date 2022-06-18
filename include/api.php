<?php
	require_once("nogit.php");

	// obtain shared memory space
	$shm = shm_attach(43);

	function token_expired($createdAt, $expiresIn) {
		// 7200 seconds less: say it expired 2 hours in advance.
		// For just in case Intra API f*cked up the timezones and $createdAt is not UTC.
		return ($createdAt + $expiresIn >= time() - 7200);
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
?>
