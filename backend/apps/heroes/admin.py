"""Админка раздела «Герої не вмирають»."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Branch, Hero, HeroPhoto


class HeroPhotoInline(admin.TabularInline):
    model = HeroPhoto
    extra = 1
    fields = ('preview', 'image', 'caption', 'order')
    readonly_fields = ('preview',)
    ordering = ('order', 'id')

    @admin.display(description='Прев’ю')
    def preview(self, obj):
        if not obj or not obj.pk or not obj.image:
            return '—'
        return format_html(
            '<img src="{}" style="height:90px;border-radius:4px;object-fit:cover;">',
            obj.image.url,
        )


@admin.register(Branch)
class BranchAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'order', 'heroes_count')
    list_editable = ('order',)
    search_fields = ('name',)

    @admin.display(description='героїв')
    def heroes_count(self, obj):
        return obj.heroes.count()


@admin.register(Hero)
class HeroAdmin(TabbedTranslationAdmin):
    list_display = ('thumb', 'full_name', 'rank_dates', 'branch', 'birth_raion', 'photos_count', 'is_published')
    list_display_links = ('thumb', 'full_name')
    list_filter = ('is_published', 'branch', 'birth_raion')
    search_fields = ('full_name', 'biography', 'rank_dates')
    list_editable = ('is_published',)
    inlines = (HeroPhotoInline,)
    save_on_top = True

    fieldsets = (
        ('Основне', {
            'fields': ('slug', 'full_name', 'rank_dates', 'branch', 'birth_raion', 'is_published'),
        }),
        ('Біографія', {
            'fields': ('biography',),
            'description': 'Кожен абзац — з нового рядка.',
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('branch').prefetch_related('photos')

    @admin.display(description='')
    def thumb(self, obj):
        photo = obj.main_photo
        if not photo:
            return 'немає фото'
        return format_html(
            '<img src="{}" style="height:48px;width:38px;border-radius:4px;'
            'object-fit:cover;display:block;">',
            photo.image.url,
        )

    @admin.display(description='фото')
    def photos_count(self, obj):
        return obj.photos.count()


admin.site.site_header = 'Музей — керування сайтом'
admin.site.site_title = 'Музей'
admin.site.index_title = 'Розділи сайту'
