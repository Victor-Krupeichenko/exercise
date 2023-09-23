from rest_framework import serializers


class AllUserLessonsSerializer(serializers.Serializer):
    """
    Сериализатор для показа списка всех уроков у текущего пользователя
    """

    title = serializers.CharField()  # Название урока
    status = serializers.CharField()  # Статус урока (просмотрено/не просмотрено)
    view_time = serializers.IntegerField()  # Время просмотра урока


class UserLessonsSpecificProductSerializer(serializers.Serializer):
    """
    Сериализатор для показа списка всех уроков, к которым пользователь имеет доступ у конкретного продукта
    """

    title = serializers.CharField()  # Название урока
    status = serializers.CharField()  # Статус урока (просмотрено/не просмотрено
    view_time = serializers.IntegerField()  # Сколько по времени просматривался урок
    last_viewed = serializers.DateTimeField()  # Дата последнего просмотра


class ProductStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для показа списка всех продуктов
    """

    name = serializers.CharField()  # Названия продукта
    views_lessons = serializers.IntegerField()  # Количество просмотренных уроков от всех учеников
    total_time_spent = serializers.IntegerField()  # Сколько в сумме все ученики потратили времени на просмотр уроков
    product_access_count = serializers.IntegerField()  # Количество учеников занимающихся на продутке
    product_access_percentage = serializers.FloatField()  # Процент приобретения продукта
