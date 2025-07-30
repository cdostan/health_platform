from django.urls import path
from . import views
from .views import SleepCreateView, SleepListView, HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # 根URL对应的视图
    path('sleep/', SleepListView.as_view(), name='sleep-list'),
    path('sleep/add/', SleepCreateView.as_view(), name='sleep-add'),
]