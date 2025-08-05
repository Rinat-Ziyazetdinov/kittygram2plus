from rest_framework import viewsets, permissions, filters
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend


from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .permissions import OwnerOrReadOnly, ReadOnly
from .throttling import WorkingHoursRateThrottle
from .pagination import CatsPagination


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    permission_classes = (OwnerOrReadOnly,)
    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    throttle_scope = 'low_request'
    # Для PageNumberPagination, установленного в классе, параметр PAGE_SIZE \
    # будет взят из словаря REST_FRAMEWORK в settings.py.
    # pagination_class = PageNumberPagination
    # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    # pagination_class = LimitOffsetPagination
    # Вот он наш собственный класс пагинации с page_size=20
    # pagination_class = CatsPagination

    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    # Добавим в кортеж ещё один бэкенд
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    # Определим, что значение параметра search должно быть началом искомой строки
    search_fields = ('^name', 'achievements__name', 'owner__username')
    # Сортировать будем по полям name и birth_year
    ordering_fields = ('name', 'birth_year')
    # Если установлен атрибут ordering, то переданное ему значение будет\
    # использоваться в качестве поля для сортировки по умолчанию при выдаче
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
    # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()

    def get_queryset(self):
        queryset = Cat.objects.all()
        # Добыть параметр color из GET-запроса
        color = self.request.query_params.get('color')
        if color is not None:
            #  через ORM отфильтровать объекты модели Cat
            #  по значению параметра color, полученного в запросе
            queryset = queryset.filter(color=color)
        return queryset


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
