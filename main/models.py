from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLES = [
        ('student', 'Ученик'),
        ('coach', 'Тренер'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='student')

class Session(models.Model):
    """Тренироваки в расисании."""

    SPORT_CHOICES = [
        ('voleyball', 'Волейбол'),
        ('basketbal','Баскeтбол'),
        ('football','Футбол'),
        ('fitness','Фитнес'),
    ]

    sport      = models.CharField(max_length=20, choices=SPORT_CHOICES)
    coach      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sessions', limit_choices_to={'role': 'coach'}
    )
    location   = models.CharField(max_length=20)
    date       = models.DateField()
    time       = models.TimeField()
    duration   = models.PositiveBigIntegerField(default=60, help_text='Длительность в минутах')
    max_places = models.PositiveBigIntegerField(default=15)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    def __str__(self):
        return f"{self.get_sport_display()} — {self.date} {self.time}"

    @property
    def sport_name(self):
        return self.get_sport_display()

    @property
    def sport_class(self):
        return self.sport  # используется как CSS-класс

    @property
    def enrolled_count(self):
        return self.enrollments.count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_places


class Enrollment(models.Model):
    """Запись ученика на тренировку."""

    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='enrollments', limit_choices_to={'role': 'student'}
    )
    session    = models.ForeignKey(
        Session, on_delete=models.CASCADE,
        related_name='enrollments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')  # нельзя записаться дважды
        ordering = ['session__date', 'session__time']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return f"{self.student} → {self.session}"

    @property
    def is_past(self):
        session_dt = timezone.datetime.combine(self.session.date, self.session.time)
        session_dt = timezone.make_aware(session_dt)
        return session_dt < timezone.now()
# Create your models here.