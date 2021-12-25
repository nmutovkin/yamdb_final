from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, auth_signup,
                    obtain_token)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews')

auth_patterns = [
    path('signup/', auth_signup),
    path('token/', obtain_token)
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_patterns)),
]
