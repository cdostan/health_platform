from django.db.models import Avg, Sum
from django.shortcuts import render
import requests

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

from django.views.generic import CreateView, ListView, TemplateView
from .models import SleepRecord, ExerciseRecord, DietRecord, UserProfile, HealthAlert, Friendship, Like, Comment
from .forms import SleepRecordForm,ExerciseRecordForm,DietRecordForm,UserProfileForm,UserSearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from users.forms import CustomUserEditForm
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.models import CustomUser
from django.contrib.contenttypes.models import ContentType

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_form_instance = request.user

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile) # 传递 request.FILES
        user_form = CustomUserEditForm(request.POST, instance=user_form_instance)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, '健康档案已更新')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = CustomUserEditForm(instance=user_form_instance)

    return render(request, 'core/profile.html', {'profile_form': profile_form, 'user_form': user_form})

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
        return SleepRecord.objects.filter(user=self.request.user).order_by('-date')[:14]

class HealthAdviceView(LoginRequiredMixin, TemplateView):
    template_name = 'core/advice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=7)

        # 获取用户健康档案
        profile, created = UserProfile.objects.get_or_create(user=user)

        # 获取近7天的健康数据
        sleep_records = SleepRecord.objects.filter(user=user, date__gte=seven_days_ago)
        exercise_records = ExerciseRecord.objects.filter(user=user, date__gte=seven_days_ago)
        diet_records = DietRecord.objects.filter(user=user, date__gte=seven_days_ago)

        # 计算平均睡眠时间（小时）
        if sleep_records:
            total_sleep_hours = sum(r.duration for r in sleep_records)
            avg_sleep_hours = total_sleep_hours / len(sleep_records)
        else:
            avg_sleep_hours = 0

        # 计算运动总时长（分钟）
        total_exercise_duration = sum(r.duration for r in exercise_records) if exercise_records else 0

        # 计算平均每日卡路里
        if diet_records:
            avg_daily_calories = sum(r.calories for r in diet_records) / 7
        else:
            avg_daily_calories = 0

        # 生成健康建议（使用小时单位）
        advice = self.generate_advice(
            user=user,
            avg_sleep_hours=avg_sleep_hours,
            total_exercise_duration=total_exercise_duration,
            avg_daily_calories=avg_daily_calories
        )

        context.update({
            'user': user,
            'profile': profile,
            'avg_sleep_duration': f"{avg_sleep_hours:.2f}",
            'total_exercise_duration': total_exercise_duration,
            'avg_daily_calories': f"{avg_daily_calories:.2f}",
            'advice': advice,
            'sleep_records_count': len(sleep_records)  # 添加记录数用于调试
        })

        return context

    def generate_advice(self, user, avg_sleep_hours, total_exercise_duration, avg_daily_calories):
        advice_list = []
        # 直接从user对象获取age和gender
        # 修正：由于UserProfile中已移除age和gender，这里直接访问user对象
        age = user.age
        gender = user.gender

        # 睡眠建议（基于小时）
        if avg_sleep_hours < 6:
            advice_list.append(f"⚠️ 您的平均睡眠时间仅为{avg_sleep_hours:.1f}小时，严重不足！建议保证每天7-9小时睡眠。")
        elif avg_sleep_hours < 7:
            advice_list.append(f"您的平均睡眠时间为{avg_sleep_hours:.1f}小时，略低于推荐值，建议增加睡眠时间。")

        # 运动建议
        if total_exercise_duration < 150:
            advice_list.append("您上周运动量不足（推荐每周150分钟中等强度运动），建议增加日常活动。")
        elif total_exercise_duration > 300:
            advice_list.append(f"您上周运动量很好（共{total_exercise_duration}分钟），请继续保持！")

        # 饮食建议（考虑性别差异）
        # 修正：直接使用从user对象获取的gender
        if gender == '男':
            if avg_daily_calories > 2800:
                advice_list.append("您的每日热量摄入偏高（男性推荐约2500大卡），注意控制饮食。")
        elif gender == '女':
            if avg_daily_calories > 2200:
                advice_list.append("您的每日热量摄入偏高（女性推荐约2000大卡），注意控制饮食。")

        # 默认建议
        if not advice_list:
            advice_list.append("您的健康状况良好，各项指标都在推荐范围内，请继续保持！")

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
        self.check_health_alerts()
        unread_alerts = HealthAlert.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by('-created_at')
        
        context['unread_alerts'] = unread_alerts
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

    def check_health_alerts(self):
        """检查用户健康状态并生成提醒"""
        user = self.request.user
        today = timezone.now().date()
        profile = user.core_profile
        
        end_date = today
        start_date = end_date - timedelta(days=6)
        
        sleep_records = SleepRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        consecutive_sleep_shortage = 0
        for i in range(3):  
            check_date = today - timedelta(days=i)
            day_records = sleep_records.filter(date=check_date)
            
            if day_records.exists():
                sleep_hours = sum(record.duration for record in day_records)
                if sleep_hours < 6:  
                    consecutive_sleep_shortage += 1
                else:
                    break
            else:
                break
        
        if consecutive_sleep_shortage >= 2:
            existing_alert = HealthAlert.objects.filter(
                user=user,
                alert_type='sleep',
                is_read=False
            ).first()
            
            if existing_alert:
                existing_alert.consecutive_days = consecutive_sleep_shortage
                existing_alert.message = f"您已连续{consecutive_sleep_shortage}天睡眠不足，请注意休息！"
                existing_alert.save()
            else:
                HealthAlert.objects.create(
                    user=user,
                    alert_type='sleep',
                    message=f"您已连续{consecutive_sleep_shortage}天睡眠不足，请注意休息！",
                    consecutive_days=consecutive_sleep_shortage
                )
        
        exercise_records = ExerciseRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        consecutive_exercise_shortage = 0
        for i in range(3):  
            check_date = today - timedelta(days=i)
            day_records = exercise_records.filter(date=check_date)
            
            if day_records.exists():
                exercise_calories = sum(record.calories for record in day_records)
                if exercise_calories < profile.daily_exercise_goal * 0.5: 
                    consecutive_exercise_shortage += 1
                else:
                    break
            else:
                break
        
        if consecutive_exercise_shortage >= 2:
            existing_alert = HealthAlert.objects.filter(
                user=user,
                alert_type='exercise',
                is_read=False
            ).first()
            
            if existing_alert:
                existing_alert.consecutive_days = consecutive_exercise_shortage
                existing_alert.message = f"您已连续{consecutive_exercise_shortage}天运动量不足，请增加活动！"
                existing_alert.save()
            else:
                HealthAlert.objects.create(
                    user=user,
                    alert_type='exercise',
                    message=f"您已连续{consecutive_exercise_shortage}天运动量不足，请增加活动！",
                    consecutive_days=consecutive_exercise_shortage
                )

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

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_alert_as_read(request, alert_id):
    """标记健康提醒为已读"""
    try:
        alert = HealthAlert.objects.get(id=alert_id, user=request.user)
        alert.is_read = True
        alert.save()
        return JsonResponse({'status': 'success'})
    except HealthAlert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '提醒不存在'}, status=404)

def search_food_calories(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'foods': []})

    params = {
        'food': query,
        'token': "hIcaRLzOptmTXEriFgBDjQNBudFKeOfn",
    }

    API_URL = "https://api.istero.com/resource/v1/food/calorie/query"

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        api_data = response.json()

        if api_data.get('code') == 200 and api_data.get('data') and api_data['data'].get('lists'):
            results = []
            for item in api_data['data']['lists']:
                results.append({
                    'name': item.get('name'),
                    'calorie': item.get('calorie'),
                })
            return JsonResponse({'foods': results})
        else:
            return JsonResponse({'foods': [], 'message': '未找到相关食物或API返回错误'})

    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return JsonResponse({'foods': [], 'message': 'API请求失败'}, status=500)

class FriendshipView(LoginRequiredMixin, TemplateView):
    template_name = 'core/friends.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 获取已接受的好友列表
        friends = CustomUser.objects.filter(
            Q(friendship_sent__to_user=user, friendship_sent__status='accepted') |
            Q(friendship_received__from_user=user, friendship_received__status='accepted')
        ).distinct()

        # 获取收到的好友请求
        incoming_requests = Friendship.objects.filter(to_user=user, status='pending')

        # 获取已发送的好友请求
        outgoing_requests = Friendship.objects.filter(from_user=user, status='pending')

        # 处理用户搜索
        search_form = UserSearchForm(self.request.GET)
        search_results = []
        if search_form.is_valid():
            username = search_form.cleaned_data['username']
            if username:
                search_results = CustomUser.objects.filter(
                    username__icontains=username
                ).exclude(
                    username=user.username
                )

        context.update({
            'friends': friends,
            'incoming_requests': incoming_requests,
            'outgoing_requests': outgoing_requests,
            'search_form': search_form,
            'search_results': search_results,
        })
        return context

@login_required
def send_friend_request(request, username):
    from_user = request.user
    to_user = get_object_or_404(CustomUser, username=username)

    if from_user == to_user:
        messages.error(request, '不能添加自己为好友。')
    elif Friendship.objects.filter(from_user=from_user, to_user=to_user).exists():
        messages.info(request, '好友请求已发送，请勿重复操作。')
    elif Friendship.objects.filter(from_user=to_user, to_user=from_user).exists():
        messages.info(request, '对方已向您发送好友请求，请前往处理。')
    else:
        Friendship.objects.create(from_user=from_user, to_user=to_user)
        messages.success(request, f'已向 {username} 发送好友请求。')

    return redirect('friendship')

@login_required
def handle_friend_request(request, request_id, action):
    friend_request = get_object_or_404(Friendship, id=request_id)
    if friend_request.to_user != request.user:
        messages.error(request, '您无权处理此请求。')
        return redirect('friendship')

    if action == 'accept':
        friend_request.status = 'accepted'
        friend_request.save()
        messages.success(request, f'已接受来自 {friend_request.from_user.username} 的好友请求。')
    elif action == 'reject':
        friend_request.status = 'rejected'
        friend_request.save()
        messages.success(request, f'已拒绝来自 {friend_request.from_user.username} 的好友请求。')
    elif action == 'cancel':
        if friend_request.from_user == request.user:
            friend_request.delete()
            messages.success(request, '已取消好友请求。')
        else:
            messages.error(request, '您无权取消此请求。')

    return redirect('friendship')

class SocialCircleView(LoginRequiredMixin, TemplateView):
    template_name = 'core/social_circle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 获取所有已接受的好友，包括自己
        friends = list(CustomUser.objects.filter(
            Q(friendship_sent__to_user=user, friendship_sent__status='accepted') |
            Q(friendship_received__from_user=user, friendship_received__status='accepted')
        ).distinct())
        
        # 将当前用户添加到好友列表中
        friends.append(user)

        # 获取所有好友和自己的健康数据记录（睡眠、运动、饮食）
        all_records = []
        for friend in friends:
            all_records.extend(list(friend.sleeprecord_set.all()))
            all_records.extend(list(friend.exerciserecord_set.all()))
            all_records.extend(list(friend.dietrecord_set.all()))
        
        # 将所有记录按创建时间倒序排序
        all_records.sort(key=lambda x: x.created_at, reverse=True)

        # 为每条记录添加一个属性，用于判断当前用户是否已点赞
        for record in all_records:
            record.user_liked = record.likes.filter(user=user).exists()
            record.comments_list = record.comments.all()

        context['all_records'] = all_records
        return context
    
@login_required
@require_POST
def like_record(request, record_type, record_id):
    model_map = {
        'sleep': SleepRecord,
        'exercise': ExerciseRecord,
        'diet': DietRecord,
    }
    model = model_map.get(record_type)
    if not model:
        return JsonResponse({'error': 'Invalid record type'}, status=400)

    try:
        record = model.objects.get(id=record_id)
        content_type = ContentType.objects.get_for_model(record)
        like, created = Like.objects.get_or_create(user=request.user, content_type=content_type, object_id=record.id)

        if not created:
            like.delete()
            return JsonResponse({'status': 'unliked', 'like_count': record.likes.count()})
        else:
            return JsonResponse({'status': 'liked', 'like_count': record.likes.count()})

    except model.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)


@login_required
@require_POST
def comment_on_record(request, record_type, record_id):
    model_map = {
        'sleep': SleepRecord,
        'exercise': ExerciseRecord,
        'diet': DietRecord,
    }
    model = model_map.get(record_type)
    if not model:
        return JsonResponse({'error': 'Invalid record type'}, status=400)

    try:
        record = model.objects.get(id=record_id)
        text = request.POST.get('text')
        if not text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)

        comment = Comment.objects.create(
            user=request.user,
            content_object=record,
            text=text
        )

        return JsonResponse({
            'status': 'success',
            'comment': {
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%Y年%m月%d日 %H:%M')
            }
        })
    except model.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
