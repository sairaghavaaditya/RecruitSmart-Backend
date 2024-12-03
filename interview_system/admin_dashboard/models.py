from django.db import models

class JobPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Active job posts are visible to users

    def __str__(self):
        return self.title


from django.db import models

class Admin(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150)  # Store hashed passwords in production

    def __str__(self):
        return self.username
