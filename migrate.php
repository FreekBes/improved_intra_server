<?php
	// get all setting files
	$settingFiles = glob("settings/*.json");

	// create array for all settings
	$allSettings = array();

	// go through all user settings
	foreach ($settingFiles as $settingFile) {
		$userSettings = json_decode(file_get_contents($settingFile), true);
		array_push($allSettings, $userSettings);
	}

	// return all settings
	echo json_encode($allSettings, JSON_UNESCAPED_UNICODE);
?>