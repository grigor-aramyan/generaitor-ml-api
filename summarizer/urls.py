from django.urls import path
from . import views

urlpatterns = [
    path('feedback_sum', views.feedback_sum, name='make_feedback_summary'),
    path('feedback_sum/<int:id>', views.delete_feedback_sum, name='destroy_feedback_summary')
]