from django.db import models
from django.contrib.auth.models import User


class CheckoutId(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.IntegerField()
    checkout_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.checkout_id
