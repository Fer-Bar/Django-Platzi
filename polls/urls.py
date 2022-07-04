from django.urls import path
from . import views


app_name = 'polls'
urlpatterns = [
    path("", views.IndexView.as_view(), name='index'),
    path("polls/<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("polls/results/<int:pk>/", views.ResultView.as_view(), name="results"),
    path("polls/vote/<int:question_id>/", views.vote, name="vote"),
]