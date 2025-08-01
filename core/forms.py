from django import forms
from .models import SleepRecord, ExerciseRecord, DietRecord, CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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

class ExerciseRecordForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().strftime('%Y-%m-%d')
    )

    class Meta:
        model = ExerciseRecord
        fields = ['date', 'exercise_type', 'duration', 'calories', 'notes']
        widgets = {
            'exercise_type': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '分钟'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '卡路里'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '可选备注'
            })
        }

class DietRecordForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().strftime('%Y-%m-%d')
    )

    class Meta:
        model = DietRecord
        fields = ['date', 'meal_type', 'food_name', 'quantity', 'calories', 'notes']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如: 米饭'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '克/毫升'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '卡路里'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '可选备注'
            })
        }
