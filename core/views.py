from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

from django.views.generic import CreateView, ListView, TemplateView
from .models import SleepRecord,ExerciseRecord,DietRecord
from .forms import SleepRecordForm,ExerciseRecordForm,DietRecordForm
from django.contrib.auth.mixins import LoginRequiredMixin

class SleepCreateView(LoginRequiredMixin, CreateView):
    model = SleepRecord
    form_class = SleepRecordForm
    template_name = 'core/sleep_form.html'
    success_url = '/sleep/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print("表单验证失败:", form.errors)  
        return super().form_invalid(form)

class SleepListView(LoginRequiredMixin, ListView):
    model = SleepRecord
    template_name = 'core/sleep_list.html'
    context_object_name = 'sleep_records'

    def get_queryset(self):
        return SleepRecord.objects.filter(user=self.request.user).order_by('-date')[:7]

class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = ExerciseRecord
    form_class = ExerciseRecordForm
    template_name = 'core/exercise_form.html'
    success_url = '/exercise/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ExerciseListView(LoginRequiredMixin, ListView):
    model = ExerciseRecord
    template_name = 'core/exercise_list.html'
    context_object_name = 'exercise_records'

    def get_queryset(self):
        return ExerciseRecord.objects.filter(user=self.request.user).order_by('-date')[:7]
from datetime import timedelta
from django.utils import timezone

class HomeView(LoginRequiredMixin, TemplateView):
    """系统首页视图"""
    template_name = 'core/home.html'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # 睡眠数据处理
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        date_range = [start_date + timedelta(days=x) for x in range(7)]

        records = SleepRecord.objects.filter(
            user=self.request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date') 
        
        chart_data = {
            'labels': [],
            'hours': [],
            'quality': []
        }
        
        for single_date in date_range:
            chart_data['labels'].append(single_date.strftime("%m-%d"))
            record = records.filter(date=single_date).first()
            if record:
                chart_data['hours'].append(float(record.duration))
                chart_data['quality'].append(record.quality)
            else:
                chart_data['hours'].append(0)
                chart_data['quality'].append(0)
        
        context['chart_data'] = chart_data

        # 获取今日运动记录和统计数据
        today_exercises = ExerciseRecord.objects.filter(
            user=self.request.user,
            date=today
        ).order_by('-id')

        today_exercise_duration = sum(e.duration for e in today_exercises) if today_exercises.exists() else 0
        today_exercise_calories = sum(e.calories for e in today_exercises) if today_exercises.exists() else 0
        latest_exercise = today_exercises.first()

        context['today_exercises'] = today_exercises
        context['today_exercise_duration'] = today_exercise_duration
        context['today_exercise_calories'] = today_exercise_calories
        context['latest_exercise'] = latest_exercise

        # 获取今日饮食记录和总卡路里
        today_diet = DietRecord.objects.filter(
            user=self.request.user,
            date=today
        ).order_by('-id')

        today_calories = sum(d.calories for d in today_diet) if today_diet.exists() else 0
        context['today_diet'] = today_diet
        context['today_calories'] = today_calories
        context['latest_diet'] = today_diet.first()

        # 运动图表数据（保持不变）
        exercise_records = ExerciseRecord.objects.filter(
            user=self.request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        exercise_chart_data = {
            'labels': [],
            'duration': [],
            'calories': []
        }

        for single_date in date_range:
            exercise_chart_data['labels'].append(single_date.strftime("%m-%d"))
            records = exercise_records.filter(date=single_date)
            if records.exists():
                total_duration = sum(r.duration for r in records)
                total_calories = sum(r.calories for r in records)
                exercise_chart_data['duration'].append(total_duration)
                exercise_chart_data['calories'].append(total_calories)
            else:
                exercise_chart_data['duration'].append(0)
                exercise_chart_data['calories'].append(0)

        context['exercise_chart_data'] = exercise_chart_data

        # 饮食图表数据
        diet_records = DietRecord.objects.filter(
            user=self.request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        diet_chart_data = {
            'labels': [],
            'calories': []
        }

        for single_date in date_range:
            diet_chart_data['labels'].append(single_date.strftime("%m-%d"))
            records = diet_records.filter(date=single_date)
            total_calories = sum(r.calories for r in records) if records.exists() else 0
            diet_chart_data['calories'].append(total_calories)

        context['diet_chart_data'] = diet_chart_data
        return context

class DietCreateView(LoginRequiredMixin, CreateView):
    model = DietRecord
    form_class = DietRecordForm
    template_name = 'core/diet_form.html'
    success_url = '/diet/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DietListView(LoginRequiredMixin, ListView):
    model = DietRecord
    template_name = 'core/diet_list.html'
    context_object_name = 'diet_records'

    def get_queryset(self):
        return DietRecord.objects.filter(user=self.request.user).order_by('-date', 'meal_type')[:14]