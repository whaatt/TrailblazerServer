<?php
	require_once 'storeConfig.php'; //get DB stuff ready
	$trials = json_decode(file_get_contents('php://input'));
	var_dump($trials); //spit input back to phone
	
	function hasProps($object, $properties){
		foreach ($properties as $property){
			if (!property_exists($object, $property)){
				return false;
			}
		}
		
		return true;
	}
	
	foreach ($trials as $session){
		$tableData = DB::queryFirstRow("SHOW TABLE STATUS LIKE %s", 'sessions');
		$sessionID = $tableData['Auto_increment']; //next session ID
		
		//valid-formed events will have certain properties, which are listed here
		$startProps = array('type', 'client', 'location', 'floor', 'start', 'calibration');
		$calibProps = array('a', 'peak', 'timeout', 'stride');
		$stepsProps = array('type', 'x', 'y', 'absX', 'absY', 'time', 'heading');
		$locatProps = array('type', 'latitude', 'longitude', 'heading', 'time', 'accuracy');
		$labelProps = array('type', 'content', 'time');
		
		if ((!property_exists($session[0], 'type')) or ($session[0]->type != 'start')){
			continue; //not a validly formed session
		}
		
		if ((!hasProps($session[0], $startProps)) or (!hasProps($session[0]->calibration, $calibProps))){
			continue; //does not have all parameters
		}
		
		DB::insert('sessions', array(
			'client' => $session[0]->client,
			'location' => $session[0]->location,
			'floor' => $session[0]->floor,
			'start' => $session[0]->start,
			'a' => $session[0]->calibration->a,
			'peak' => $session[0]->calibration->peak,
			'timeout' => $session[0]->calibration->timeout,
			'stride' => $session[0]->calibration->stride
		));
		
		foreach ($session as $event){
			if (!property_exists($event, 'type')){
				continue; //must have type field
			}
			
			if ($event->type == 'start'){
				continue; //only one of these
			}
			
			//insert step information
			else if ($event->type == 'relative'){
				if (hasProps($event, $stepsProps)){
					DB::insert('events', array(
						'session' => $sessionID,
						'type' => $event->type,
						'time' => $event->time,
						'x' => $event->x,
						'y' => $event->y,
						'absX' => $event->absX,
						'absY' => $event->absY,
						'heading' => $event->heading
					));
				}
			}
			
			//insert GPS location
			else if ($event->type == 'absolute'){
				if (hasProps($event, $locatProps)){
					DB::insert('events', array(
						'session' => $sessionID,
						'type' => $event->type,
						'time' => $event->time,
						'latitude' => $event->latitude,
						'longitude' => $event->longitude,
						'accuracy' => $event->accuracy,
						'heading' => $event->heading
					));
				}
			}
			
			//insert label annotation
			else if ($event->type == 'label'){
				if (hasProps($event, $labelProps)){
					DB::insert('events', array(
						'session' => $sessionID,
						'type' => $event->type,
						'time' => $event->time,
						'content' => $event->content
					));
				}
			}
		}
	}
?>