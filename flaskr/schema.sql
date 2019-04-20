-- instantiates initial sql for this thing

DROP TABLE IF EXISTS user;
CREATE TABLE user (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  u_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP --,
   -- gender TEXT CHECK( gender IN ('M', 'F', 'non binary', 'other') ) DEFAULT 'not specified',
   -- income TEXT CHECK( income IN ('0-25k', '26-50k', '51-75k', '76-100k', '101k+')) DEFAULT 'not specified',
   -- party TEXT CHECK( party IN ('red', 'blue', 'ind', 'other')) DEFAULT 'not specified',
   -- geography TEXT CHECK( geography IN ('west coast', 'east coast', 'midwest', 'south', 'outside territories', 'non-us')) DEFAULT 'not specified'
);

DROP TABLE IF EXISTS question;
CREATE TABLE question (
  question_id INTEGER PRIMARY KEY AUTOINCREMENT,
  text VARCHAR(250) UNIQUE NOT NULL,
  q_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  author_id INTEGER NOT NULL,
  CONSTRAINT user_id_fk_q FOREIGN KEY (author_id) REFERENCES user(id)
);

DROP TABLE IF EXISTS answer;
CREATE TABLE answer (
  answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  text VARCHAR(250) NOT NULL,
  question_id INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  a_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT question_id_fk FOREIGN KEY (question_id) REFERENCES question(id),
  CONSTRAINT user_id_fk_a FOREIGN KEY (author_id) REFERENCES user(id)
);

DROP TABLE IF EXISTS choose;
CREATE TABLE choose (
  user_id INTEGER NOT NULL,
  answer_id INTEGER NOT NULL,
  c_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (answer_id, user_id),
  CONSTRAINT answer_id_fk_c FOREIGN KEY (answer_id) REFERENCES answer(id),
  CONSTRAINT user_id_fk_c FOREIGN KEY (user_id) REFERENCES user(id)
);