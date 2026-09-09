

-- Bài nộp
ALTER TABLE submissions DROP CONSTRAINT submissions_exam_id_fkey;
ALTER TABLE submissions ADD CONSTRAINT submissions_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE;

ALTER TABLE submissions DROP CONSTRAINT submissions_student_id_fkey;
ALTER TABLE submissions ADD CONSTRAINT submissions_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Điểm
ALTER TABLE grades DROP CONSTRAINT grades_submission_id_fkey;
ALTER TABLE grades ADD CONSTRAINT grades_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE;

-- Kết quả
ALTER TABLE results DROP CONSTRAINT results_student_id_fkey;
ALTER TABLE results ADD CONSTRAINT results_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE results DROP CONSTRAINT results_exam_id_fkey;
ALTER TABLE results ADD CONSTRAINT results_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE;

ALTER TABLE results DROP CONSTRAINT results_grade_id_fkey;
ALTER TABLE results ADD CONSTRAINT results_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE;

-- Kết quả chấm điểm
ALTER TABLE grading_results DROP CONSTRAINT grading_results_submission_id_fkey;
ALTER TABLE grading_results ADD CONSTRAINT grading_results_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE;
