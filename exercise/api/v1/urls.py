from django.urls import path
from .views import AllUserLessons, UserLessonsSpecificProduct, ProductStatistics

urlpatterns = [
    # Маршрут для просмотра всех уроков текущего пользователя
    path("lesson-user/", AllUserLessons.as_view(), name="lesson_user"),
    # Маршрут для просмотра всех уроков у конкретного продукта, к которому пользователь имеет
    path("lesson-specific-product/<int:product_id>/", UserLessonsSpecificProduct.as_view(), name="specific_product"),
    # Маршрут для просмотра списка всех продуктов
    path("product-stats/", ProductStatistics.as_view(), name="product_stats"),
]
