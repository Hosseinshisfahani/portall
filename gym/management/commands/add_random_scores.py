import random
from django.core.management.base import BaseCommand
from gym.models import UserProfile
from scores.models import Score, Subject, Grade, School, Class
from django.utils import timezone

class Command(BaseCommand):
    help = 'Add random scores for all students'

    def handle(self, *args, **options):
        # Get or create a default school
        school, _ = School.objects.get_or_create(
            name='مدرسه نمونه',
            defaults={'address': 'تهران', 'phone': '021-12345678'}
        )
        
        # Get or create grades
        grades = []
        for grade_name in ['هفتم', 'هشتم', 'نهم']:
            grade, _ = Grade.objects.get_or_create(
                name=grade_name,
                school=school,
                defaults={'order': len(grades) + 1}
            )
            grades.append(grade)
        
        # Get or create subjects
        subjects = []
        subject_names = ['ریاضی', 'علوم', 'ادبیات', 'عربی', 'انگلیسی', 'مطالعات اجتماعی']
        for subject_name in subject_names:
            for grade in grades:
                subject, _ = Subject.objects.get_or_create(
                    name=subject_name,
                    grade=grade,
                    defaults={'description': f'{subject_name} پایه {grade.name}'}
                )
                subjects.append(subject)
        
        # Get or create classes
        classes = []
        for grade in grades:
            for class_num in range(1, 4):  # Create 3 classes per grade
                class_obj, _ = Class.objects.get_or_create(
                    name=f'کلاس {class_num}',
                    grade=grade,
                    defaults={'student_count': 0}
                )
                classes.append(class_obj)
        
        # Get all students
        students = UserProfile.objects.all()
        
        # Add random scores for each student
        for student in students:
            self.stdout.write(f'Adding scores for student: {student.full_name}')
            
            # Randomly select a grade and class for the student
            grade = random.choice(grades)
            class_obj = random.choice([c for c in classes if c.grade == grade])
            
            # Add scores for each subject in the selected grade
            for subject in subjects:
                if subject.grade == grade:
                    # Create score with random values
                    Score.objects.create(
                        user_profile=student,
                        subject=subject,
                        class_obj=class_obj,
                        score=random.uniform(10, 20),  # Random score between 10 and 20
                        date=timezone.now().date(),
                        description=f'نمره {subject.name} برای {student.full_name}'
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Added score for {student.full_name} in {subject.name}'
                    ))
        
        self.stdout.write(self.style.SUCCESS('Successfully added random scores for all students')) 