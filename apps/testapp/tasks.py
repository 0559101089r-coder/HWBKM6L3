from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()


@shared_task
def send_welcome_email_task(user_email):
    send_mail(
        subject="Добро пожаловать!",
        message="Спасибо за регистрацию на нашем сайте.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

    return f"Приветственное письмо отправлено на {user_email}"


@shared_task
def clean_inactive_users_task(days=30):
    cutoff_date = timezone.now() - timedelta(days=days)

    inactive_users = User.objects.filter(
        is_active=False,
        date_joined__lte=cutoff_date,
    )

    deleted_count, _ = inactive_users.delete()

    return f"Удалено неактивных пользователей: {deleted_count}"


@shared_task
def send_daily_admin_report_task():
    admin_count = User.objects.filter(role="ADMIN").count()
    moderator_count = User.objects.filter(role="MODERATOR").count()
    user_count = User.objects.filter(role="USER").count()

    report = (
        "--- Статистика пользователей ---\n"
        f"Администраторы: {admin_count}\n"
        f"Модераторы: {moderator_count}\n"
        f"Обычные пользователи: {user_count}\n"
        "---------------------------------"
    )

    print(report)
    return report