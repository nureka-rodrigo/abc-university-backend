from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, validators

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

        extra_kwargs = {
            'username': {
                'required': True,
                'allow_blank': False,
                'validators': [
                    validators.UniqueValidator(
                        get_user_model().objects.all(), 'Username already in use'
                    )
                ]
            },
            'password': {
                'write_only': True,
                'required': True,
                'allow_blank': False
            },
            'role': {
                'required': True,
                'allow_blank': False
            },
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        role = validated_data.get('role')

        user = get_user_model().objects.create(
            username=username,
            password=make_password(password),
            role=role,
        )

        return user


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = '__all__'


class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Degree
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = '__all__'


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Faculty
        fields = '__all__'


class LecturerSerializer(serializers.ModelSerializer):
    username = UserSerializer()

    class Meta:
        model = models.Lecturer
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    username = UserSerializer()
    degree = DegreeSerializer()
    department = DepartmentSerializer()
    faculty = FacultySerializer()

    class Meta:
        model = models.Student
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()
    semester = SemesterSerializer()

    class Meta:
        model = models.Course
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    semester = SemesterSerializer()

    class Meta:
        model = models.Result
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feedback
        fields = '__all__'


from .models import Course, FeedbackQuestion

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = '__all__'
