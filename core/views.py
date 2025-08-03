from django.db.models import Avg, Sum
from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

from django.views.generic import CreateView, ListView, TemplateView
from .models import SleepRecord,ExerciseRecord,DietRecord,UserProfile
from .forms import SleepRecordForm,ExerciseRecordForm,DietRecordForm,UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '健康档案已更新')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'core/profile.html', {'form': form})

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
        return DietRecord.objects.filter(user=self.request.user).order_by('-date', 'meal_type')[:14]

class HealthAdviceView(LoginRequiredMixin, TemplateView):
    template_name = 'core/advice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=7)

        # 获取用户健康档案 - 统一使用UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)

        # 获取近7天的健康数据
        sleep_records = SleepRecord.objects.filter(user=user, date__gte=seven_days_ago)
        exercise_records = ExerciseRecord.objects.filter(user=user, date__gte=seven_days_ago)
        diet_records = DietRecord.objects.filter(user=user, date__gte=seven_days_ago)

        # 数据汇总和分析
        avg_sleep_duration_minutes = sum(r.duration for r in sleep_records) / len(sleep_records) if sleep_records else 0
        total_exercise_duration = sum(r.duration for r in exercise_records)
        avg_daily_calories = sum(r.calories for r in diet_records) / 7 if diet_records else 0

        # 生成健康建议
        advice = self.generate_advice(user, avg_sleep_duration_minutes, total_exercise_duration, avg_daily_calories)

        context.update({
            'user': user,
            'profile': profile,  # 统一使用profile变量名
            'avg_sleep_duration': f"{avg_sleep_duration_minutes / 60:.2f}",
            'total_exercise_duration': total_exercise_duration,
            'avg_daily_calories': f"{avg_daily_calories:.2f}",
            'advice': advice
        })

        return context

    def generate_advice(self, user, avg_sleep_duration_minutes, total_exercise_duration, avg_daily_calories):
        advice_list = []
        profile = UserProfile.objects.get(user=user)

        # 睡眠建议
        if avg_sleep_duration_minutes < 7 * 60:
            advice_list.append("您的平均睡眠时间少于7小时，建议您调整作息，争取每天有充足的睡眠。")

        # 运动建议
        if total_exercise_duration < 150:
            advice_list.append("您近7天的运动时长较短，建议您增加运动，每周至少进行150分钟的中等强度运动。")

        # 饮食建议
        if profile.age > 18:
            if avg_daily_calories > 2500 and profile.gender == '男':
                advice_list.append("您的平均每日卡路里摄入较高，建议您注意饮食均衡，减少高热量食物摄入。")
            elif avg_daily_calories > 2000 and profile.gender == '女':
                advice_list.append("您的平均每日卡路里摄入较高，建议您注意饮食均衡，减少高热量食物摄入。")

        if not advice_list:
            advice_list.append("您的健康状况良好，请继续保持！")

        return advice_list

    def generate_advice(self, user, avg_sleep_duration_minutes, total_exercise_duration, avg_daily_calories):
        advice_list = []

        # 睡眠建议
        # 修正：将7小时转换为420分钟
        if avg_sleep_duration_minutes < 7 * 60:
            advice_list.append("您的平均睡眠时间少于7小时，建议您调整作息，争取每天有充足的睡眠。")

        # 运动建议
        if total_exercise_duration < 150:
            advice_list.append("您近7天的运动时长较短，建议您增加运动，每周至少进行150分钟的中等强度运动。")

        # 饮食建议
        profile, created = UserProfile.objects.get_or_create(user=user)
        if profile.age > 18:
            if avg_daily_calories > 2500 and profile.gender == '男':
                advice_list.append("您的平均每日卡路里摄入较高，建议您注意饮食均衡，减少高热量食物摄入。")
            elif avg_daily_calories > 2000 and profile.gender == '女':
                advice_list.append("您的平均每日卡路里摄入较高，建议您注意饮食均衡，减少高热量食物摄入。")

        if not advice_list:
            advice_list.append("您的健康状况良好，请继续保持！")

        return advice_list

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
        # 获取用户profile
        profile = self.request.user.core_profile

        # 计算睡眠进度
        sleep_records = SleepRecord.objects.filter(
            user=self.request.user,
            date=today
        )
        sleep_hours = sum(record.duration for record in sleep_records)
        sleep_progress = min(100, (sleep_hours / profile.daily_sleep_goal * 100)) if profile.daily_sleep_goal else 0

        # 计算运动进度
        exercise_records = ExerciseRecord.objects.filter(
            user=self.request.user,
            date=today
        )
        exercise_calories = sum(record.calories for record in exercise_records)
        exercise_progress = min(100, (
                    exercise_calories / profile.daily_exercise_goal * 100)) if profile.daily_exercise_goal else 0

        # 添加到上下文
        context.update({
            'sleep_hours': round(sleep_hours, 1),
            'sleep_progress': round(sleep_progress),
            'exercise_minutes': exercise_calories,
            'exercise_progress': round(exercise_progress),
        })
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