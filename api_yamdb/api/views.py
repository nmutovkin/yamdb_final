from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import (AllValuesFilter, AllValuesMultipleFilter,
                            FilterSet, NumberFilter)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .permissions import AccessToReview, AdminOrSuperUser
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer, UserProfileSerializer,
                          UserSerializer, UserSignupSerializer)


class NameSlugBaseViewSet(viewsets.GenericViewSet,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny,)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return (AdminOrSuperUser(),)

        return super().get_permissions()


class CategoryViewSet(NameSlugBaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(NameSlugBaseViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleFilter(FilterSet):
    category = AllValuesFilter(field_name='category__slug')
    genre = AllValuesMultipleFilter(field_name='genre__slug')
    name = AllValuesFilter(field_name='name', lookup_expr='istartswith')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = (
            'category',
            'genre',
            'name',
            'year',)


class TitleViewSet(viewsets.ModelViewSet):

    queryset = (Title.objects.all().annotate(rating=Avg('reviews__score'))
                .order_by('name'))
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'partial_update']:
            return (AdminOrSuperUser(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer


@api_view(['POST'])
@permission_classes((AllowAny, ))
def auth_signup(request):
    serializer = UserSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()  # create new user

    new_user, _ = User.objects.get_or_create(
        username=serializer.data['username'],
        email=serializer.data['email']
    )

    token = default_token_generator.make_token(new_user)
    new_user.confirmation_code = token
    new_user.save()

    recip_email = serializer.data['email']
    send_mail('Confirmation code',
              (f"User {serializer.data['username']}!"
               f"Your confirmation code is {token}"),
              settings.EMAIL_SENDER, [recip_email, ])
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def obtain_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    code = request.data['confirmation_code']

    if not default_token_generator.check_token(user, code):
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    refresh = RefreshToken.for_user(user)
    token_data = {
        'token': str(refresh.access_token),
    }

    return Response(token_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOrSuperUser, )
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_field = ('username', )

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        user = request.user

        if request.method == 'PATCH':
            context = {'request': request}
            serializer = UserProfileSerializer(user,
                                               data=request.data,
                                               partial=True,
                                               context=context)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        elif self.action in ['partial_update', 'destroy']:
            return (AccessToReview(),)

        return super().get_permissions()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        title_id = self.kwargs['title_id']
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review_id = self.kwargs['review_id']
        title_id = self.kwargs['title_id']
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        if (serializer.instance.author != self.request.user
                and not (self.request.user.is_admin
                         or self.request.user.is_moderator)):
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(CommentViewSet, self).perform_update(serializer)

    def perform_destroy(self, serializer):
        if (serializer.author != self.request.user
                and not (self.request.user.is_admin
                         or self.request.user.is_moderator)):
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super(CommentViewSet, self).perform_destroy(serializer)
