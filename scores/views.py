from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from scores.models import Score, StudentScore, Subject, Class
from gym.models import UserProfile
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Grade, Class, School
from django.views.decorators.http import require_GET
from django.db.models import Avg, Q, Count, F
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def scores(request):
    user_profile = request.user.userprofile
    context = {}
    
    # Admin view
    if request.user.is_staff:
        # Get all schools for filtering
        schools = School.objects.all()
        selected_school = request.GET.get('school')
        selected_grade = request.GET.get('grade')
        selected_class = request.GET.get('class')
        search_query = request.GET.get('search', '')
        
        # Get all available options for form dropdowns
        all_students = UserProfile.objects.all()
        all_subjects = Subject.objects.all()
        all_classes = Class.objects.all()
        
        # Base queryset
        scores = Score.objects.select_related(
            'user_profile', 'subject', 'class_obj',
            'subject__grade', 'subject__grade__school'
        ).all()
        
        # Apply filters
        if selected_school:
            scores = scores.filter(subject__grade__school_id=selected_school)
            # Get grades for selected school
            grades = Grade.objects.filter(school_id=selected_school)
            context['grades'] = grades
            
            if selected_grade:
                scores = scores.filter(subject__grade_id=selected_grade)
                # Get classes for selected grade
                classes = Class.objects.filter(grade_id=selected_grade)
                context['classes'] = classes
                
                if selected_class:
                    scores = scores.filter(class_obj_id=selected_class)
        
        # Apply search
        if search_query:
            scores = scores.filter(
                Q(user_profile__full_name__icontains=search_query) |
                Q(user_profile__melli_code__icontains=search_query)
            )
        
        # Calculate statistics
        total_students = scores.values('user_profile').distinct().count()
        total_subjects = scores.values('subject').distinct().count()
        avg_score = scores.aggregate(avg=Avg('score'))['avg']
        
        # Get score distribution
        score_distribution = scores.values('score').annotate(
            count=Count('id')
        ).order_by('score')
        
        # Get recent scores (last 30 days)
        recent_scores = scores.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).count()
        
        # Handle score deletion
        if request.method == 'POST' and 'delete_score' in request.POST:
            score_id = request.POST.get('score_id')
            try:
                score = Score.objects.get(id=score_id)
                score.delete()
                messages.success(request, 'نمره با موفقیت حذف شد.')
            except Score.DoesNotExist:
                messages.error(request, 'نمره مورد نظر یافت نشد.')
            return redirect('scores:scores')
        
        # Handle score addition/editing
        if request.method == 'POST' and ('add_score' in request.POST or 'edit_score' in request.POST):
            score_id = request.POST.get('score_id')
            student_id = request.POST.get('student')
            subject_id = request.POST.get('subject')
            class_id = request.POST.get('class_obj')
            score_value = request.POST.get('score')
            date = request.POST.get('date')
            description = request.POST.get('description')
            
            try:
                if score_id:  # Editing existing score
                    score = Score.objects.get(id=score_id)
                else:  # Adding new score
                    score = Score()
                
                score.user_profile = UserProfile.objects.get(id=student_id)
                score.subject = Subject.objects.get(id=subject_id)
                score.class_obj = Class.objects.get(id=class_id)
                score.score = score_value
                score.date = date or timezone.now().date()
                score.description = description
                score.save()
                
                messages.success(request, 'نمره با موفقیت ذخیره شد.')
                return redirect('scores:scores')
            except Exception as e:
                messages.error(request, f'خطا در ذخیره نمره: {str(e)}')
        
        context.update({
            'scores': scores,
            'schools': schools,
            'all_students': all_students,
            'all_subjects': all_subjects,
            'all_classes': all_classes,
            'selected_school': selected_school,
            'selected_grade': selected_grade,
            'selected_class': selected_class,
            'search_query': search_query,
            'is_admin': True,
            'total_students': total_students,
            'total_subjects': total_subjects,
            'avg_score': avg_score or 0,  # Provide default value
            'score_distribution': score_distribution,
            'recent_scores': recent_scores,
        })
    
    # Student view
    else:
        # Get student's scores with related data
        scores = Score.objects.select_related(
            'subject', 'class_obj', 'subject__grade', 'subject__grade__school'
        ).filter(user_profile=user_profile)
        
        # Calculate average score
        avg_score = scores.aggregate(avg_score=Avg('score'))['avg_score']
        
        # Group scores by subject
        subjects = {}
        for score in scores:
            if score.subject not in subjects:
                subjects[score.subject] = []
            subjects[score.subject].append(score)
        
        # Calculate subject-wise averages
        subject_averages = {}
        for subject, subject_scores in subjects.items():
            subject_averages[subject] = sum(s.score for s in subject_scores) / len(subject_scores)
        
        # Get score trend (last 5 scores)
        recent_scores = scores.order_by('-date')[:5]
        score_trend = [s.score for s in recent_scores]
        
        context.update({
            'scores': scores,
            'subjects': subjects,
            'avg_score': avg_score,
            'is_admin': False,
            'subject_averages': subject_averages,
            'score_trend': score_trend,
        })
    
    return render(request, 'scores/scores.html', context)

@login_required
def add_score(request):
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای این عملیات را ندارید.')
        return redirect('scores:scores')

    if request.method == 'POST':
        user_profile_id = request.POST.get('user_profile')
        subject = request.POST.get('subject')
        score_value = request.POST.get('score')

        try:
            user_profile = UserProfile.objects.get(id=user_profile_id)

            # Check if score already exists
            if Score.objects.filter(user_profile=user_profile, subject=subject).exists():
                messages.error(request, 'نمره برای این دانش‌آموز و درس قبلاً ثبت شده است.')
                return redirect('scores:scores')

            Score.objects.create(
                user_profile=user_profile,
                subject=subject,
                score=score_value
            )
            messages.success(request, 'نمره با موفقیت ثبت شد.')
            return redirect('scores:scores')

        except UserProfile.DoesNotExist:
            messages.error(request, 'اطلاعات وارد شده نامعتبر است.')
            return redirect('scores:scores')

    user_profiles = UserProfile.objects.all()
    context = {
        'user_profiles': user_profiles,
    }
    return render(request, 'scores/add_score.html', context)

@login_required
def edit_score(request, score_id):
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای این عملیات را ندارید.')
        return redirect('scores:scores')

    score = get_object_or_404(Score, id=score_id)

    if request.method == 'POST':
        score_value = request.POST.get('score')
        score.score = score_value
        score.save()
        messages.success(request, 'نمره با موفقیت ویرایش شد.')
        return redirect('scores:scores')

    context = {
        'score': score,
    }
    return render(request, 'scores/edit_score.html', context)

@login_required
def delete_score(request, score_id):
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای این عملیات را ندارید.')
        return redirect('scores:scores')

    if request.method == 'POST':
        score = get_object_or_404(Score, id=score_id)
        score.delete()
        messages.success(request, 'نمره با موفقیت حذف شد.')
    return redirect('scores:scores')

@staff_member_required
def get_grades(request):
    school_id = request.GET.get('school_id')
    grades = Grade.objects.filter(school_id=school_id).values('id', 'name')
    return JsonResponse({'grades': list(grades)})

@require_GET
def get_subjects(request):
    grade_id = request.GET.get('grade_id')
    if not grade_id:
        return JsonResponse([], safe=False)
    
    subjects = Subject.objects.filter(grade_id=grade_id)
    data = [{'id': s.id, 'name': s.name} for s in subjects]
    return JsonResponse(data, safe=False)

@require_GET
def get_classes(request):
    grade_id = request.GET.get('grade_id')
    if not grade_id:
        return JsonResponse([], safe=False)
    
    classes = Class.objects.filter(grade_id=grade_id)
    data = [{'id': c.id, 'name': c.name} for c in classes]
    return JsonResponse(data, safe=False)

@require_GET
def get_students(request):
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse([], safe=False)
    
    students = UserProfile.objects.filter(class_obj_id=class_id)
    data = [{'id': s.id, 'full_name': f"{s.user.first_name} {s.user.last_name}"} for s in students]
    return JsonResponse(data, safe=False)

@staff_member_required
def manage_students(request):
    search_query = request.GET.get('search', '')
    students = UserProfile.objects.select_related('user').prefetch_related(
        'user__enrolled_classes',
        'user__enrolled_classes__grade',
        'user__enrolled_classes__grade__school'
    ).all()
    
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(melli_code__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Get all schools, grades, and classes for filtering
    schools = School.objects.all()
    grades = Grade.objects.all()
    classes = Class.objects.all()
    
    # Get filter parameters
    selected_school = request.GET.get('school')
    selected_grade = request.GET.get('grade')
    selected_class = request.GET.get('class')
    
    # Apply filters
    if selected_class:
        students = students.filter(user__enrolled_classes=selected_class)
    elif selected_grade:
        students = students.filter(user__enrolled_classes__grade=selected_grade)
    elif selected_school:
        students = students.filter(user__enrolled_classes__grade__school=selected_school)
    
    context = {
        'students': students,
        'schools': schools,
        'grades': grades,
        'classes': classes,
        'search_query': search_query,
        'selected_school': selected_school,
        'selected_grade': selected_grade,
        'selected_class': selected_class,
    }
    return render(request, 'scores/manage_students.html', context)