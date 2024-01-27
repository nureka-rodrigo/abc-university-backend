from django.contrib.auth.models import AbstractUser
from django.db import models


def upload_to(instance, filename):
    return 'users/{filename}'.format(filename=filename)


# User modal
class User(AbstractUser):
    username = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    image = models.ImageField("Image", upload_to=upload_to, default='anonymous/anonymous.jpg')

    last_login = None
    is_superuser = None
    is_staff = None
    date_joined = None
    email = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [username, password, role]


# Semester modal
class Semester(models.Model):
    name = models.CharField(max_length=20, null=False)
    status = models.CharField(max_length=20, null=True)


# Degree modal
class Degree(models.Model):
    name = models.CharField(max_length=100, null=False)


# Department modal
class Department(models.Model):
    name = models.CharField(max_length=100, null=False)


# Faculty modal
class Faculty(models.Model):
    name = models.CharField(max_length=100, null=False)


# Lecturer modal
class Lecturer(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    tel = models.CharField(max_length=20, null=True)
    image = models.ImageField("Image", upload_to=upload_to, default='anonymous/anonymous.jpg')


# Student modal
class Student(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    tel = models.CharField(max_length=20, null=True)
    dob = models.DateField(null=True)
    description = models.TextField(null=True)
    image = models.ImageField("Image", upload_to=upload_to, default='anonymous/anonymous.jpg')


# Course modal
class Course(models.Model):
    code = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=100, null=False)
    credits = models.CharField(max_length=10, null=False)
    type = models.CharField(max_length=10, null=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    grade = models.CharField(max_length=20, default="-")


class Feedback(models.Model):
    course = models.ForeignKey(Result, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    Course_Content = models.CharField(max_length=100, null=False)
    Instructor_Effectiveness = models.CharField(max_length=100, null=False)
    Clarity_of_Explanations = models.CharField(max_length=100, null=False)
    Usefulness_of_Assignments = models.CharField(max_length=100, null=False)
    Overall_Satisfaction = models.CharField(max_length=100, null=False)





class Course(models.Model):
    course_code = models.CharField(max_length=10)
    course_title = models.CharField(max_length=100)
    credits = models.IntegerField()
    lecturer = models.CharField(max_length=100)

class FeedbackQuestion(models.Model):
    question_text = models.CharField(max_length=255)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    feedback_date = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField()
