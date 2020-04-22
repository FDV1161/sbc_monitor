CREATE TABLE sbc(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE logs(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sbc_id INT NOT NULL, 
    date DATETIME NOT NULL,
    type CHAR(32),
    realAddress CHAR(39) NOT NULL, 
    virtualAddress CHAR(39) NOT NULL,
    FOREIGN KEY (sbc_id) REFERENCES sbc (id) 
);




select * from sbc left join lofs on sbc.id = logs.sbc_id group by sbc.id 
select sbc.id, name, type, max(date) from sbc left join logs on sbc.id = logs.sbc_id group by sbc.id, type;


SELECT logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress`, logs.sbc FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date 

SELECT logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress`, logs.sbc_id
FROM logs INNER JOIN (SELECT logs.sbc_id AS sbc_id, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc_id) AS last_connect ON logs.sbc_id = last_connect.sbc_id AND logs.date = last_connect.max_date INNER JOIN sbc ON sbc.id = last_connect.sbc_id


SELECT logs.id, logs.date , logs.type, logs.`realAddress`, logs.`virtualAddress` , logs.sbc_id, sbc.id , sbc.name , sbc.description  
FROM sbc, logs INNER JOIN (SELECT logs.sbc_id AS sbc_id, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc_id) AS last_connect ON logs.sbc_id = last_connect.sbc_id AND logs.date = last_connect.max_date


SELECT logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress`, logs.sbc 
FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date 
INNER JOIN sbc ON sbc.id = logs.sbc


SELECT logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress`, logs.sbc , sbc.id, sbc.name , sbc.description  
FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date INNER JOIN sbc ON sbc.id = logs.sbc


SELECT logs.id, logs.date , logs.type, logs.`realAddress` , logs.`virtualAddress`, logs.sbc , sbc.id, sbc.name , sbc.description 
FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date FULL OUTER JOIN sbc ON sbc.id = logs.sbc


SELECT logs.id , logs.date, logs.type , logs.`realAddress` , logs.`virtualAddress`, logs.sbc , sbc.id , sbc.name , sbc.description 
FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date FULL OUTER JOIN sbc ON sbc.id = last_connect.sbc


SELECT logs.id AS logs_id, logs.date AS logs_date, logs.type AS logs_type, logs.`realAddress` AS `logs_realAddress`, logs.`virtualAddress` AS `logs_virtualAddress`, logs.sbc_id AS logs_sbc_id, sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description 
FROM logs INNER JOIN sbc ON sbc.id = logs.sbc_id INNER JOIN (SELECT logs.sbc_id AS sbc_id, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc_id) AS last_connect ON logs.sbc_id = last_connect.sbc_id AND logs.date = last_connect.max_date INNER JOIN sbc ON sbc.id = last_connect.sbc_id


SELECT sbc.id, sbc.name, sbc.description, logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress`, logs.sbc 
FROM sbc INNER JOIN logs ON sbc.id = logs.sbc INNER JOIN (SELECT logs.sbc AS sbc_id, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date


SELECT sbc.id, sbc.name, sbc.description , logs.id, logs.date , logs.type , logs.`realAddress` , logs.`virtualAddress` , logs.sbc
FROM sbc INNER JOIN logs ON sbc.id = logs.sbc LEFT OUTER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date


SELECT sbc.id, sbc.name, sbc.description, logs.id, logs.date, logs.type , logs.`realAddress`, logs.`virtualAddress`, logs.sbc
FROM sbc LEFT OUTER JOIN logs ON sbc.id = logs.sbc LEFT OUTER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date

SELECT logs.id, logs.date, logs.type, logs.`realAddress`, logs.`virtualAddress` , logs.sbc, sbc.id , sbc.name , sbc.description 
FROM sbc, logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date





SELECT logs.id AS logs_id, logs.date AS logs_date, logs.type AS logs_type, logs.`realAddress` AS `logs_realAddress`, logs.`virtualAddress` AS `logs_virtualAddress`, logs.sbc, sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description 
FROM logs INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date LEFT OUTER JOIN sbc ON sbc.id = last_connect.sbc


SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description 
FROM sbc INNER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc

SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description 
FROM sbc LEFT OUTER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc

SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description, last_connect.sbc, last_connect.max_date AS last_connect_max_date 
FROM sbc LEFT OUTER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc


SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description, last_connect.sbc , last_connect.max_date AS last_connect_max_date 
FROM sbc LEFT OUTER JOIN (SELECT logs.sbc , max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc LEFT OUTER JOIN logs ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date


SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description, last_connect.sbc, last_connect.max_date AS last_connect_max_date, logs.id AS logs_id, logs.date AS logs_date, logs.type AS logs_type, logs.`realAddress` AS `logs_realAddress`, logs.`virtualAddress` AS `logs_virtualAddress`, logs.sbc 
FROM sbc LEFT OUTER JOIN (SELECT logs.sbc , max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc LEFT OUTER JOIN logs ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date



SELECT sbc.id AS sbc_id, sbc.name AS sbc_name, sbc.description AS sbc_description, logs.id AS logs_id, logs.date AS logs_date, logs.type AS logs_type, logs.`realAddress` AS `logs_realAddress`, logs.`virtualAddress` AS `logs_virtualAddress`, logs.sbc 
FROM sbc LEFT OUTER JOIN (SELECT logs.sbc, max(logs.date) AS max_date 
FROM logs GROUP BY logs.sbc) AS last_connect ON sbc.id = last_connect.sbc LEFT OUTER JOIN logs ON logs.sbc = last_connect.sbc AND logs.date = last_connect.max_date