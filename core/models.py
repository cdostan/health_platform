from time import timezone
from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
import datetime

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