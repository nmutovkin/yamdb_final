from django.contrib import admin
from reviews.models.category import Category
from reviews.models.comment import Comment
from reviews.models.genre import Genre
from reviews.models.review import Review
from reviews.models.title import Title
from reviews.models.user import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'role',
        'email',
        'first_name',
        'last_name',
        'bio',
    )
    empty_value_display = '-пусто-'
    list_editable = ('bio',)


class TitleAdmin(admin.ModelAdmin):
    fields = ('name', 'year', 'description', 'genre', 'category',)
    list_display = ('name', 'year', 'description', 'get_genres', 'category',)
    empty_value_display = '-пусто-'
    list_editable = ('description', 'category')

    def get_genres(self, obj):
        return ', '.join([g.name for g in obj.genre.all()])


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)


class ReviewAdmin(admin.ModelAdmin):
    fields = ('title', 'text', 'score', 'author',)
    list_display = ('text', 'author', 'score', 'title',)
    search_fields = ('author',)
    list_editable = ('score', )


class CommentAdmin(admin.ModelAdmin):
    fields = ('review', 'text', 'author',)
    list_display = ('text', 'author', 'review')
    search_fields = ('author', )


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
