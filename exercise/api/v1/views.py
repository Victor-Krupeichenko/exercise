from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.v1.serializers import (
    AllUserLessonsSerializer, UserLessonsSpecificProductSerializer, ProductStatisticsSerializer
)
from education.models import Product, Lesson, LessonView
from django.db.models import Sum, Count, F, Q
from django.contrib.auth.models import User


class AllUserLessons(ListAPIView):
    """
    Представление для показа списка всех уроков у текущего пользователя

    """

    serializer_class = AllUserLessonsSerializer  # Сериализатор
    permission_classes = [IsAuthenticated]  # Доступ имеют только авторизованные пользователи

    def get_queryset(self):

        user = self.request.user  # Получаем текущего пользователя

        # Получаем все записи которые связанны с текущим пользователем(предварительно подгружаем связанные данные)
        lessons_views = LessonView.objects.filter(user=user).select_related("lesson")

        # Получаем уроки, которые были просмотрены (получаем список id уроков)
        view_lesson_id = lessons_views.filter(status="viewed").values_list("lesson_id", flat=True)

        # Получаем уроки, которые небыли просмотрены (путем исключения просотренных)
        not_views = Lesson.objects.exclude(id__in=view_lesson_id).filter(students=user)

        lesson_stats = list()  # Список в котором будут храниться словари со статистикой по каждому уроку

        # Добавляем просмотренные уроки
        for view in lessons_views:
            if view.status == "viewed":
                lesson_stats.append({
                    "title": view.lesson.title,
                    "status": "Просмотрено",
                    "view_time": view.viewed_time_seconds
                })

        # Добавляем уроки, которые пользователь не смотрел
        for unviewed_lesson in not_views:
            lesson_stats.append({
                "title": unviewed_lesson.title,
                "status": "Не просмотрено",
                "view_time": 0
            })

        return lesson_stats

    def list(self, request, *args, **kwargs):
        """
        Показ списка объектов
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserLessonsSpecificProduct(ListAPIView):
    """
    Представление для показа списка всех уроков, к которым пользователь имеет доступ у конкретного продукта
    """
    serializer_class = UserLessonsSpecificProductSerializer  # Сериализатор
    permission_classes = [IsAuthenticated]  # Доступ имеют только авторизованные пользователи

    def get_queryset(self):

        user = self.request.user  # Получаем текущего пользователя
        product_id = self.kwargs['product_id']  # Получение из url маршрута id-продукта

        # Получаем все уроки у конкретного продукта к которым пользователь имеет доступ
        result = Lesson.objects.filter(products__id=product_id, students=user)

        # Получаем все уроки которые просмотрел текущий пользователь(предварительно подгружаем связанные данные)
        lessons_views = LessonView.objects.filter(
            lesson__in=result, status="viewed", user=user
        ).select_related("lesson")

        # Получаем уроки, которые небыли просмотрены (путем исключения просотренных)
        not_views = result.exclude(id__in=lessons_views.values_list("lesson_id", flat=True))

        lesson_stats = list()  # Список в котором будут храниться словари со статистикой по каждому уроку

        # Список в котором будут временна хранится названия уроков(чтобы вывести только послединие просмотренные)
        title_list = list()

        for lesson in reversed(lessons_views):
            if lesson.lesson.title in title_list:
                continue

            title_list.append(lesson.lesson.title)
            temp_dict = {
                "title": lesson,
                "status": lesson.status,
                "view_time": lesson.viewed_time_seconds,
                "last_viewed": lesson.last_viewed
            }

            lesson_stats.append(temp_dict)  # Добовляем просмотренные уроки

        for lesson in not_views:
            temp_dict = {
                "title": lesson,
                "status": "not viewed",
                "view_time": 0,
                "last_viewed": 0
            }
            lesson_stats.append(temp_dict)  # Добовляем не просмотренные уроки

        return lesson_stats

    def list(self, request, *args, **kwargs):
        """
        Показ списка объектов
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductStatistics(ListAPIView):
    """
    Представление для показа списка всех продуктов
    views_lessons: количество просмотренных уроков от всех учеников
    total_time_spent: сколько в сумме все ученики потратили времени на просмотр уроков
    product_access_count: количество учеников занимающихся на продутке
    product_access_percentage: процент приобретения продукта
    """

    serializer_class = ProductStatisticsSerializer  # Сериализатор

    def get_queryset(self):
        result = Product.objects.annotate(
            views_lessons=Count("lessons__lessonview", filter=Q(
                lessons__lessonview__status="viewed"), distinct=True
                                ),
            total=Sum("lessons__lessonview__viewed_time_seconds"),
            product_access_count=Count("productaccess__user", distinct=True),
            total_time_spent=F("total") / F("product_access_count"),
            product_access_percentage=F("product_access_count") * 100 / User.objects.count()
        )
        return result

    def list(self, request, *args, **kwargs):
        """
        Показ списка объектов
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
