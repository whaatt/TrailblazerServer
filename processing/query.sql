SELECT * FROM `events` LEFT JOIN `sessions` ON `events`.session = `sessions`.id WHERE `sessions`.location = '@1' ORDER BY `time` ASC;