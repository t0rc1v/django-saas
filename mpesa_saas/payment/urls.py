from django.urls import path
from . import views

urlpatterns = [
    path("<int:course_id>/checkout/", views.create_checkout_session, name="create_checkout_session"),
    path("processing/", views.handle_checkout_session, name="handle_checkout_session"),
    path("course_success/", views.course_success, name="course_success"),
    path("course_cancel", views.course_cancel, name="course_cancel"),
]
