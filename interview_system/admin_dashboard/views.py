from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JobPost,Question
import json


from .models import Admin

import uuid
import io

import csv
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JobPost, Question

@csrf_exempt
def create_job_post(request):
    if request.method == 'POST':
        try:
            # Get the data from the form
            title = request.POST.get('title')
            description = request.POST.get('description')
            questions_csv = request.FILES.get('questions_csv')  # Get the uploaded CSV file

            if not questions_csv:
                return JsonResponse({'error': 'No CSV file uploaded.'}, status=400)

            # Read the CSV file and parse it
            csv_data = questions_csv.read().decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_data)

            # Ensure the required columns are in the CSV
            required_columns = ['question', 'answer', 'difficulty', 'keywords']
            missing_columns = [col for col in required_columns if col not in csv_reader.fieldnames]

            if missing_columns:
                return JsonResponse({'error': f"Missing columns: {', '.join(missing_columns)}"}, status=400)

            # Create the JobPost instance
            job_post_command_id = str(uuid.uuid4())  # Generate unique ID (UUID)

            # Create the JobPost instance
            job_post = JobPost.objects.create(
                title=title,
                description=description,
                command_id=job_post_command_id,
            )

            # Process each row in the CSV
            questions = []
            for row in csv_reader:
                question = {
                    'question': row['question'],
                    'answer': row['answer'],
                    'difficulty': row['difficulty'],
                    'keywords': [],
                }

                # Handle the 'keywords' column and ensure it is a valid JSON array
                try:
                    question['keywords'] = json.loads(row['keywords'])  # Convert JSON string to list
                except json.JSONDecodeError:
                    question['keywords'] = []  # If there's an error, set it to an empty list

                # Save the question to the database
                Question.objects.create(
                    job_post=job_post,  # Link the question to the job post
                    command_id=job_post_command_id,
                    question=question['question'],
                    answer=question['answer'],
                    difficulty=question['difficulty'],
                    keywords=question['keywords'],
                )

            # Return a success response
            return JsonResponse({'message': 'Job post created successfully!', 'job_post_id': job_post.id}, status=200)

        except Exception as e:
            # Catch any exception and return an error response
            return JsonResponse({'error': str(e)}, status=500)






@csrf_exempt
def list_job_posts(request):
    if request.method == "GET":
        job_posts = JobPost.objects.all().values("id", "title", "description", "created_at")
        return JsonResponse(list(job_posts), safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import JobPost



@csrf_exempt
def delete_job_post(request, job_id):
    if request.method == "DELETE":
        try:
            job_post = JobPost.objects.get(id=job_id)
            job_post.delete()
            return JsonResponse({"message": "Job post deleted successfully!"})
        except JobPost.DoesNotExist:
            return JsonResponse({"error": "Job post not found!"}, status=404)








@csrf_exempt
def admin_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Validate input
            if not email or not password:
                return JsonResponse({"error": "Email and password are required."}, status=400)

            # Authenticate admin
            try:
                admin_user = Admin.objects.get(email=email)
                if admin_user.password != password:  # Use a secure hash function in production
                    return JsonResponse({"error": "Invalid email or password."}, status=401)
            except Admin.DoesNotExist:
                return JsonResponse({"error": "Invalid email or password."}, status=401)

            # Login successful
            return JsonResponse({"message": "Admin login successful!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
