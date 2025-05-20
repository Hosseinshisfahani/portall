from django.contrib import admin
from .models import Exam, Question, ExamRegistration, UserAnswer, SiteSettings, ExamPayment

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'payment_card_number', 'payment_card_owner')
    fieldsets = (
        ('تنظیمات پرداخت', {
            'fields': ('payment_card_number', 'payment_card_owner', 'payment_description')
        }),
    )
    
    def has_add_permission(self, request):
        # Check if a settings object already exists
        return not SiteSettings.objects.exists()
        
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings
        return False

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'grade', 'field', 'duration_minutes', 'price', 'status', 'question_count', 'registered_count')
    list_filter = ('status', 'course', 'grade', 'field')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'status')
        }),
        ('جزئیات', {
            'fields': ('course', 'grade', 'field', 'duration_minutes', 'price')
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'question_type', 'short_text', 'order')
    list_filter = ('exam', 'question_type')
    search_fields = ('text',)
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'متن سوال'

@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'status', 'created_at')
    list_filter = ('status', 'exam')
    search_fields = ('user__username', 'exam__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'exam', 'status', 'admin_note')
        }),
        ('اطلاعات پرداخت', {
            'fields': ('payment_image', 'card_number')
        }),
        ('زمان‌ها', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Check if the status has changed to 'approved'
        if change and 'status' in form.changed_data and obj.status == 'approved':
            # Check if a payment record already exists for this registration
            if not ExamPayment.objects.filter(registration=obj).exists():
                # Create a new ExamPayment record
                ExamPayment.objects.create(
                    user=obj.user,
                    exam=obj.exam,
                    registration=obj,
                    amount=obj.exam.price,
                    payment_image=obj.payment_image
                )
        super().save_model(request, obj, form, change)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('registration', 'question', 'viewed_answer', 'created_at')
    list_filter = ('registration__exam', 'viewed_answer')
    search_fields = ('registration__user__username', 'question__text')
    readonly_fields = ('created_at',)

admin.site.register(ExamPayment) 