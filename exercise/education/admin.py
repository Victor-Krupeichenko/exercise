from django.contrib import admin
from .models import Product, ProductAccess, Lesson, LessonView


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Регистрация модели Product в админке
    """

    list_display = ["name", "owner"]
    list_display_links = ["name", "owner"]


@admin.register(ProductAccess)
class ProductAccessAdmin(admin.ModelAdmin):
    """
    Регистрация модели ProductAccess в админке
    """

    list_display = ["user", "product"]
    list_display_links = ["user", "product"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Регистрация модели Lesson в админке
    """

    list_display = ["title", "get_user_count"]
    filter_horizontal = ["products"]

    def get_user_count(self, obj):
        """
        Подсчитывает количество пользователей которые имею доступ к уроку
        :param obj: экземпляр модели
        :return: количество пользователь
        """

        return obj.students.count()

    # Имя, которое будет использоватся для колонки с показом количества пользователей
    get_user_count.short_description = "студентов"


@admin.register(LessonView)
class LessonViewAdmin(admin.ModelAdmin):
    """
    Регистрация модели LessonView в админке
    """

    list_display = ["user", "lesson", "viewed_time_seconds", "status", "last_viewed"]
