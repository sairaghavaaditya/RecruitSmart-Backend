from django.db import models
from admin_dashboard.models import JobPost





class Question(models.Model):
    id = models.AutoField(primary_key=True)  # Ensure this is present if you're using a CSV with IDs.
    question = models.TextField()           # This should match your database column for question text.
    answer = models.TextField()             # This should match your database column for answers.
    difficulty = models.CharField(max_length=20)  # Ensure the column exists for difficulty levels.
    keywords = models.JSONField(default=dict)
    

    def __str__(self):
        return self.question
    
    




class UsersResponses(models.Model):
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE)
    user_answer = models.TextField()
    original_answer = models.TextField(default="Not Provided")  # Add a default value
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Response to Question {self.question_id.id}"




class UserResponse(models.Model):
    user_id = models.IntegerField()  # You can later link it to a User model if needed
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    response_text = models.TextField()
    difficulty = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Response to Question ID {self.question.id} by User {self.user_id}"


    

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Ideally hashed

    def __str__(self):
        return self.email
