from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date, timedelta


class User(AbstractUser):
    ROLES = [
        ('student', 'Ученик'),
        ('coach',   'Тренер'),
        ('admin',   'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='student')



class Location(models.Model):
    """Зал / место проведения тренировок."""
    name     = models.CharField(max_length=100, unique=True, verbose_name='Название')
    capacity = models.PositiveIntegerField(default=20, verbose_name='Вместимость')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        ordering = ['name']
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def __str__(self):
        return self.name


class RecurringSession(models.Model):
    """Шаблон повторяющейся тренировки (каждый пн, вт и т.д.)."""

    SPORT_CHOICES = [
        ('volleyball', 'Волейбол'),
        ('basketball', 'Баскетбол'),
        ('football',   'Футбол'),
        ('fitness',    'Фитнес'),
    ]

    WEEKDAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    REPEAT_MODES = [
        ('weekly', 'Еженедельно'),
        ('daily',  'Ежедневно'),
    ]

    sport      = models.CharField(max_length=20, choices=SPORT_CHOICES)
    coach      = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recurring_sessions',
        limit_choices_to={'role': 'coach'}
    )
    location   = models.CharField(max_length=100)
    weekday    = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)  # null при daily
    repeat_mode = models.CharField(max_length=10, choices=REPEAT_MODES, default='weekly')
    time       = models.TimeField()
    duration   = models.PositiveIntegerField(default=60)
    max_places = models.PositiveIntegerField(default=15)
    date_from  = models.DateField(help_text='С какой даты начинать генерацию')
    date_until = models.DateField(
        null=True, blank=True,
        help_text='До какой даты (пусто = без конца, генерируем на 8 недель вперёд)'
    )
    is_active  = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Шаблон тренировки'
        verbose_name_plural = 'Шаблоны тренировок'

    def __str__(self):
        return f"{self.get_sport_display()} {self.get_weekday_display()} {self.time} — {self.coach}"

    def generate_sessions(self, weeks_ahead=8):
        """Создать Session-объекты вперёд."""
        from datetime import date as date_type
        today = date.today()

        # Привести к datetime.date если вдруг строка
        date_from  = self.date_from
        date_until = self.date_until
        if isinstance(date_from, str):
            date_from = date_type.fromisoformat(date_from)
        if isinstance(date_until, str):
            date_until = date_type.fromisoformat(date_until)

        end_date = date_until or (today + timedelta(weeks=weeks_ahead))
        start    = max(date_from, today)

        if self.repeat_mode == 'daily':
            current = start
            step    = timedelta(days=1)
        else:
            # Найти первую дату с нужным днём недели начиная с start
            days_ahead = (self.weekday - start.weekday()) % 7
            current    = start + timedelta(days=days_ahead)
            step       = timedelta(weeks=1)

        created = 0
        while current <= end_date:
            _, is_new = Session.objects.get_or_create(
                recurring=self,
                date=current,
                defaults={
                    'sport':      self.sport,
                    'coach':      self.coach,
                    'location':   self.location,
                    'time':       self.time,
                    'duration':   self.duration,
                    'max_places': self.max_places,
                }
            )
            if is_new:
                created += 1
            current += step

        return created


class Session(models.Model):
    """Конкретная тренировка в расписании."""

    SPORT_CHOICES = [
        ('volleyball', 'Волейбол'),
        ('basketball', 'Баскетбол'),
        ('football',   'Футбол'),
        ('fitness',    'Фитнес'),
    ]

    sport      = models.CharField(max_length=20, choices=SPORT_CHOICES)
    coach      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sessions', limit_choices_to={'role': 'coach'}
    )
    location   = models.CharField(max_length=100)
    date       = models.DateField()
    time       = models.TimeField()
    duration   = models.PositiveIntegerField(default=60, help_text='Длительность в минутах')
    max_places = models.PositiveIntegerField(default=15)

    # Ссылка на шаблон повторения (null = разовая тренировка)
    recurring  = models.ForeignKey(
        RecurringSession, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sessions'
    )

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
        return self.sport

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
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE,
        related_name='enrollments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')
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