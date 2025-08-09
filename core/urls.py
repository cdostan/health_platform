from django.urls import path
from . import views
from .views import SleepCreateView, SleepListView, ExerciseCreateView, ExerciseListView, DietCreateView, DietListView,profile_edit, HomeView, FriendshipView, SocialCircleView
from .views import send_friend_request, handle_friend_request

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # 根URL对应的视图
    path('sleep/', SleepListView.as_view(), name='sleep-list'),
    path('sleep/add/', SleepCreateView.as_view(), name='sleep-add'),
    path('exercise/', ExerciseListView.as_view(), name='exercise-list'),
    path('exercise/add/', ExerciseCreateView.as_view(), name='exercise-add'),
    path('diet/', DietListView.as_view(), name='diet-list'),
    path('diet/add/', DietCreateView.as_view(), name='diet-add'),
    path('profile/', profile_edit, name='profile'),
    path('advice/', views.HealthAdviceView.as_view(), name='health_advice'),
    path('alert/<int:alert_id>/mark-read/', views.mark_alert_as_read, name='mark-alert-read'),
    path('api/search_food/', views.search_food_calories, name='search_food_calories'),
    path('friends/', FriendshipView.as_view(), name='friendship'),
    path('friends/add/<str:username>/', send_friend_request, name='send_friend_request'),
    path('friends/handle/<int:request_id>/<str:action>/', handle_friend_request, name='handle_friend_request'),
    path('social_circle/', SocialCircleView.as_view(), name='social_circle'),
]