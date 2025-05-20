from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import json

class SiteSettings(models.Model):
    """Model for storing global site settings"""
    payment_card_number = models.CharField(max_length=16, verbose_name='شماره کارت پرداخت', 
                                          help_text='شماره کارت که به کاربران نمایش داده می‌شود (بدون فاصله وارد کنید: مثلا 6104338968423552)')
    payment_card_owner = models.CharField(max_length=100, verbose_name='نام صاحب کارت', blank=True, null=True)
    payment_description = models.TextField(verbose_name='توضیحات پرداخت', blank=True, null=True, 
                                           help_text='توضیحات پرداخت که به کاربران نمایش داده می‌شود')

    class Meta:
        verbose_name = 'تنظیمات پرداخت'
        verbose_name_plural = 'تنظیمات پرداخت'

    def save(self, *args, **kwargs):
        """Only allow a single instance of SiteSettings"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the single settings instance"""
        pass

    @classmethod
    def load(cls):
        """Load or create the site settings"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
        
    def __str__(self):
        return "تنظیمات پرداخت"


class Exam(models.Model):
    """Model for online exams"""

    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
        ('archived', 'آرشیو شده'),
    )

    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    course = models.CharField(max_length=100, verbose_name='درس')
    grade = models.CharField(max_length=100, verbose_name='پایه')
    field = models.CharField(max_length=100, verbose_name='رشته')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    price = models.PositiveIntegerField(verbose_name='قیمت (تومان)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'آزمون'
        verbose_name_plural = 'آزمون‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        """Returns the number of questions in this exam"""
        return self.question_set.count()

    @property
    def registered_count(self):
        """Returns the number of users registered for this exam"""
        return self.examregistration_set.count()


class Question(models.Model):
    """Model for exam questions"""

    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', 'چندگزینه‌ای'),
        ('descriptive', 'تشریحی'),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='آزمون')
    text = models.TextField(verbose_name='متن سوال')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='descriptive', verbose_name='نوع سوال')
    options = models.JSONField(null=True, blank=True, verbose_name='گزینه‌ها')
    answer = models.TextField(verbose_name='پاسخ')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')

    class Meta:
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'
        ordering = ['exam', 'order']

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text


class ExamRegistration(models.Model):
    """Model for exam registrations"""

    STATUS_CHOICES = (
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('completed', 'تکمیل شده'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='آزمون')
    payment_image = models.ImageField(upload_to='exams/payments/', verbose_name='تصویر پرداخت')
    card_number = models.CharField(max_length=16, verbose_name='شماره کارت', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    admin_note = models.TextField(blank=True, null=True, verbose_name='یادداشت مدیر')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان شروع')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان پایان')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'ثبت‌نام آزمون'
        verbose_name_plural = 'ثبت‌نام‌های آزمون'
        ordering = ['-created_at']
        unique_together = ['user', 'exam']

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

    @property
    def is_approved(self):
        """Returns True if registration is approved"""
        return self.status == 'approved'

    @property
    def time_remaining_seconds(self):
        """Returns the remaining time in seconds for this exam"""
        if not self.started_at or self.completed_at:
            return self.exam.duration_minutes * 60
        
        # Calculate elapsed time
        elapsed = timezone.now() - self.started_at
        elapsed_seconds = elapsed.total_seconds()
        
        # Calculate remaining time
        total_seconds = self.exam.duration_minutes * 60
        remaining = total_seconds - elapsed_seconds
        
        return max(0, int(remaining))


class UserAnswer(models.Model):
    """Model for tracking user's answers and viewed answers"""

    registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE, verbose_name='ثبت‌نام')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='سوال')
    viewed_answer = models.BooleanField(default=False, verbose_name='پاسخ دیده شده')
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان دیدن پاسخ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'پاسخ کاربر'
        verbose_name_plural = 'پاسخ‌های کاربر'
        ordering = ['registration', 'question__order']
        unique_together = ['registration', 'question']

    def __str__(self):
        return f"{self.registration.user.username} - {self.question}"

    def save(self, *args, **kwargs):
        """Override save to update viewed_at timestamp"""
        if self.viewed_answer and not self.viewed_at:
            self.viewed_at = timezone.now()
        super().save(*args, **kwargs)


class ExamPayment(models.Model):
    """Model for recording payments for exams"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='آزمون')
    registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE, verbose_name='ثبت‌نام')
    amount = models.PositiveIntegerField(verbose_name='مبلغ پرداختی (تومان)')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پرداخت')
    payment_image = models.ImageField(upload_to='exams/payments/', verbose_name='تصویر پرداخت', blank=True, null=True)

    class Meta:
        verbose_name = 'پرداخت آزمون'
        verbose_name_plural = 'پرداخت‌های آزمون'
        ordering = ['-payment_date']

    def __str__(self):
        return f"پرداخت {self.amount} تومان برای {self.exam.title} توسط {self.user.username}" 