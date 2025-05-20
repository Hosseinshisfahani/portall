from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import random
import json

from .models import Exam, ExamRegistration, Question, UserAnswer, SiteSettings, ExamPayment
from .forms import ExamRegistrationForm


@login_required
def exam_list(request):
    """View for listing all available exams"""
    
    try:
        # Get published exams only
        exams = Exam.objects.filter(status='published')
        
        # Get user's registrations
        user_registrations = ExamRegistration.objects.filter(user=request.user)
        
        # Create a dictionary mapping exam IDs to registration status
        registration_status = {reg.exam_id: reg.status for reg in user_registrations}
        
        # Get all exams the user can take (approved registrations)
        approved_exams = [reg.exam for reg in user_registrations.filter(status='approved', completed_at__isnull=True)]
        
        context = {
            'exams': exams,
            'registration_status': registration_status,
            'approved_exams': approved_exams,
        }
        
        return render(request, 'exams/exam_list.html', context)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error in exam_list view: {str(e)}<br><pre>{tb}</pre>", status=500)


@login_required
def exam_detail(request, exam_id):
    """View for showing exam details and registration form"""
    
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Load site settings for payment information
    site_settings = SiteSettings.load()
    
    # Check if user is already registered
    try:
        registration = ExamRegistration.objects.get(user=request.user, exam=exam)
        
        # If registration is approved and not completed, redirect to exam page
        if registration.status == 'approved' and not registration.completed_at:
            return redirect('exams:take_exam', registration_id=registration.id)
            
    except ExamRegistration.DoesNotExist:
        registration = None
    
    # Handle registration form
    if request.method == 'POST' and not registration:
        form = ExamRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.exam = exam
            # Set card_number to empty string since it's not in the form anymore
            registration.card_number = ""
            registration.save()
            
            messages.success(request, 'ثبت‌نام شما برای آزمون با موفقیت انجام شد. پس از تایید پرداخت، می‌توانید در آزمون شرکت کنید.')
            return redirect('exams:exam_list')
    else:
        form = ExamRegistrationForm()
    
    context = {
        'exam': exam,
        'registration': registration,
        'form': form,
        'settings': site_settings,
    }
    
    return render(request, 'exams/exam_detail.html', context)


@login_required
def my_exams(request):
    """View for showing user's registered exams"""
    
    # Get user's registrations
    registrations = ExamRegistration.objects.filter(user=request.user)
    
    context = {
        'registrations': registrations,
    }
    
    return render(request, 'exams/my_exams.html', context)


@login_required
def take_exam(request, registration_id, question=None):
    """View for taking an exam"""
    
    try:
        # Get registration or return 404
        registration = get_object_or_404(ExamRegistration, id=registration_id, user=request.user)
        exam = registration.exam
        
        # Check if user is allowed to take the exam
        if registration.status != 'approved':
            messages.error(request, 'شما نمی‌توانید در این آزمون شرکت کنید. ثبت‌نام شما تایید نشده است.')
            return redirect('exams:exam_list')
        
        # Check if exam is already completed
        if registration.completed_at:
            messages.info(request, 'شما قبلاً این آزمون را به پایان رسانده‌اید.')
            return redirect('exams:exam_list')
        
        # Start the exam if not started already
        if not registration.started_at:
            registration.started_at = timezone.now()
            registration.save()
        
        # Check if time is up
        if registration.time_remaining_seconds <= 0:
            registration.completed_at = timezone.now()
            registration.status = 'completed'
            registration.save()
            messages.info(request, 'زمان آزمون به پایان رسیده است.')
            return redirect('exams:exam_list')
        
        # Get all questions for this exam
        questions = list(Question.objects.filter(exam=exam))
        
        # Check if the exam has any questions
        if not questions:
            messages.warning(request, 'این آزمون فاقد سوال می‌باشد. لطفا با مدیر سیستم تماس بگیرید.')
            return redirect('exams:exam_list')
        
        # Get or create session key for storing question order
        session_key = f'exam_{registration_id}_question_order'
        
        # Use stored question order or create a new shuffled order
        if session_key not in request.session:
            # Create a shuffled order of question IDs
            question_ids = [q.id for q in questions]
            random.shuffle(question_ids)
            request.session[session_key] = question_ids
        
        question_order = request.session[session_key]
        
        # Get current question index from URL or query parameters
        if question is not None:
            # Question passed in URL
            current_index = int(question)
        else:
            # Check if question passed as GET parameter
            current_index = request.GET.get('question')
            if current_index is not None:
                current_index = int(current_index)
            else:
                current_index = 0
                
        # Validate index range
        if current_index < 0 or current_index >= len(question_order):
            current_index = 0
        
        # Get the current question by ID
        current_question_id = question_order[current_index]
        current_question = next((q for q in questions if q.id == current_question_id), questions[0])
        
        # Get or create user answers for all questions
        user_answers = {}
        for question in questions:
            answer, created = UserAnswer.objects.get_or_create(
                registration=registration,
                question=question
            )
            user_answers[question.id] = answer
        
        context = {
            'registration': registration,
            'exam': exam,
            'questions': questions,
            'current_question': current_question,
            'current_index': current_index,
            'total_questions': len(questions),
            'user_answers': user_answers,
            'time_remaining': registration.time_remaining_seconds,
            'next_index': min(current_index + 1, len(questions) - 1),
            'prev_index': max(current_index - 1, 0),
            'question_navigator_range': range(len(questions)),
        }
        
        return render(request, 'exams/take_exam.html', context)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error in take_exam view: {str(e)}<br><pre>{tb}</pre>", status=500)


@login_required
def view_answer(request, registration_id, question_id):
    """API endpoint for viewing a question's answer"""
    
    # Accept both GET and POST for debugging
    if request.method not in ['POST', 'GET']:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        # Get registration and question or return 404
        registration = get_object_or_404(ExamRegistration, id=registration_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, exam=registration.exam)
        
        # Check if user is allowed to view the answer
        if registration.status != 'approved' and registration.status != 'completed':
            return JsonResponse({'error': 'You are not allowed to view this answer'}, status=403)
        
        # Get or create user answer
        user_answer, created = UserAnswer.objects.get_or_create(
            registration=registration,
            question=question
        )
        
        # Mark answer as viewed
        user_answer.viewed_answer = True
        user_answer.save()
        
        # Return the answer
        return JsonResponse({
            'answer': question.answer,
            'question_type': question.question_type
        })
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JsonResponse({'error': str(e), 'traceback': tb}, status=500)


@login_required
@csrf_exempt
def complete_exam(request, registration_id):
    """View for completing an exam - supports both AJAX and regular form submissions"""
    
    # Get registration or return 404
    registration = get_object_or_404(ExamRegistration, id=registration_id, user=request.user)
    
    # Check if user is allowed to complete the exam
    if registration.status != 'approved':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You are not allowed to complete this exam'}, status=403)
        else:
            messages.error(request, 'شما مجاز به پایان دادن این آزمون نیستید.')
            return redirect('exams:take_exam', registration_id=registration_id)
    
    # Check if exam is already completed
    if registration.completed_at:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'This exam is already completed'}, status=400)
        else:
            messages.info(request, 'این آزمون قبلاً به پایان رسیده است.')
            return redirect('exams:exam_list')
    
    # Mark exam as completed
    registration.completed_at = timezone.now()
    registration.status = 'completed'
    registration.save()
    
    # Handle based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        messages.success(request, 'آزمون با موفقیت به پایان رسید.')
        return redirect('exams:exam_list')


# Admin views

@login_required
def manage_exams(request):
    """Admin view for managing exams"""
    
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای مدیریت آزمون‌ها را ندارید.')
        return redirect('exams:exam_list')
    
    # Get all exams
    exams = Exam.objects.all()
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        exams = exams.filter(status=status)
    
    # Search by title or description if provided
    search = request.GET.get('search')
    if search:
        exams = exams.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    # Paginate results
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'exams/admin/manage_exams.html', context)


@login_required
def manage_registrations(request):
    """Admin view for managing exam registrations"""
    
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای مدیریت ثبت‌نام‌های آزمون را ندارید.')
        return redirect('exams:exam_list')
    
    # Get all registrations
    registrations = ExamRegistration.objects.all()
    
    # Filter by exam if provided
    exam_id = request.GET.get('exam')
    if exam_id:
        registrations = registrations.filter(exam_id=exam_id)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        registrations = registrations.filter(status=status)
    
    # Search by user or exam if provided
    search = request.GET.get('search')
    if search:
        registrations = registrations.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(exam__title__icontains=search)
        )
    
    # Get all exams for filter dropdown
    exams = Exam.objects.all()
    
    # Paginate results
    paginator = Paginator(registrations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'exams': exams,
        'exam_filter': exam_id,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'exams/admin/manage_registrations.html', context)


@login_required
def update_registration_status(request, registration_id):
    """Admin view for updating a registration's status"""
    
    # Check if user is staff
    if not request.user.is_staff:
        return HttpResponseForbidden('شما دسترسی لازم برای این عملیات را ندارید.')
    
    # Get registration or return 404
    registration = get_object_or_404(ExamRegistration, id=registration_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        admin_note = request.POST.get('admin_note', '')
        
        # Update registration status
        if status in [s[0] for s in ExamRegistration.STATUS_CHOICES]:
            old_status = registration.status
            registration.status = status
            registration.admin_note = admin_note
            registration.save()
            
            # Create payment record when status changes to approved
            if status == 'approved' and old_status != 'approved':
                # Check if payment record already exists
                if not ExamPayment.objects.filter(registration=registration).exists():
                    ExamPayment.objects.create(
                        user=registration.user,
                        exam=registration.exam,
                        registration=registration,
                        amount=registration.exam.price,
                        payment_image=registration.payment_image
                    )
            
            messages.success(request, 'وضعیت ثبت‌نام با موفقیت به‌روزرسانی شد.')
        else:
            messages.error(request, 'وضعیت نامعتبر است.')
    
    return redirect('exams:manage_registrations')


@login_required
def import_questions(request):
    """Admin view for importing questions from JSON file"""
    
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی لازم برای وارد کردن سوالات را ندارید.')
        return redirect('exams:exam_list')
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        json_file = request.FILES.get('json_file')
        
        # Check if exam exists
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            messages.error(request, 'آزمون مورد نظر یافت نشد.')
            return redirect('exams:manage_exams')
        
        # Check if file is provided
        if not json_file:
            messages.error(request, 'لطفاً یک فایل JSON انتخاب کنید.')
            return redirect('exams:import_questions')
        
        # Read and parse JSON file
        try:
            data = json.load(json_file)
            questions_data = data.get('questions', [])
            
            # Create questions in a transaction
            with transaction.atomic():
                for i, q_data in enumerate(questions_data):
                    # Determine question type
                    question_type = 'descriptive'
                    if q_data.get('options'):
                        question_type = 'multiple_choice'
                    
                    # Create question
                    Question.objects.create(
                        exam=exam,
                        text=q_data.get('question', ''),
                        question_type=question_type,
                        options=q_data.get('options'),
                        answer=q_data.get('answer', ''),
                        order=i+1
                    )
            
            messages.success(request, f'{len(questions_data)} سوال با موفقیت به آزمون اضافه شد.')
            return redirect('exams:manage_exams')
            
        except Exception as e:
            messages.error(request, f'خطا در وارد کردن سوالات: {str(e)}')
            return redirect('exams:import_questions')
    
    # Get all exams for dropdown
    exams = Exam.objects.all()
    
    context = {
        'exams': exams,
    }
    
    return render(request, 'exams/admin/import_questions.html', context)


def debug_view(request):
    """Debug view to help diagnose issues"""
    from django.http import HttpResponse
    from .models import SiteSettings, Exam
    
    try:
        # Test SiteSettings
        settings = SiteSettings.load()
        card_number = settings.payment_card_number
        
        # Test loading exams
        exams = list(Exam.objects.all())
        exam_count = len(exams)
        
        # Test template tags
        from django.template import Template, Context
        from django.template.loader import get_template
        
        # Return success response
        return HttpResponse(
            f"Debug successful!<br>"
            f"Card number: {card_number}<br>"
            f"Exam count: {exam_count}<br>"
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return HttpResponse(f"Error: {str(e)}<br><pre>{tb}</pre>", status=500)


def simple_exam_list(request):
    """Simple view for listing all available exams without complex logic"""
    
    try:
        # Get published exams only
        exams = Exam.objects.filter(status='published')
        
        # Create a simple HTML response
        html = "<html><head><title>Simple Exam List</title></head><body>"
        html += "<h1>Available Exams</h1>"
        
        if exams:
            html += "<ul>"
            for exam in exams:
                html += f"<li>{exam.title} - {exam.course} - {exam.grade} - {exam.price} تومان</li>"
            html += "</ul>"
        else:
            html += "<p>No exams available</p>"
        
        html += "</body></html>"
        
        from django.http import HttpResponse
        return HttpResponse(html)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error in simple_exam_list view: {str(e)}<br><pre>{tb}</pre>", status=500)


def test_exam_list(request):
    """Very basic test view to diagnose the issue with exam listing"""
    try:
        # Try loading the exams
        exams = list(Exam.objects.filter(status='published'))
        exam_count = len(exams)
        
        # Try loading user registrations
        user_registrations = []
        registration_status = {}
        approved_exams = []
        
        if request.user.is_authenticated:
            user_registrations = list(ExamRegistration.objects.filter(user=request.user))
            registration_status = {reg.exam_id: reg.status for reg in user_registrations}
            approved_exams = [reg.exam for reg in user_registrations.filter(status='approved', completed_at__isnull=True)]
        
        # Create a response with the results
        html = "<html><head><title>Exam List Test</title></head><body>"
        html += "<h1>Exam List Test Results</h1>"
        html += f"<p>Exams found: {exam_count}</p>"
        html += f"<p>User registrations found: {len(user_registrations)}</p>"
        html += f"<p>Registration status: {registration_status}</p>"
        html += f"<p>Approved exams: {len(approved_exams)}</p>"
        
        # Test the template tags
        html += "<h2>Testing get_item filter</h2>"
        for exam_id in registration_status:
            html += f"<p>Exam {exam_id}: {registration_status.get(exam_id)}</p>"
        
        html += "</body></html>"
        
        from django.http import HttpResponse
        return HttpResponse(html)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error in test_exam_list: {str(e)}<br><pre>{tb}</pre>", status=500)


@login_required
def view_answer_direct(request, registration_id, question_id):
    """Direct view for viewing a question's answer - supports both GET and POST requests"""
    
    try:
        # Get registration and question or return 404
        registration = get_object_or_404(ExamRegistration, id=registration_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, exam=registration.exam)
        
        # Check if user is allowed to view the answer
        if registration.status != 'approved' and registration.status != 'completed':
            messages.error(request, 'شما مجاز به مشاهده پاسخ نیستید.')
            return redirect('exams:take_exam', registration_id=registration_id)
        
        # Get or create user answer
        user_answer, created = UserAnswer.objects.get_or_create(
            registration=registration,
            question=question
        )
        
        # Mark answer as viewed
        user_answer.viewed_answer = True
        user_answer.save()
        
        # Add success message
        messages.success(request, 'پاسخ سوال با موفقیت نمایش داده شد.')
        
        # Get current question index from session
        session_key = f'exam_{registration_id}_question_order'
        if session_key in request.session:
            question_order = request.session[session_key]
            
            try:
                # Find the current question index
                current_index = question_order.index(question.id)
                
                # Return to the same question (no auto-navigation)
                # Use the HTTP_REFERER if available to go back to the exact same page
                if 'HTTP_REFERER' in request.META and 'take/' in request.META['HTTP_REFERER']:
                    response = redirect(request.META['HTTP_REFERER'])
                else:
                    response = redirect('exams:take_exam_with_question', 
                                      registration_id=registration_id, 
                                      question=current_index)
                
                # Add no-cache headers
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                return response
            except (ValueError, IndexError) as e:
                print(f"ERROR: {str(e)}")
        
        # Fallback to default exam page
        response = redirect('exams:take_exam', registration_id=registration_id)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    except Exception as e:
        messages.error(request, f'خطا در نمایش پاسخ: {str(e)}')
        response = redirect('exams:take_exam', registration_id=registration_id)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response 