DROP TABLE IF EXISTS textfiles;
DROP TABLE IF EXISTS token_freqs;
DROP TABLE IF EXISTS stopwords;
DROP TABLE IF EXISTS parameter;
DROP TABLE IF EXISTS model;


CREATE TABLE textfiles (
  id INTEGER PRIMARY KEY,
  title TEXT,
  content TEXT
);

CREATE TABLE token_freqs (
  id INTEGER PRIMARY KEY,
  content TEXT
);

CREATE TABLE stopwords (
  id INTEGER PRIMARY KEY,
  content TEXT
);

CREATE TABLE parameter (
  id INTEGER PRIMARY KEY
);

CREATE TABLE model (
  id INTEGER PRIMARY KEY,
  document_topic TEXT,
  topics TEXT,
  document_similarities TEXT,
  topic_similarities TEXT
);