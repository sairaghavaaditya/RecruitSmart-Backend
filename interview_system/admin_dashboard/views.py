from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JobPost
import json


from .models import Admin


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
def create_job_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            description = data.get('description', '')

            if not title or not description:
                return JsonResponse({'error': 'Title and description are required.'}, status=400)

            job_post = JobPost.objects.create(title=title, description=description)
            return JsonResponse({'message': 'Job post created successfully!', 'job_post_id': job_post.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method. Only POST is allowed.'}, status=405)


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
