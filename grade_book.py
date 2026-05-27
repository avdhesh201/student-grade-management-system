

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum




class Category(Enum):
    HOMEWORK   = "HOMEWORK"
    QUIZZES    = "QUIZZES"
    MIDTERM    = "MIDTERM"
    FINAL_EXAM = "FINAL_EXAM"




CATEGORY_WEIGHTS: dict[Category, float] = {
    Category.HOMEWORK:   0.20,
    Category.QUIZZES:    0.20,
    Category.MIDTERM:    0.25,
    Category.FINAL_EXAM: 0.35,
}


LETTER_THRESHOLDS: list[tuple[float, str]] = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    ( 0, "F"),
]


GPA_MAP: dict[str, float] = {
    "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0
}




@dataclass
class Assignment:
    name:            str
    points_earned:   float
    points_possible: float
    category:        Category


    @property
    def percentage(self) -> float:
        if self.points_possible == 0:
            return 0.0
        return (self.points_earned / self.points_possible) * 100




@dataclass
class Course:
    course_name:  str
    credit_hours: int
    assignments:  list[Assignment] = field(default_factory=list)


    def assignments_by_category(self, category: Category) -> list[Assignment]:
        return [a for a in self.assignments if a.category == category]




@dataclass
class Student:
    student_id: str
    name:       str
    courses:    dict[str, Course] = field(default_factory=dict)




class GradeBook:
    def __init__(self):
        self._students: dict[str, Student] = {}


    # mutations


    def add_student(self, student_id: str, name: str) -> None:
        if student_id in self._students:
            raise ValueError(f"Student '{student_id}' already exists.")
        self._students[student_id] = Student(student_id=student_id, name=name)


    def enroll_in_course(self, student_id: str, course_name: str, credit_hours: int) -> None:
        student = self._get_student(student_id)
        if course_name in student.courses:
            raise ValueError(f"'{student.name}' is already enrolled in '{course_name}'.")
        student.courses[course_name] = Course(course_name=course_name, credit_hours=credit_hours)


    def add_assignment(self, student_id: str, course_name: str, assignment: Assignment) -> None:
        course = self._get_course(student_id, course_name)
        course.assignments.append(assignment)


    # queries


    def get_category_average(self, student_id: str, course_name: str,
                              category: Category) -> Optional[float]:
        course = self._get_course(student_id, course_name)
        items = course.assignments_by_category(category)
        if not items:
            return None
        return sum(a.percentage for a in items) / len(items)


    def get_course_grade(self, student_id: str, course_name: str) -> tuple[float, str]:
        weighted_total = 0.0
        active_weight  = 0.0


        for category, weight in CATEGORY_WEIGHTS.items():
            avg = self.get_category_average(student_id, course_name, category)
            if avg is not None:
                weighted_total += avg * weight
                active_weight  += weight


        percentage = (weighted_total / active_weight) if active_weight else 0.0
        return percentage, self._letter_grade(percentage)


    def calculate_gpa(self, student_id: str) -> float:
        student = self._get_student(student_id)
        total_points  = 0.0
        total_credits = 0


        for course_name, course in student.courses.items():
            _, letter = self.get_course_grade(student_id, course_name)
            total_points  += GPA_MAP[letter] * course.credit_hours
            total_credits += course.credit_hours


        return round(total_points / total_credits, 2) if total_credits else 0.0


    def generate_transcript(self, student_id: str) -> str:
        student = self._get_student(student_id)
        lines: list[str] = []


        lines.append("=" * 62)
        lines.append(f"  OFFICIAL TRANSCRIPT")
        lines.append(f"  Student : {student.name}")
        lines.append(f"  ID      : {student.student_id}")
        lines.append("=" * 62)


        for course_name, course in student.courses.items():
            pct, letter = self.get_course_grade(student_id, course_name)
            lines.append(f"\n  Course  : {course_name}  ({course.credit_hours} credits)")
            lines.append(f"  Grade   : {letter}  ({pct:.2f}%)")
            lines.append(f"  {'Category':<14} {'Avg':>7}   Assignments")
            lines.append(f"  {'-'*52}")


            for category in Category:
                avg   = self.get_category_average(student_id, course_name, category)
                items = course.assignments_by_category(category)
                w     = int(CATEGORY_WEIGHTS[category] * 100)


                avg_str = f"{avg:6.2f}%" if avg is not None else "  N/A "
                detail  = ", ".join(
                    f"{a.name} ({a.points_earned}/{a.points_possible})" for a in items
                ) or "—"
                lines.append(f"  {category.value:<14} {avg_str}   [{w}%]  {detail}")


        gpa = self.calculate_gpa(student_id)
        lines.append("\n" + "=" * 62)
        lines.append(f"  Cumulative GPA : {gpa:.2f}")
        lines.append("=" * 62)
        return "\n".join(lines)


    # private helpers


    def _get_student(self, student_id: str) -> Student:
        if student_id not in self._students:
            raise KeyError(f"Student '{student_id}' not found.")
        return self._students[student_id]


    def _get_course(self, student_id: str, course_name: str) -> Course:
        student = self._get_student(student_id)
        if course_name not in student.courses:
            raise KeyError(f"Course '{course_name}' not found for student '{student_id}'.")
        return student.courses[course_name]


    @staticmethod
    def _letter_grade(percentage: float) -> str:
        for threshold, letter in LETTER_THRESHOLDS:
            if percentage >= threshold:
                return letter
        return "F"




def demo() -> None:
    gb = GradeBook()


    gb.add_student("S001", "Saurabh Sharma")
    gb.add_student("S002", "Sasan Mehta")
    gb.add_student("S003", "Nidhi Verma")


    # Saurabh: Calculus II + Physics I
    gb.enroll_in_course("S001", "Calculus II", 3)
    gb.enroll_in_course("S001", "Physics I",   4)


    for name, earned, possible in [("HW1", 18, 20), ("HW2", 16, 20), ("HW3", 19, 20)]:
        gb.add_assignment("S001", "Calculus II", Assignment(name, earned, possible, Category.HOMEWORK))


    for name, earned, possible in [("Quiz1", 14, 15), ("Quiz2", 13, 15)]:
        gb.add_assignment("S001", "Calculus II", Assignment(name, earned, possible, Category.QUIZZES))


    gb.add_assignment("S001", "Calculus II", Assignment("Midterm",    88, 100, Category.MIDTERM))
    gb.add_assignment("S001", "Calculus II", Assignment("Final Exam", 92, 100, Category.FINAL_EXAM))


    for name, earned, possible in [("HW1", 15, 20), ("HW2", 17, 20)]:
        gb.add_assignment("S001", "Physics I", Assignment(name, earned, possible, Category.HOMEWORK))


    gb.add_assignment("S001", "Physics I", Assignment("Quiz1",      11,  15, Category.QUIZZES))
    gb.add_assignment("S001", "Physics I", Assignment("Midterm",    78, 100, Category.MIDTERM))
    gb.add_assignment("S001", "Physics I", Assignment("Final Exam", 82, 100, Category.FINAL_EXAM))


    # Sasan: English Comp + History + CS101
    gb.enroll_in_course("S002", "English Comp", 3)
    gb.enroll_in_course("S002", "History",      3)
    gb.enroll_in_course("S002", "CS101",        3)


    for name, earned, possible in [("Essay1", 17, 20), ("Essay2", 15, 20), ("Essay3", 18, 20)]:
        gb.add_assignment("S002", "English Comp", Assignment(name, earned, possible, Category.HOMEWORK))


    for name, earned, possible in [("Quiz1", 8, 10), ("Quiz2", 9, 10)]:
        gb.add_assignment("S002", "English Comp", Assignment(name, earned, possible, Category.QUIZZES))


    gb.add_assignment("S002", "English Comp", Assignment("Midterm Essay", 74, 100, Category.MIDTERM))
    gb.add_assignment("S002", "English Comp", Assignment("Final Essay",   79, 100, Category.FINAL_EXAM))


    # History has no quizzes - category excluded from calculation
    for name, earned, possible in [("HW1", 14, 20), ("HW2", 16, 20)]:
        gb.add_assignment("S002", "History", Assignment(name, earned, possible, Category.HOMEWORK))


    gb.add_assignment("S002", "History", Assignment("Midterm",    65, 100, Category.MIDTERM))
    gb.add_assignment("S002", "History", Assignment("Final Exam", 70, 100, Category.FINAL_EXAM))


    for name, earned, possible in [("HW1", 20, 20), ("HW2", 19, 20), ("HW3", 18, 20)]:
        gb.add_assignment("S002", "CS101", Assignment(name, earned, possible, Category.HOMEWORK))


    for name, earned, possible in [("Quiz1", 15, 15), ("Quiz2", 14, 15), ("Quiz3", 13, 15)]:
        gb.add_assignment("S002", "CS101", Assignment(name, earned, possible, Category.QUIZZES))


    gb.add_assignment("S002", "CS101", Assignment("Midterm",    95, 100, Category.MIDTERM))
    gb.add_assignment("S002", "CS101", Assignment("Final Exam", 97, 100, Category.FINAL_EXAM))


    # Nidhi: Statistics + Chemistry
    gb.enroll_in_course("S003", "Statistics", 3)
    gb.enroll_in_course("S003", "Chemistry",  4)


    for name, earned, possible in [("HW1", 10, 20), ("HW2", 12, 20)]:
        gb.add_assignment("S003", "Statistics", Assignment(name, earned, possible, Category.HOMEWORK))


    gb.add_assignment("S003", "Statistics", Assignment("Quiz1",      9,  15, Category.QUIZZES))
    gb.add_assignment("S003", "Statistics", Assignment("Midterm",   59, 100, Category.MIDTERM))
    gb.add_assignment("S003", "Statistics", Assignment("Final Exam",62, 100, Category.FINAL_EXAM))


    for name, earned, possible in [("Lab1", 18, 20), ("Lab2", 17, 20), ("Lab3", 19, 20)]:
        gb.add_assignment("S003", "Chemistry", Assignment(name, earned, possible, Category.HOMEWORK))


    for name, earned, possible in [("Quiz1", 13, 15), ("Quiz2", 12, 15)]:
        gb.add_assignment("S003", "Chemistry", Assignment(name, earned, possible, Category.QUIZZES))


    gb.add_assignment("S003", "Chemistry", Assignment("Midterm",    83, 100, Category.MIDTERM))
    gb.add_assignment("S003", "Chemistry", Assignment("Final Exam", 86, 100, Category.FINAL_EXAM))


    for sid in ["S001", "S002", "S003"]:
        print(gb.generate_transcript(sid))
        print()




if __name__ == "__main__":
    demo()
