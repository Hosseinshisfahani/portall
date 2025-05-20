from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym.models import UserProfile
from scores.models import School, Grade, Class, Subject
import pandas as pd
from django.db import transaction

class Command(BaseCommand):
    help = 'Import students from Excel file'

    def handle(self, *args, **kwargs):
        try:
            # Create or get the school
            school, _ = School.objects.get_or_create(
                name='خوارزمی',
                defaults={
                    'address': 'آدرس مدرسه خوارزمی',
                    'phone': '---'
                }
            )
            self.stdout.write(self.style.SUCCESS(f'School: {school.name}'))

            # Create or get the grade
            grade, _ = Grade.objects.get_or_create(
                name='هفتم',
                school=school
            )
            self.stdout.write(self.style.SUCCESS(f'Grade: {grade.name}'))

            # Create or get the class
            class_obj, _ = Class.objects.get_or_create(
                name='الف',
                grade=grade
            )
            self.stdout.write(self.style.SUCCESS(f'Class: {class_obj.name}'))

            # Create or get the subject
            subject, _ = Subject.objects.get_or_create(
                name='عربی',
                grade=grade
            )
            self.stdout.write(self.style.SUCCESS(f'Subject: {subject.name}'))

            # Read the Excel file
            df = pd.read_excel('Book1.xlsx')
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    with transaction.atomic():
                        # Create user with melli_code as username
                        melli_code = str(row['کد ملی']).strip()
                        if not melli_code.isdigit() or len(melli_code) != 10:
                            self.stdout.write(self.style.WARNING(f'Invalid melli_code: {melli_code}'))
                            continue

                        # Create or get user
                        user, created = User.objects.get_or_create(
                            username=melli_code,
                            defaults={
                                'email': f'{melli_code}@example.com',  # Temporary email
                                'password': melli_code  # Temporary password
                            }
                        )
                        
                        if created:
                            user.set_password(melli_code)  # Set proper hashed password
                            user.save()

                        # Create or update UserProfile
                        profile, _ = UserProfile.objects.get_or_create(
                            user=user,
                            defaults={
                                'melli_code': melli_code,
                                'full_name': row['نام و نام خانوادگی'],
                                'father_name': row['نام پدر'],
                                'birth_year': row.get('سال تولد', None),
                                'phone_number': str(row.get('شماره تلفن', '')),
                            }
                        )

                        # Add student to the class
                        class_obj.students.add(user)

                        self.stdout.write(self.style.SUCCESS(
                            f'Successfully processed student: {profile.full_name}'
                        ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error processing row {index}: {str(e)}'
                    ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 