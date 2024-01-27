import base64
import os

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.files.base import ContentFile
from knox.auth import AuthToken, TokenAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Feedback, FeedbackQuestion
from .forms import FeedbackForm




from . import models
from .serializers import UserSerializer, StudentSerializer, ResultSerializer, CourseSerializer, FeedbackSerializer




from rest_framework import generics
from .models import Course, FeedbackQuestion
from .serializers import CourseSerializer, FeedbackQuestionSerializer

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class FeedbackQuestionListView(generics.ListAPIView):
    queryset = FeedbackQuestion.objects.all()
    serializer_class = FeedbackQuestionSerializer





@api_view(['GET'])
def list_routes(request):
    """
    Get a list of available API routes.

    Returns:
        Response: JSON response containing a list of routes.
    """
    try:
        # Define the available routes
        routes = [
            "api/login",
            "api/user",
        ]
        # Return the list of routes as a JSON response with a 200-status code
        return Response(routes, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_user(request):
    """
    Create a new user.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing user information.
    """
    try:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return a JSON response with the created user information and a 201 status code
        return Response({
            'user_info': {
                'username': user.username,
            },
        }, status=status.HTTP_201_CREATED)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_user(request):
    """
    Log in a user and generate an authentication token.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing user information and token.
    """
    try:
        # Extract username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Retrieve the user based on the provided username
        user = get_user_model().objects.filter(username=username).first()

        # Check if the user exists
        if user is None:
            raise AuthenticationFailed("User not found")

        # Check if the provided password is correct
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        # Generate an authentication token for the user
        _, token = AuthToken.objects.create(user)

        # Set user as active (if needed)
        if not user.is_active:
            user.save()

        # Return a JSON response with user information and the generated token
        return Response({
            'user_info': {
                'username': user.username,
            },
            'token': token
        }, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """
    Check if the user is authenticated.

    Returns:
        Response: JSON response indicating whether the token is valid.
    """
    return Response({
        "message": "Token is valid"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_student(request):
    """
    Retrieve information about the authenticated student.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing student details.
    """
    try:
        # Get the student associated with the token
        student = models.Student.objects.get(username=request.user)

        # Check if the student exists
        if student:
            # Read and base64 encode the image data
            if student.image:
                with open(student.image.path, 'rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                encoded_image = None

            # Serialize the student data and include the image in the response
            serializer = StudentSerializer(student)
            response_data = serializer.data
            response_data['image'] = encoded_image

            return Response(response_data, status=status.HTTP_200_OK)

    # Handle the case when the student is not found
    except models.Student.DoesNotExist:
        return Response({
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    """
    Update the user's password.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response indicating the result of the password update.
    """
    # Extract data from the request
    current_password = request.data.get('currentPassword')
    new_password = request.data.get('newPassword')
    confirm_password = request.data.get('confirmPassword')

    # Get the user associated with the provided token
    user = request.user

    # Check if the current password matches the one in the database
    if not user.check_password(current_password):
        return Response({
            'error': 'Current password is incorrect.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        return Response({
            'error': 'New password and confirm password do not match.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's password
    user.set_password(new_password)
    user.save()

    # Update session authentication hash
    update_session_auth_hash(request, user)

    # Generate a new token to invalidate the old ones
    AuthToken.objects.create(user)

    return Response({
        'message': 'Password updated successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_student(request):
    """
        Update the student's profile.

        Args:
            request: The HTTP request object.

        Returns:
            Response: JSON response containing password update status.
    """
    try:
        # Get the student associated with the token
        student = models.Student.objects.get(username=request.user)

        # Initialize a flag to check if any field is updated
        fields_updated = False

        # Check for the presence of each field in the request data and update accordingly
        if 'fnameUpdate' in request.data:
            student.first_name = request.data.get('fnameUpdate')
            fields_updated = True

        if 'lnameUpdate' in request.data:
            student.last_name = request.data.get('lnameUpdate')
            fields_updated = True

        if 'telUpdate' in request.data:
            student.tel = request.data.get('telUpdate')
            fields_updated = True

        if 'dobUpdate' in request.data:
            student.dob = request.data.get('dobUpdate')
            fields_updated = True

        if 'descriptionUpdate' in request.data:
            student.description = request.data.get('descriptionUpdate')
            fields_updated = True

        if 'file-upload' in request.FILES:
            uploaded_file = request.FILES['file-upload']

            # Extract the file extension from the original filename
            _, file_extension = os.path.splitext(uploaded_file.name)

            # Generate a new filename using username
            new_filename = f"{student.username}{file_extension}"

            # Set the new filename for the student's image
            student.image.save(new_filename, ContentFile(uploaded_file.read()))
            fields_updated = True

        # If none of the expected fields are present in the request data
        if not fields_updated:
            return Response({
                'error': 'Missing or invalid data for profile update'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save the student instance only if any field is updated
        student.save()

        # Return a success message
        return Response({
            'message': 'User profile updated successfully'
        }, status=status.HTTP_200_OK)

    # Handle the case where the associated student is not found
    except models.Student.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_courses_next_sem(request):
    """
    Retrieve information about the authenticated student.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing course details.
    """
    try:
        # Retrieve the active semester
        active_semester = models.Semester.objects.get(status="1")

        # Set next semester
        next_semester = int(active_semester.name) + 1

        # Retrieve courses of the next semester
        courses = models.Course.objects.filter(semester__name=next_semester)

        # Serialize the results using nested serialization
        serializer = CourseSerializer(courses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_sem(request):
    """
    Retrieve information about the authenticated student.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing semester registration status.
    """
    try:
        # Assuming the checkedCheckboxes array is sent in the request data
        checked_courses = request.data.get('checkedCourses', [])

        # Get the student associated with the token
        student = models.Student.objects.get(username=request.user)

        # Retrieve the active semester
        active_semester = models.Semester.objects.get(status="1")

        # Set next semester
        next_semester = models.Semester.objects.get(name=int(active_semester.name) + 1)

        # Update the Result model for each checked course
        for course_code in checked_courses:
            course = models.Course.objects.get(code=course_code)

            # Check if the result already exists, if not, create a new one
            _, created = models.Result.objects.get_or_create(
                student=student,
                course=course,
                semester=next_semester,
                defaults={'grade': '-'}
            )

        return Response({
            'message': 'Registered for semester successfully'
        }, status=status.HTTP_200_OK)

    # Handle the case when the student is not found
    except models.Student.DoesNotExist:
        return Response({
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_results(request):
    """
    Retrieve information about the authenticated student.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing student results.
    """
    try:
        # Get the student associated with the token
        student = models.Student.objects.get(username=request.user)

        # Retrieve the semester from the request
        semester = request.data['semester']

        # Check if the student exists
        if student:
            # Retrieve results of the student
            results = models.Result.objects.filter(student=student, semester=semester)

            # Serialize the results using nested serialization
            serializer = ResultSerializer(results, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle the case when the student is not found
    except models.Student.DoesNotExist:
        return Response({
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_courses_prev_sem(request):
    """
    Retrieve information about the authenticated student.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing course details.
    """
    try:
        # Retrieve the active semester
        active_semester = models.Semester.objects.get(status="1")

        # Set previous semester
        prev_semester = int(active_semester.name) - 1

        # Retrieve courses of the previous semester
        courses = models.Result.objects.filter(semester__name=prev_semester)

        # Serialize the results using nested serialization
        serializer = ResultSerializer(courses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """
    Submit course feedback.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing submit feedback status.
    """
    try:
        # Get the student associated with the token
        student = models.Student.objects.get(username=request.user)

        # Extract data from the request body
        course = request.data.get('course')
        feedback1 = request.data.get('feedback1')
        feedback2 = request.data.get('feedback2')
        feedback3 = request.data.get('feedback3')
        feedback4 = request.data.get('feedback4')
        feedback5 = request.data.get('feedback5')

        # Get the Course instance based on the course code
        course_instance = models.Result.objects.get(course__code=course)

        # Create a dictionary to match with the model fields
        feedback_data = {
            'course': course_instance.pk,
            'student': student.id,
            'Course_Content': feedback1,
            'Instructor_Effectiveness': feedback2,
            'Clarity_of_Explanations': feedback3,
            'Usefulness_of_Assignments': feedback4,
            'Overall_Satisfaction': feedback5,
        }

        # Serialize the data
        serializer = FeedbackSerializer(data=feedback_data)

        # Validate and save the data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@csrf_exempt
def submit_feedback(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if request.method == 'POST':
        feedback_questions = FeedbackQuestion.objects.all()
        form = FeedbackForm(request.POST, feedback_questions=feedback_questions)

        if form.is_valid():
            answers = {question.question_text: form.cleaned_data[question.question_text] for question in feedback_questions}
            feedback = Feedback.objects.create(user=user, course=course, answers=answers)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return render(request, 'feedback_form.html', {'course': course})
