DROP TABLE IF EXISTS textfiles;
DROP TABLE IF EXISTS stopwords;
DROP TABLE IF EXISTS model;

CREATE TABLE textfiles (
  id INTEGER PRIMARY KEY,
  title TEXT,
  content TEXT
);

CREATE TABLE stopwords (
  id INTEGER PRIMARY KEY,
  content TEXT
);

CREATE TABLE model (
  id INTEGER PRIMARY KEY,
  document_topic TEXT,
  topics TEXT,
  document_similarities TEXT,
  topic_similarities TEXT
);