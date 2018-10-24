DROP TABLE IF EXISTS textfiles;
DROP TABLE IF EXISTS model;

CREATE TABLE textfiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT UNIQUE,
  content TEXT
);

CREATE TABLE model (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_topic TEXT,
  topics TEXT,
  doc_similarities TEXT,
  topic_similarities TEXT
);
