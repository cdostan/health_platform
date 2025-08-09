from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时自动创建关联的Profile"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """用户保存时自动保存关联的Profile"""
    # 移除age和gender的同步代码，因为这些字段只存在于CustomUser中
    profile = instance.core_profile
    profile.save()