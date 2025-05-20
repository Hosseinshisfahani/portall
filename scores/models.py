from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from gym.models import UserProfile

class School(models.Model):
    name = models.CharField(max_length=200, verbose_name='نام مدرسه')
    address = models.TextField(verbose_name='آدرس')
    phone = models.CharField(max_length=20, verbose_name='شماره تماس')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'مدرسه'
        verbose_name_plural = 'مدارس'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Grade(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grades', verbose_name='مدرسه')
    name = models.CharField(max_length=50, verbose_name='پایه تحصیلی')
    order = models.IntegerField(verbose_name='ترتیب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'پایه تحصیلی'
        verbose_name_plural = 'پایه‌های تحصیلی'
        ordering = ['school', 'order']
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.school.name}"

class Subject(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects', verbose_name='پایه تحصیلی')
    name = models.CharField(max_length=100, verbose_name='نام درس')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'درس‌ها'
        ordering = ['grade', 'name']
        unique_together = ['grade', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.grade.name}"

class Class(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes', verbose_name='پایه تحصیلی')
    name = models.CharField(max_length=50, verbose_name='نام کلاس')
    student_count = models.PositiveIntegerField(default=0, verbose_name='تعداد دانش‌آموزان')
    students = models.ManyToManyField(User, related_name='enrolled_classes', blank=True, verbose_name='دانش‌آموزان')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'کلاس'
        verbose_name_plural = 'کلاس‌ها'
        ordering = ['grade', 'name']
        unique_together = ['grade', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.grade.name}"

class Score(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='scores', verbose_name='دانش‌آموز')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores', verbose_name='درس')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='scores', verbose_name='کلاس')
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name='نمره'
    )
    date = models.DateField(verbose_name='تاریخ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'نمره'
        verbose_name_plural = 'نمرات'
        ordering = ['-date', 'user_profile']
        unique_together = ['user_profile', 'subject', 'date']
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.subject.name}: {self.score}"

class StudentScore(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='دانش‌آموز')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='درس')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='کلاس')
    score = models.DecimalField(max_digits=4, decimal_places=2, 
                              validators=[MinValueValidator(0), MaxValueValidator(20)],
                              verbose_name='نمره')
    date = models.DateField(verbose_name='تاریخ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    
    class Meta:
        db_table = 'gym_studentscore'
        verbose_name = 'نمره دانش‌آموز'
        verbose_name_plural = 'نمرات دانش‌آموزان'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.subject.name}: {self.score}"
