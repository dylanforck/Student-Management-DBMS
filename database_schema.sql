-- Base schema:
CREATE TABLE IF NOT EXISTS user (
  username VARCHAR(32) PRIMARY KEY,
  password VARCHAR(32) NOT NULL,
  role ENUM('admin','user') NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS student (
  id VARCHAR(9) PRIMARY KEY,
  name VARCHAR(32) NOT NULL,
  age INT,
  gender CHAR(1),
  major VARCHAR(32),
  phone VARCHAR(32),
  version INT NOT NULL DEFAULT 1
);
  
CREATE TABLE IF NOT EXISTS course (
  course_id VARCHAR(32) PRIMARY KEY,
  course_name VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS score (
  student_id VARCHAR(9),
  course_id VARCHAR(32),
  score INT,
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);

