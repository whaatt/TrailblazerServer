<?php
	$value = json_decode(file_get_contents('php://input'));
	var_dump($value);
	
	$last = substr((file_get_contents('output.txt')), 0, -1);
	
	if ($value != null){
		if ($last == '['){
			file_put_contents('output.txt', json_encode(json_decode(last . json_encode($value) . ']')));
		}
		
		else{
			file_put_contents('output.txt', json_encode(json_decode($last . ',' . json_encode($value) . ']')));
		}
	}
?>