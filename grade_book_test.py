

import unittest
from grade_book import (
    Assignment, Course, Student, GradeBook,
    Category, CATEGORY_WEIGHTS, GPA_MAP
)




class TestAssignment(unittest.TestCase):


    def test_percentage_normal(self):
        a = Assignment("HW1", 18, 20, Category.HOMEWORK)
        self.assertAlmostEqual(a.percentage, 90.0)


    def test_percentage_full_marks(self):
        a = Assignment("Quiz1", 15, 15, Category.QUIZZES)
        self.assertAlmostEqual(a.percentage, 100.0)


    def test_percentage_zero_earned(self):
        a = Assignment("HW1", 0, 20, Category.HOMEWORK)
        self.assertAlmostEqual(a.percentage, 0.0)


    def test_percentage_zero_possible(self):
        a = Assignment("HW1", 10, 0, Category.HOMEWORK)
        self.assertAlmostEqual(a.percentage, 0.0)




class TestCourse(unittest.TestCase):


    def setUp(self):
        self.course = Course("Calculus II", 3)
        self.course.assignments = [
            Assignment("HW1",   18, 20, Category.HOMEWORK),
            Assignment("HW2",   16, 20, Category.HOMEWORK),
            Assignment("Quiz1", 14, 15, Category.QUIZZES),
            Assignment("Final", 92, 100, Category.FINAL_EXAM),
        ]


    def test_assignments_by_category_homework(self):
        result = self.course.assignments_by_category(Category.HOMEWORK)
        self.assertEqual(len(result), 2)


    def test_assignments_by_category_empty(self):
        result = self.course.assignments_by_category(Category.MIDTERM)
        self.assertEqual(result, [])


    def test_assignments_by_category_single(self):
        result = self.course.assignments_by_category(Category.QUIZZES)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Quiz1")




class TestGradeBookAddStudent(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()


    def test_add_student(self):
        self.gb.add_student("S001", "Saurabh Sharma")
        self.assertIn("S001", self.gb._students)


    def test_add_duplicate_student_raises(self):
        self.gb.add_student("S001", "Saurabh Sharma")
        with self.assertRaises(ValueError):
            self.gb.add_student("S001", "Saurabh Sharma")


    def test_student_name_stored(self):
        self.gb.add_student("S001", "Nidhi Verma")
        self.assertEqual(self.gb._students["S001"].name, "Nidhi Verma")




class TestGradeBookEnrollment(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Saurabh Sharma")


    def test_enroll_in_course(self):
        self.gb.enroll_in_course("S001", "Calculus II", 3)
        self.assertIn("Calculus II", self.gb._students["S001"].courses)


    def test_enroll_duplicate_raises(self):
        self.gb.enroll_in_course("S001", "Calculus II", 3)
        with self.assertRaises(ValueError):
            self.gb.enroll_in_course("S001", "Calculus II", 3)


    def test_enroll_unknown_student_raises(self):
        with self.assertRaises(KeyError):
            self.gb.enroll_in_course("S999", "Calculus II", 3)


    def test_credit_hours_stored(self):
        self.gb.enroll_in_course("S001", "Physics I", 4)
        self.assertEqual(self.gb._students["S001"].courses["Physics I"].credit_hours, 4)




class TestGradeBookAddAssignment(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Saurabh Sharma")
        self.gb.enroll_in_course("S001", "Calculus II", 3)


    def test_add_assignment(self):
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("HW1", 18, 20, Category.HOMEWORK))
        course = self.gb._students["S001"].courses["Calculus II"]
        self.assertEqual(len(course.assignments), 1)


    def test_add_multiple_assignments(self):
        for name, earned in [("HW1", 18), ("HW2", 16), ("HW3", 19)]:
            self.gb.add_assignment("S001", "Calculus II",
                                   Assignment(name, earned, 20, Category.HOMEWORK))
        course = self.gb._students["S001"].courses["Calculus II"]
        self.assertEqual(len(course.assignments), 3)


    def test_add_assignment_unknown_course_raises(self):
        with self.assertRaises(KeyError):
            self.gb.add_assignment("S001", "Physics I",
                                   Assignment("HW1", 18, 20, Category.HOMEWORK))




class TestGetCategoryAverage(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Saurabh Sharma")
        self.gb.enroll_in_course("S001", "Calculus II", 3)


    def test_average_single_assignment(self):
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("HW1", 18, 20, Category.HOMEWORK))
        avg = self.gb.get_category_average("S001", "Calculus II", Category.HOMEWORK)
        self.assertAlmostEqual(avg, 90.0)


    def test_average_multiple_assignments(self):
        for name, earned, possible in [("HW1", 18, 20), ("HW2", 16, 20), ("HW3", 19, 20)]:
            self.gb.add_assignment("S001", "Calculus II",
                                   Assignment(name, earned, possible, Category.HOMEWORK))
        avg = self.gb.get_category_average("S001", "Calculus II", Category.HOMEWORK)
        self.assertAlmostEqual(avg, 88.333, places=2)


    def test_average_no_assignments_returns_none(self):
        avg = self.gb.get_category_average("S001", "Calculus II", Category.MIDTERM)
        self.assertIsNone(avg)


    def test_average_perfect_score(self):
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Quiz1", 15, 15, Category.QUIZZES))
        avg = self.gb.get_category_average("S001", "Calculus II", Category.QUIZZES)
        self.assertAlmostEqual(avg, 100.0)




class TestGetCourseGrade(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Saurabh Sharma")
        self.gb.enroll_in_course("S001", "Calculus II", 3)


    def _add_full_course(self):
        for name, earned, possible in [("HW1", 18, 20), ("HW2", 16, 20), ("HW3", 19, 20)]:
            self.gb.add_assignment("S001", "Calculus II",
                                   Assignment(name, earned, possible, Category.HOMEWORK))
        for name, earned, possible in [("Quiz1", 14, 15), ("Quiz2", 13, 15)]:
            self.gb.add_assignment("S001", "Calculus II",
                                   Assignment(name, earned, possible, Category.QUIZZES))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Midterm",    88, 100, Category.MIDTERM))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Final Exam", 92, 100, Category.FINAL_EXAM))


    def test_course_grade_percentage(self):
        self._add_full_course()
        pct, _ = self.gb.get_course_grade("S001", "Calculus II")
        self.assertAlmostEqual(pct, 89.87, places=1)


    def test_course_grade_letter_B(self):
        self._add_full_course()
        _, letter = self.gb.get_course_grade("S001", "Calculus II")
        self.assertEqual(letter, "B")


    def test_course_grade_letter_A(self):
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Final Exam", 97, 100, Category.FINAL_EXAM))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Midterm",    95, 100, Category.MIDTERM))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("HW1",        20,  20, Category.HOMEWORK))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Quiz1",      15,  15, Category.QUIZZES))
        _, letter = self.gb.get_course_grade("S001", "Calculus II")
        self.assertEqual(letter, "A")


    def test_course_grade_letter_F(self):
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Final Exam", 50, 100, Category.FINAL_EXAM))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Midterm",    40, 100, Category.MIDTERM))
        _, letter = self.gb.get_course_grade("S001", "Calculus II")
        self.assertEqual(letter, "F")


    def test_missing_category_excluded(self):
        # only HOMEWORK and FINAL_EXAM — QUIZZES and MIDTERM excluded
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("HW1",        80, 100, Category.HOMEWORK))
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Final Exam", 80, 100, Category.FINAL_EXAM))
        pct, _ = self.gb.get_course_grade("S001", "Calculus II")
        # active_weight = 0.20 + 0.35 = 0.55; weighted = 80*0.20 + 80*0.35 = 44; 44/0.55 = 80
        self.assertAlmostEqual(pct, 80.0)


    def test_no_assignments_returns_zero(self):
        pct, letter = self.gb.get_course_grade("S001", "Calculus II")
        self.assertEqual(pct, 0.0)
        self.assertEqual(letter, "F")




class TestLetterGrades(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Nidhi Verma")
        self.gb.enroll_in_course("S001", "Test Course", 3)


    def _set_final_only(self, score):
        self.gb.add_assignment("S001", "Test Course",
                               Assignment("Final", score, 100, Category.FINAL_EXAM))


    def test_boundary_A(self):
        self._set_final_only(90)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "A")


    def test_boundary_B(self):
        self._set_final_only(80)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "B")


    def test_boundary_C(self):
        self._set_final_only(70)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "C")


    def test_boundary_D(self):
        self._set_final_only(60)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "D")


    def test_boundary_F(self):
        self._set_final_only(59)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "F")


    def test_just_below_A(self):
        self._set_final_only(89)
        _, letter = self.gb.get_course_grade("S001", "Test Course")
        self.assertEqual(letter, "B")




class TestCalculateGPA(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Sasan Mehta")


    def test_single_course_A(self):
        self.gb.enroll_in_course("S001", "CS101", 3)
        self.gb.add_assignment("S001", "CS101",
                               Assignment("Final", 95, 100, Category.FINAL_EXAM))
        gpa = self.gb.calculate_gpa("S001")
        self.assertEqual(gpa, 4.0)


    def test_single_course_F(self):
        self.gb.enroll_in_course("S001", "Statistics", 3)
        self.gb.add_assignment("S001", "Statistics",
                               Assignment("Final", 50, 100, Category.FINAL_EXAM))
        gpa = self.gb.calculate_gpa("S001")
        self.assertEqual(gpa, 0.0)


    def test_weighted_gpa_different_credits(self):
        # Course 1: A (4.0), 3 credits
        # Course 2: C (2.0), 4 credits
        # GPA = (4.0*3 + 2.0*4) / 7 = 20/7 = 2.86
        self.gb.enroll_in_course("S001", "Course A", 3)
        self.gb.enroll_in_course("S001", "Course B", 4)


        self.gb.add_assignment("S001", "Course A",
                               Assignment("Final", 95, 100, Category.FINAL_EXAM))
        self.gb.add_assignment("S001", "Course B",
                               Assignment("Final", 72, 100, Category.FINAL_EXAM))


        gpa = self.gb.calculate_gpa("S001")
        self.assertAlmostEqual(gpa, round((4.0 * 3 + 2.0 * 4) / 7, 2))


    def test_no_courses_returns_zero(self):
        gpa = self.gb.calculate_gpa("S001")
        self.assertEqual(gpa, 0.0)




class TestGenerateTranscript(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Saurabh Sharma")
        self.gb.enroll_in_course("S001", "Calculus II", 3)
        self.gb.add_assignment("S001", "Calculus II",
                               Assignment("Final Exam", 92, 100, Category.FINAL_EXAM))


    def test_transcript_contains_student_name(self):
        transcript = self.gb.generate_transcript("S001")
        self.assertIn("Saurabh Sharma", transcript)


    def test_transcript_contains_student_id(self):
        transcript = self.gb.generate_transcript("S001")
        self.assertIn("S001", transcript)


    def test_transcript_contains_course_name(self):
        transcript = self.gb.generate_transcript("S001")
        self.assertIn("Calculus II", transcript)


    def test_transcript_contains_credits(self):
        transcript = self.gb.generate_transcript("S001")
        self.assertIn("credits", transcript)


    def test_transcript_contains_gpa(self):
        transcript = self.gb.generate_transcript("S001")
        self.assertIn("Cumulative GPA", transcript)


    def test_transcript_contains_all_categories(self):
        transcript = self.gb.generate_transcript("S001")
        for category in Category:
            self.assertIn(category.value, transcript)


    def test_transcript_unknown_student_raises(self):
        with self.assertRaises(KeyError):
            self.gb.generate_transcript("S999")




class TestEdgeCases(unittest.TestCase):


    def setUp(self):
        self.gb = GradeBook()
        self.gb.add_student("S001", "Nidhi Verma")
        self.gb.enroll_in_course("S001", "Maths", 3)


    def test_zero_points_earned(self):
        self.gb.add_assignment("S001", "Maths",
                               Assignment("HW1", 0, 20, Category.HOMEWORK))
        avg = self.gb.get_category_average("S001", "Maths", Category.HOMEWORK)
        self.assertAlmostEqual(avg, 0.0)


    def test_multiple_categories_partial(self):
        self.gb.add_assignment("S001", "Maths",
                               Assignment("Midterm",    80, 100, Category.MIDTERM))
        self.gb.add_assignment("S001", "Maths",
                               Assignment("Final Exam", 80, 100, Category.FINAL_EXAM))
        pct, _ = self.gb.get_course_grade("S001", "Maths")
        # active_weight = 0.25 + 0.35 = 0.60; weighted = 80*0.25 + 80*0.35 = 48; 48/0.60 = 80
        self.assertAlmostEqual(pct, 80.0)


    def test_add_get_unknown_student_raises(self):
        with self.assertRaises(KeyError):
            self.gb.get_category_average("S999", "Maths", Category.HOMEWORK)


    def test_add_get_unknown_course_raises(self):
        with self.assertRaises(KeyError):
            self.gb.get_category_average("S001", "Physics", Category.HOMEWORK)




if __name__ == "__main__":
    unittest.main(verbosity=2)