DROP TABLE IF EXISTS posts;

CREATE TABLE posts
(ID INTEGER PRIMARY KEY,
title VARCHAR NOT NULL,
published VARCHAR NOT NULL,
author VARCHAR NOT NULL,
comments VARCHAR NOT NULL);

