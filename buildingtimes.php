<?php
	require_once("include/respond.php");

	http_response_code(503);
	respond("error", "Service Unavailable");
?>
