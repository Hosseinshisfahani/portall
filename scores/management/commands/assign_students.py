from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scores.models import School, Grade, Class
import pandas as pd

class Command(BaseCommand):
    help = 'Assign imported students to their class'

    def handle(self, *args, **kwargs):
        try:
            # Get the class
            school = School.objects.get(name='خوارزمی')
            grade = Grade.objects.get(name='هفتم', school=school)
            class_obj = Class.objects.get(name='الف', grade=grade)
            
            # Read the Excel file to get melli_codes
            df = pd.read_excel('/root/Gym_web/Book1.xlsx')
            
            # Process each row
            success_count = 0
            for index, row in df.iterrows():
                try:
                    melli_code = str(row['کدملی']).strip()
                    if not melli_code.isdigit() or len(melli_code) != 10:
                        self.stdout.write(self.style.WARNING(
                            f'Skipping invalid melli_code: {melli_code}'
                        ))
                        continue
                    
                    user = User.objects.get(username=melli_code)
                    class_obj.students.add(user)
                    success_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Added student {user.userprofile.full_name} to class {class_obj.name}'
                    ))
                    
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'User not found for melli_code: {melli_code}'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error processing melli_code {melli_code}: {str(e)}'
                    ))
            
            self.stdout.write(self.style.SUCCESS(
                f'\nSuccessfully assigned {success_count} students to class {class_obj.name}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 