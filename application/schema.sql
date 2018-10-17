DROP TABLE IF EXISTS textfiles;
DROP TABLE IF EXISTS model;

CREATE TABLE textfiles (
  title TEXT UNIQUE NOT NULL,
  text TEXT NOT NULL
);

CREATE TABLE model (
  doc_topic TEXT NOT NULL,
  topics TEXT NOT NULL
);
