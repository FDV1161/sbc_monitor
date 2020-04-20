CREATE TABLE sbc(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE logs(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sbc INT NOT NULL, 
    date DATETIME NOT NULL,
    type CHAR(32),
    realAddress CHAR(39) NOT NULL, 
    virtualAddress CHAR(39) NOT NULL,
    FOREIGN KEY (sbc) REFERENCES sbc (id) 
);
