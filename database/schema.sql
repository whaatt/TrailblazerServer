/* MySQL Database Schema */

CREATE TABLE events (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT, /* EID */
	`session` INT NOT NULL, /* Sequence of Steps */
	`type` VARCHAR(20) NOT NULL, /* Label, Relative, Absolute */
	`time` BIGINT NOT NULL, /* UNIX Time in Milliseconds */
	`content` VARCHAR(140), /* Label Content, 140 Characters */
	`heading` DOUBLE, /* Compass Direction */
	`x` DOUBLE, /* Relative X Coordinate */
	`y` DOUBLE, /* Relative Y Coordinate */
	`absX` DOUBLE, /* Oriented X Coordinate */
	`absY` DOUBLE, /* Oriented Y Coordinate */
	`latitude` DOUBLE, /* GPS Latitude */
	`longitude` DOUBLE, /* GPS Longitude */
	`accuracy` FLOAT /* GPS Accuracy */
);

CREATE TABLE sessions (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT, /* SID */
	`client` CHAR(128) NOT NULL, /* Client Device ID */
	`location` VARCHAR(140) NOT NULL, /* Location, 140 Characters */
	`floor` VARCHAR(140) NOT NULL, /* Current Floor, 140 Characters */
	`start` VARCHAR(140) NOT NULL, /* Starting Location, 140 Characters */
	`a` FLOAT NOT NULL, /* Alpha, Calibration Parameter */
	`peak` FLOAT NOT NULL, /* Peak, Calibration Parameter */
	`timeout` INT NOT NULL, /* Step Timeout, Calibration Setting */
	`stride` FLOAT NOT NULL /* Stride Length, Calibration Setting */
);