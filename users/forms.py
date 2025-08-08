from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    GENDER_CHOICES = [('男', '男'), ('女', '女')]
    age = forms.IntegerField(
        label='年龄',
        min_value=1,
        max_value=120,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 100px'})
    )
    gender = forms.ChoiceField(
        label='性别',
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'width: 100px'})
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'age', 'gender')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '用户名'
        self.fields['email'].label = '电子邮箱'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '密码确认'
        
        self.fields['username'].help_text = '(至少三个字符)'
        self.fields['password1'].help_text = '(至少8个字符，不能全是数字)'
        self.fields['password2'].help_text = '(再次输入相同的密码)'