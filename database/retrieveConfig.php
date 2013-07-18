<?php
	$DBUser = '';
	$DBPass = '';
	$DBName = '';

	//instantiate database connection. pray for no errors
	$mysqli = new mysqli('localhost', $DBUser, $DBPass, $DBName);
?>