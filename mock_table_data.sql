-- 1) Mock students
INSERT INTO student (id, name, age, gender, major, phone) VALUES
  ('100000001', 'Alice Johnson', 19, 'F', 'Computer Science', '555-010-1001'),
  ('100000002', 'Bob Williams',   21, 'M', 'Mathematics',       '555-020-2002'),
  ('100000003', 'Carol Martinez', 20, 'F', 'Biology',           '555-030-3003'),
  ('100000004', 'David Lee',      22, 'M', 'History',           '555-040-4004'),
  ('100000005', 'Eva Brown',      18, 'F', 'English',           '555-050-5005');

-- 2) Mock courses
INSERT INTO course (course_id, course_name) VALUES
  ('CS101',   'Introduction to Computer Science'),
  ('MATH201', 'Calculus I'),
  ('ENG150',  'English Literature');

-- 3) Mock scores 
INSERT INTO score (student_id, course_id, score) VALUES
  ('100000001', 'CS101',   88),
  ('100000001', 'MATH201', 92),
  ('100000002', 'CS101',   75),
  ('100000002', 'ENG150',  85),
  ('100000003', 'MATH201', 78),
  ('100000003', 'ENG150',  83),
  ('100000004', 'CS101',   90),
  ('100000004', 'MATH201', 94),
  ('100000005', 'ENG150',  88);
  