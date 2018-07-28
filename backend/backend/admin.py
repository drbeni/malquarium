from django import forms
from django.contrib import admin

from backend.models import *


# copied from https://stackoverflow.com/a/42307168
class BaseAdmin(admin.ModelAdmin):
    """
    Base admin capable of forcing widget conversion
    """

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(
            db_field, **kwargs)

        display_as_charfield = getattr(self, 'display_as_charfield', [])
        display_as_choicefield = getattr(self, 'display_as_choicefield', [])

        if db_field.name in display_as_charfield:
            formfield.widget = forms.TextInput(attrs=formfield.widget.attrs)
        elif db_field.name in display_as_choicefield:
            formfield.widget = forms.Select(choices=formfield.choices,
                                            attrs=formfield.widget.attrs)

        return formfield


@admin.register(Sample)
class SampleAdmin(BaseAdmin):
    search_fields = ('sha2', 'tags__name', 'source__name')
    list_display = ('sha2', 'md5', 'original_filename', 'vt_permalink')
    display_as_charfield = ('sha2', 'md5', 'sha1', 'ssdeep', 'original_filename', 'vt_permalink')


@admin.register(Analyzer)
class AnalyzerAdmin(BaseAdmin):
    search_fields = ('identifier', 'name', 'docker_image_name')
    list_display = ('identifier', 'name', 'docker_image_name')
    display_as_charfield = ('identifier', 'name', 'docker_image_name')


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    search_fields = ('name',)
    display_as_charfield = ('name',)


@admin.register(Source)
class SourceAdmin(BaseAdmin):
    search_fields = ('name', 'url')
    list_display = ('name', 'url')
    display_as_charfield = ('name', 'url')


@admin.register(AccessStatistic)
class AccessStatisticAdmin(BaseAdmin):
    search_fields = ('user__username',)


@admin.register(LogAction)
class LogActionAdmin(BaseAdmin):
    search_fields = ('user__username',)
    display_as_charfield = ('operation',)
    readonly_fields = [f.name for f in LogAction._meta.get_fields()]

    def has_add_permission(self, request):
        return False


@admin.register(ServicePlan)
class ServicePlanAdmin(BaseAdmin):
    search_fields = ('name',)
    list_display = ('name', 'download_quota', 'upload_quota')
    display_as_charfield = ('name',)


@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    search_fields = ('user__username', 'service_plan__name',)


@admin.register(Feed)
class FeedAdminAdmin(BaseAdmin):
    search_fields = ('url', 'format', 'source__name',)
    list_display = ('url',)
    display_as_charfield = ('url',)


@admin.register(VirusTotalResult)
class VirusTotalResultAdmin(BaseAdmin):
    search_fields = ('av', 'malware_name')
    list_display = ('av', 'malware_name')
    display_as_charfield = ('av', 'malware_name')
