-- instantiates initial sql for this thing

DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

DROP TABLE IF EXISTS question;
CREATE TABLE question (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question VARCHAR(250) NOT NULL,
  author_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) references user(id)
);

DROP TABLE IF EXISTS answer;
CREATE TABLE answer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  answer VARCHAR(250) NOT NULL,
  question_id INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  FOREIGN KEY (question_id) references user(id),
  FOREIGN KEY (author_id) references user(id)
);

DROP TABLE IF EXISTS vote;
CREATE TABLE vote (
  user_id INTEGER NOT NULL,
  answer_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) references user(id),
  FOREIGN KEY (answer_id) references answer(id)
);