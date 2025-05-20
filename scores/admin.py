from gym.admin import admin_site
from .models import Score, StudentScore, Subject, Class, School, Grade
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from gym.models import UserProfile

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'created_at')
    search_fields = ('name', 'address', 'phone')
    list_filter = ('created_at',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'order', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('name', 'school__name')
    ordering = ('school', 'order')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'created_at')
    list_filter = ('grade__school', 'grade', 'created_at')
    search_fields = ('name', 'grade__name', 'grade__school__name')
    ordering = ('grade', 'name')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'student_count', 'created_at')
    list_filter = ('grade__school', 'grade', 'created_at')
    search_fields = ('name', 'grade__name', 'grade__school__name')
    ordering = ('grade', 'name')

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = '__all__'
        widgets = {
            'subject': forms.Select(attrs={'class': 'subject-select'}),
            'class_obj': forms.Select(attrs={'class': 'class-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user_profile' in self.data:
            try:
                user_profile_id = int(self.data.get('user_profile'))
                user_profile = UserProfile.objects.get(id=user_profile_id)
                self.fields['subject'].queryset = Subject.objects.filter(grade__school=user_profile.school)
                self.fields['class_obj'].queryset = Class.objects.filter(grade__school=user_profile.school)
            except (ValueError, TypeError, UserProfile.DoesNotExist):
                pass
        elif self.instance.pk:
            self.fields['subject'].queryset = Subject.objects.filter(grade__school=self.instance.user_profile.school)
            self.fields['class_obj'].queryset = Class.objects.filter(grade__school=self.instance.user_profile.school)

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm
    list_display = ('get_student_name', 'subject', 'class_obj', 'score', 'date')
    list_filter = ('subject__grade__school', 'subject__grade', 'class_obj', 'date')
    search_fields = ('user_profile__user__first_name', 
                    'user_profile__user__last_name',
                    'user_profile__melli_code',
                    'subject__name',
                    'class_obj__name')
    ordering = ('-date', 'user_profile__user__last_name')
    raw_id_fields = ('user_profile',)

    def get_student_name(self, obj):
        return obj.user_profile.user.get_full_name()
    get_student_name.short_description = 'دانش‌آموز'

    class Media:
        js = ('admin/js/score-form.js',)

@admin.register(StudentScore)
class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_subject', 'get_class', 'score', 'date')
    list_filter = ('subject__grade__school', 'subject__grade', 'class_obj', 'date')
    search_fields = ('user_profile__user__first_name',
                    'user_profile__user__last_name',
                    'user_profile__melli_code',
                    'subject__name',
                    'class_obj__name')
    ordering = ('-date', 'user_profile__user__last_name')
    raw_id_fields = ('user_profile',)

    def get_student_name(self, obj):
        return obj.user_profile.user.get_full_name()
    get_student_name.short_description = 'دانش‌آموز'

    def get_subject(self, obj):
        return obj.subject.name
    get_subject.short_description = 'درس'

    def get_class(self, obj):
        return obj.class_obj.name
    get_class.short_description = 'کلاس'

# Register models in the desired order
admin_site.register(School, SchoolAdmin)
admin_site.register(Grade, GradeAdmin)
admin_site.register(Subject, SubjectAdmin)
admin_site.register(Class, ClassAdmin)
admin_site.register(Score, ScoreAdmin)
admin_site.register(StudentScore, StudentScoreAdmin)

# The admin.register decorator already registers these models with the default admin site
# So we don't need to register them again
