CREATE TABLE stock (
    record_id INT NOT NULL AUTO_INCREMENT,
    time DATETIME NOT NULL,
    open FLOAT NOT NULL,
	high FLOAT NOT NULL,
	low FLOAT NOT NULL,
	close FLOAT NOT NULL,
	volume FLOAT NOT NULL,
	symbol VARCHAR(40),
    event_time DATETIME DEFAULT NOW(),
    PRIMARY KEY (record_id)
);

