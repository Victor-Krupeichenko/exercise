from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class Product(models.Model):
    """
    Модель для создания продукта
    name: название продукта
    owner: владелец продукта
    """

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class ProductAccess(models.Model):
    """
    Модель для доступа к продукту для пользователей
    user: пользователь для которого разрешается доступ к продукту
    product: продукт для которого даем пользователю разрешения
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # При получении пользователем доступа к продукту он автоматически получает доступ ко всем урокам в этом продукте
        for lesson in self.product.lessons.all():
            lesson.students.add(self.user)


class Lesson(models.Model):
    """
    Модель для добавления урока
    title: название урока
    video_link: ссылка на видео с уроком
    duration_seconds: продолжительность видео в секундах
    product: продукт которому пренадлежит урок
    student: пользователь у которого есть доступ к этому уроку
    """

    title = models.CharField(max_length=255)
    video_link = models.URLField()
    duration_seconds = models.PositiveIntegerField()
    products = models.ManyToManyField(Product, related_name="lessons")
    students = models.ManyToManyField(User, related_name="students", blank=True)

    def __str__(self):
        return str(self.title)


class LessonView(models.Model):
    """
    Модель хранения информации по уроку
    user: пользователь который имеею доступ к уроку
    lesson: урок
    viewed_time_seconds: время которое пользователь потратил на упросмотр урока в секундах
    status: показывает статус урока для пользователя (просмотрено/не просмотрено)
    last_viewed: дата просмотра урока
    """

    STATUS_CHOICES = [
        ("viewed", "Просмотрено"),
        ("not_viewed", "Не просмотрено")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    viewed_time_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="not_viewed", choices=STATUS_CHOICES)
    last_viewed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.lesson.title)


@receiver(pre_save, sender=LessonView)
def set_viewed_status(sender, instance, **kwargs):
    """
    Сигнал для изменения статуса урока
    :param sender: класс модели которая отправляет сигнал
    :param instance: экземпляр модели который будет сохранен
    :param kwargs: параметр ключевых слов которые могут передаватся вместе с сигналом
    """

    if instance.viewed_time_seconds > 0:
        percentage = instance.viewed_time_seconds / instance.lesson.duration_seconds * 100
        if percentage >= 80:
            instance.status = "viewed"
            instance.last_viewed = timezone.now()
