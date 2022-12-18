from django.contrib import admin
from .models import Post, Group, Comment


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group',
                    'edit_date',
                    'video')
    list_display_links = ('pk',
                          'text',)
    list_editable = ('group', 'edit_date', 'video')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
