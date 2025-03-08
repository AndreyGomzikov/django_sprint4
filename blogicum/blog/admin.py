from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'created_at')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category',
                    'is_published', 'pub_date', 'created_at')
    search_fields = ('title', 'text', 'author__username', 'category__title')
    list_filter = ('is_published', 'category', 'pub_date', 'created_at')

    fieldsets = (
        (None, {'fields': ('title', 'text', 'author',
                           'category', 'location', 'is_published')}),
        ('Дополнительная информация', {
            'fields': ('pub_date',), 'classes': ('collapse',)}),
    )


admin.site.site_header = 'Управление блогом'
admin.site.site_title = 'Администрирование блога'
admin.site.index_title = 'Добро пожаловать в панель управления'
