from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Course
from .forms import AddCourseForm

def course_list(request):
    courses = Course.objects.all()

    if request.user.is_authenticated:
        for course in courses:
            course.is_unlocked = request.user in course.subscribers.all()
    else:
        for course in courses:
            course.is_unlocked = False
    
    context = {
        "courses": courses
    }

    return render(request, "course/course_list.html", context)

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user not in course.subscribers.all():
        return redirect("course_list")

    context = {
        "course": course
    }

    return render(request, "course/course_detail.html", context)

def add_course(request):
    user = request.user
    if request.method == 'POST':
        form = AddCourseForm(request.POST)

        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = user
            course.save()

            return redirect("course_list")
    else:
        form = AddCourseForm()

    return render(request, 'course/add_course.html', {
        'form': form,
    })
            
