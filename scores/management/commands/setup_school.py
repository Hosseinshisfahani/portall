from django.core.management.base import BaseCommand
from scores.models import School, Grade, Class, Subject

class Command(BaseCommand):
    help = 'Set up school, grade, class, and subject'

    def handle(self, *args, **kwargs):
        try:
            # Create or get the school
            school, created = School.objects.get_or_create(
                name='خوارزمی',
                defaults={
                    'address': 'آدرس مدرسه خوارزمی',
                    'phone': '---'
                }
            )
            self.stdout.write(self.style.SUCCESS(
                f'School {"created" if created else "already exists"}: {school.name}'
            ))

            # Create or get the grade
            grade, created = Grade.objects.get_or_create(
                name='هفتم',
                school=school
            )
            self.stdout.write(self.style.SUCCESS(
                f'Grade {"created" if created else "already exists"}: {grade.name}'
            ))

            # Create or get the class
            class_obj, created = Class.objects.get_or_create(
                name='الف',
                grade=grade
            )
            self.stdout.write(self.style.SUCCESS(
                f'Class {"created" if created else "already exists"}: {class_obj.name}'
            ))

            # Create or get the subject
            subject, created = Subject.objects.get_or_create(
                name='عربی',
                grade=grade
            )
            self.stdout.write(self.style.SUCCESS(
                f'Subject {"created" if created else "already exists"}: {subject.name}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 