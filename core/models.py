from time import timezone
from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
import datetime
from django.conf import settings


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('男', '男'),
        ('女', '女'),
    ]
    """扩展用户信息的Profile模型，与auth.User一对一关联"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_profile'  # 自定义反向关系名称
    )
    # 同步auth.User的字段
    age = models.PositiveSmallIntegerField(
        '年龄',
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        null=True,
        blank=True
    )
    gender = models.CharField(
        '性别',
        max_length=1,
        choices=GENDER_CHOICES,
        default='U',
        blank=True
    )

    # 健康相关属性
    height = models.PositiveSmallIntegerField(
        '身高(cm)',
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        null=True,
        blank=True
    )
    weight = models.DecimalField(
        '体重(kg)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        null=True,
        blank=True
    )

    # 健康目标
    daily_sleep_goal = models.PositiveSmallIntegerField(
        '每日睡眠目标(小时)',
        default=8,
        validators=[MinValueValidator(4), MaxValueValidator(12)]
    )
    daily_exercise_goal = models.PositiveSmallIntegerField(
        '每日运动目标(卡路里)',
        default=500,
        validators=[MinValueValidator(200), MaxValueValidator(2000)]
    )


    # 健康档案
    blood_type = models.CharField(
        '血型',
        max_length=10,
        choices=[
            ('A', 'A型'),
            ('B', 'B型'),
            ('AB', 'AB型'),
            ('O', 'O型')
        ],
        blank=True
    )
    allergies = models.TextField('过敏史', blank=True)

    class Meta:
        verbose_name = '用户健康档案'
        verbose_name_plural = '用户健康档案'

    @property
    def bmi(self):
        """计算BMI指数"""
        if self.height and self.weight:
            return round(float(self.weight) / ((self.height / 100) ** 2), 1)
        return None

    def __str__(self):
        return f"{self.user.username}的健康档案"
    

class SleepRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField("记录日期", default=datetime.date.today)
    bedtime = models.TimeField("入睡时间")
    wakeup_time = models.TimeField("起床时间")

    class Meta:
        verbose_name = "睡眠记录"
        verbose_name_plural = "睡眠记录"
        ordering = ['-date']  

    @property
    def day_of_week(self):
        return self.date.strftime('%A')

    @property
    def quality(self):
        hours = self.duration
        if hours >= 8: return 5
        elif hours >= 7: return 4
        elif hours >= 6: return 3 
        elif hours >= 5: return 2
        else: return 1

    @property
    def duration(self):
        if not (self.bedtime and self.wakeup_time):
            return 0
            
        bedtime_dt = datetime.datetime.combine(self.date, self.bedtime)
        wakeup_dt = datetime.datetime.combine(
            self.date + datetime.timedelta(days=1) 
            if self.wakeup_time < self.bedtime 
            else self.date,
            self.wakeup_time
        )
        return round((wakeup_dt - bedtime_dt).total_seconds() / 3600, 1)

    def __str__(self):
        return f"{self.user.username}的睡眠记录 - {self.date}"

class ExerciseRecord(models.Model):
    EXERCISE_TYPES = [
        ('running', '跑步'),
        ('walking', '步行'),
        ('cycling', '骑行'),
        ('swimming', '游泳'),
        ('gym', '健身房'),
        ('other', '其他')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField("运动日期", default=datetime.date.today)
    exercise_type = models.CharField("运动类型", max_length=20, choices=EXERCISE_TYPES)
    duration = models.PositiveIntegerField("运动时长(分钟)", validators=[MinValueValidator(1)])
    calories = models.PositiveIntegerField("消耗卡路里")
    notes = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "运动记录"
        verbose_name_plural = "运动记录"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username}的运动记录 - {self.date}"


class DietRecord(models.Model):
    MEAL_TYPES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '零食')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField("饮食日期", default=datetime.date.today)
    meal_type = models.CharField("餐别", max_length=20, choices=MEAL_TYPES)
    food_name = models.CharField("食物名称", max_length=100)
    quantity = models.PositiveIntegerField("份量(g/ml)", validators=[MinValueValidator(1)])
    calories = models.PositiveIntegerField("卡路里")
    notes = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "饮食记录"
        verbose_name_plural = "饮食记录"
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.user.username}的饮食记录 - {self.date}"

# ... existing code ...

class HealthAlert(models.Model):
    """健康提醒模型，用于记录用户健康状态异常的提醒"""
    ALERT_TYPES = [
        ('sleep', '睡眠不足'),
        ('exercise', '运动不足'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="用户")
    alert_type = models.CharField("提醒类型", max_length=20, choices=ALERT_TYPES)
    message = models.CharField("提醒消息", max_length=200)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    is_read = models.BooleanField("是否已读", default=False)
    consecutive_days = models.PositiveSmallIntegerField("连续天数", default=0)
    
    class Meta:
        verbose_name = "健康提醒"
        verbose_name_plural = "健康提醒"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.get_alert_type_display()}提醒"
