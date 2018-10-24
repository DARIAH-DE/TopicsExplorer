DROP TABLE IF EXISTS textfiles;
DROP TABLE IF EXISTS model;

CREATE TABLE textfiles (
  id INTEGER PRIMARY KEY,
  title TEXT UNIQUE,
  content TEXT
);

CREATE TABLE model (
  id INTEGER PRIMARY KEY,
  doc_topic TEXT,
  topics TEXT,
  doc_sim TEXT,
  topic_sim TEXT
);
