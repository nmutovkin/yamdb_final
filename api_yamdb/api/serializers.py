import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):

    name = serializers.CharField(max_length=256)

    slug = serializers.SlugField(
        max_length=50,
        validators=[validators.UniqueValidator(
            Category.objects.all(),
            message='Поле slug должно быть уникальным'
        )]
    )

    class Meta:
        exclude = ('id', )
        lookup_field = 'slug'
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    name = serializers.CharField(max_length=256)

    slug = serializers.SlugField(
        max_length=50,
        validators=[validators.UniqueValidator(
            Genre.objects.all(),
            message='Поле slug должно быть уникальным'
        )]
    )

    class Meta:
        exclude = ('id', )
        lookup_field = 'slug'
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):

    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):

    rating = serializers.IntegerField(read_only=True)
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all())
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                {'year': 'Некорректный год произведения'})
        return value

    def to_representation(self, instance):
        s = TitleReadSerializer()
        return s.to_representation(instance=instance)


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {'email': {'required': True}}

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError("Can't use 'me' as username")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists"
            )
        return value


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User
        lookup_field = 'username'
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "User with this username already exists"
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists"
            )
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User

    def validate(self, data):
        if 'role' in data:
            role = self.context['request'].user.role
            data['role'] = role  # save role as is

        return data


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',)
        model = Review
        read_only_fields = ('pub_date',)

    def validate(self, data):

        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            author_slug = self.context['request'].user
            author = get_object_or_404(User, username=author_slug)
            if title.reviews.filter(author=author).exists():
                raise validators.ValidationError(
                    {'detail': 'Пользователь может создать только один отзыв '
                               'для каждого произведения'})
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
