from time import timezone
from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
import datetime
from django.contrib.auth.models import AbstractUser

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
