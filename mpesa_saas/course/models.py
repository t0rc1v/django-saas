from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses_taught")
    subscribers = models.ManyToManyField(User, related_name="courses_subscribed", blank=True)
    price = models.IntegerField()

    def __str__(self):
        return self.title