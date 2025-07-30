from django import forms
from .models import SleepRecord
from django.utils import timezone
import datetime

class SleepRecordForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().strftime('%Y-%m-%d')
    )

    class Meta:
        model = SleepRecord
        fields = ['date', 'bedtime', 'wakeup_time']
        widgets = {
            'bedtime': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'value': '22:00'
                },
                format='%H:%M'
            ),
            'wakeup_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control', 
                    'value': '07:00'
                },
                format='%H:%M'
            ),
            'quality': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        bedtime = cleaned_data.get("bedtime")
        wakeup_time = cleaned_data.get("wakeup_time")
        date = cleaned_data.get("date")
        
        if all([bedtime, wakeup_time, date]):
            bedtime_dt = datetime.datetime.combine(date, bedtime)
            wakeup_dt = datetime.datetime.combine(
                date + datetime.timedelta(days=1) if wakeup_time < bedtime else date,
                wakeup_time
            )
            
            duration_seconds = (wakeup_dt - bedtime_dt).total_seconds()
            
            if duration_seconds < 3600:
                raise forms.ValidationError("睡眠时长不能少于1小时")
                
        return cleaned_data