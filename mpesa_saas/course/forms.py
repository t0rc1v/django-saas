from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Course


# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=65)
#     password = forms.CharField(max_length=65, widget=forms.PasswordInput)
    

class AddCourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields = ['title', 'content', 'price'] 
   
