<?php
	@session_start();

	// set headers
	header('Content-Type: text/html; charset=utf-8');
	header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
	header("Cache-Control: post-check=0, pre-check=0", false);
	header("Pragma: no-cache");

	// set custom respond function, only for this page
	function respond_auth($type, $msg, $data = null) {
?>
<!DOCTYPE html>
<html>
	<head>
		<meta charset='utf-8' />
		<title>Connect Improved Intra 42 with your Intranet account</title>
		<link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
		<link rel="icon" type="image/ico" href="favicon.ico" />
		<!-- TODO remove below style block, use internal.css -->
		<style>
			html {
				display: block;
				padding: 0px;
				margin: 0px;
				background-color: #202124;
				width: 100%;
				height: 100%;
			}

			body {
				display: block;
				background-color: #292a2d;
				color: #f2f2f2;
				caret-color: #f2f2f2;
				font-family: "Futura PT", "Futura", "Helvetica", Verdana, Arial, Sans-Serif;
				font-size: 16px;
				padding: 0px 16px;
				box-sizing: border-box;
				cursor: default;
				width: 100%;
				height: 100%;
				min-height: 100%;
				min-width: 360px;
				max-width: 540px;
				margin: 0 auto;
				user-select: none;
				box-shadow: 0 0 4px rgba(0,0,0,.14), 0 4px 8px rgba(0,0,0,.28);
			}

			a, a:visited {
				color: #00babc;
				text-decoration: none;
				transition: 0.075s ease-out;
			}

			a:hover, a:focus {
				color: #006e70;
				text-decoration: underline;
				transition: 0s ease-in;
			}

			code {
				display: block;
				white-space: pre-wrap;
				word-break: break-word;
				font-size: smaller;
				padding: 16px 0px;
			}

			h1 {
				margin: 0px;
				padding: 16px 0px;
			}

			details {
				padding: 8px;
				border: 1px solid #4a4a4a;
				background: #3a3a3a;
				border-radius: 4px;
			}

			summary {
				font-size: initial;
			}

			details[open] summary {
				border-bottom: 1px solid #4a4a4a;
				padding-bottom: 8px;
				margin-bottom: 8px;
			}
		</style>
	</head>
	<body>
		<code style="display: none;" id="result"><?php echo json_encode($data, JSON_UNESCAPED_UNICODE); ?></code>
<?php
	switch ($type) {
		case "redirect":
?>
		<h1>Redirecting...</h1>
		<p>If you are not redirected automatically, click here: <a href="<?php echo get_auth_page_url(); ?>" target="_self"><?php echo get_auth_page_url(); ?></a></p>
<?php
			break;
		case "success":
?>
		<h1>Authentication succesful</h1>
		<p>Improved Intra 42 is now connected to your Intranet account.<br><span id="action">You can safely close this tab.</span><br><small id="clicker" style="display: none;">Or click <a id="redir_link" href="#" target="_self">here</a> if you are not being redirected...</small></p>
<?php
			break;
		case "error":
?>
		<h1>An error occurred</h1>
		<p>An error occurred while authorizing with your Intranet 42 account.</p>
		<details>
			<summary><?php echo (!empty($data["auth"]) ? $data["auth"]["error_description"] : $msg); ?></summary>
			<code><?php echo json_encode($data, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT); ?></code>
		</details>
<?php
			break;
	}
?>
	</body>
</html>
<?php
		die();
	}

	// include authorization methods
	require_once("include/auth.php");

	// check code
	if (isset($_GET["code"]) && !empty($_GET["code"])) {
		$res = exchange($_GET["code"], "authorization_code");
		if (empty($res)) {
			http_response_code(503);
			respond_auth("error", "Could not exchange Intra authorization code for access token: service unavailable");
		}
		else {
			if (isset($res["auth"]["error"])) {
				switch ($res["auth"]["error"]) {
					case "invalid_scope":
						http_response_code(400);
						break;
					case "invalid_grant":
						http_response_code(401);
						break;
					case "unsupported_grant_type":
					case "unauthorized_client":
					case "invalid_request":
					case "invalid_client":
					default:
						http_response_code(500);
						break;
				}
				respond_auth("error", $res["auth"]["error"], $res);
			}
			else {
				http_response_code(200);
				respond_auth("success", "Access code retrieved", $res);
			}
		}
	}
	else {
		http_response_code(302);
		header("Location: ".get_auth_page_url());
		respond_auth("redirect", "Redirecting to authorization page... See Location field in header for URL");
	}
?>
