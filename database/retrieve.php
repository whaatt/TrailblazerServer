<?php
	require_once 'retrieveConfig.php'; //get DB stuff ready
	if (!isset($_POST['query'])) { exit(); }
	else { $query = stripslashes($_POST['query']); }
	
	function cast($parameter, $key){
		$floats = array('accuracy', 'a', 'peak', 'timeout', 'stride');
		$doubles = array('heading', 'x', 'y', 'absX', 'absY', 'latitude', 'longitude');
		$ints = array('id', 'session', 'time');
		
		if (in_array($key, $floats)){
			return (float) $parameter;
		}
		
		if (in_array($key, $doubles)){
			return (double) $parameter;
		}
		
		if (in_array($key, $ints)){
			return (int) $parameter;
		}
		
		return $parameter;
	}
	
	$result = $mysqli->query($query) or trigger_error($mysqli->error."[$sql]");
	$JSONArray = array();
	
	while($row = $result->fetch_assoc()){
		//remove null values
		$row = array_filter($row, 'strlen');
		
		foreach ($row as $key => $parameter){
			$row[$key] = cast($parameter, $key);
		} 
		
		//add to output
		$JSONArray[] = $row;
	}
	
	$result->free();
	$mysqli->close();
	
	//output the JSON array
	echo json_encode($JSONArray);
?>