from django.http import JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import evaluate_technical_answer
from .models import User


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from admin_dashboard.models import JobPost,Question,UsersResponses
from .serializers import JobPostSerializer



from difflib import SequenceMatcher

# Helper function to calculate similarity




@csrf_exempt
def submit_response(request):
    if request.method == "POST":
        try:
            print("Request received:", request.body)  # Debugging input
            data = json.loads(request.body)
            question_id = data.get("question_id")
            user_answer = data.get("user_answer")

            if not question_id or not user_answer:
                return JsonResponse({"error": "Invalid input."}, status=400)

            question = Question.objects.get(id=question_id)
            print("Question retrieved:", question)  # Debugging question retrieval

            # Placeholder for score calculation logic
              # Replace with your logic
            keywords = question.keywords

            score = evaluate_technical_answer(
                question_g=question.question,
                expected_answer=question.answer,
                candidate_answer=user_answer,
                keywords=keywords
            )
            print("Calculated score:", score)  # Debugging score calculation
            response = UsersResponses.objects.create(
                question_id=question,
                command_id=question.command_id,
                user_answer=user_answer,
                original_answer=question.answer,
                score=score,
            )
            print("Response created:", response)  # Debugging response creation

            return JsonResponse({"message": "Response submitted successfully!", "score": score})

        except Question.DoesNotExist:
            return JsonResponse({"error": "Question not found."}, status=404)
        except Exception as e:
            print("Error:", str(e))  # Print the exact error
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)



class JobPostListView(APIView):
    def get(self, request):
        try:
            # Fetch active job posts only
            active_jobs = JobPost.objects.filter(is_active=True).order_by('-created_at')
            
            if not active_jobs.exists():
                return Response({"message": "No jobs are available."}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the data
            serializer = JobPostSerializer(active_jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from django.core.exceptions import ObjectDoesNotExist

def fetch_next_question(request):
    try:
        command_id = request.GET.get('command_id')
        current_question_id = request.GET.get('current_question_id')

        if not command_id:
            return JsonResponse({"error": "Command ID is required."}, status=400)

        questions = Question.objects.filter(command_id=command_id)  # Filter by command_id

        if current_question_id:
            next_question = questions.filter(id__gt=current_question_id).order_by('id').first()
        else:
            next_question = questions.order_by('id').first()

        if not next_question:
            return JsonResponse({"message": "No more questions available."}, status=200)

        return JsonResponse({
            "id": next_question.id,
            "question": next_question.question,
            "difficulty": next_question.difficulty,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)







@csrf_exempt
def user_signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON body
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            mobile_number = data.get("mobileNumber")
            email = data.get("email")
            password = data.get("password")
            confirm_password = data.get("confirmPassword")

            # Check if all required fields are present
            if not all([first_name, last_name, mobile_number, email, password, confirm_password]):
                return JsonResponse({"error": "All fields are required."}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match."}, status=400)

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already registered."}, status=400)

            # Create the user
            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
                email=email,
                password=password,
            )

            return JsonResponse({"message": "Signup successful!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)







@csrf_exempt
def user_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            password = data.get("password")

            # Validate input
            if not email or not password:
                return JsonResponse({"error": "Email and password are required."}, status=400)

            # Check if the user exists
            try:
                user = User.objects.get(email=email)
                if user.password != password:  # Ideally, use a password hashing mechanism
                    return JsonResponse({"error": "Invalid email or password."}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid email or password."}, status=401)

            # Login successful
            return JsonResponse({"message": "Login successful!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

