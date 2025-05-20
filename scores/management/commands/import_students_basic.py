from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym.models import UserProfile
import pandas as pd
from django.db import transaction

class Command(BaseCommand):
    help = 'Import students from Excel file (basic information only)'

    def handle(self, *args, **kwargs):
        try:
            # Read the Excel file
            df = pd.read_excel('/root/Gym_web/Book1.xlsx')
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    with transaction.atomic():
                        # Get and validate melli_code
                        melli_code = str(row['کدملی']).strip()
                        if not melli_code.isdigit() or len(melli_code) != 10:
                            self.stdout.write(self.style.WARNING(
                                f'Row {index + 1}: Invalid melli_code: {melli_code}'
                            ))
                            continue

                        # Create or get user
                        user, created = User.objects.get_or_create(
                            username=melli_code,
                            defaults={
                                'email': f'{melli_code}@example.com',
                            }
                        )
                        
                        if created:
                            user.set_password(melli_code)  # Set initial password
                            user.save()
                            self.stdout.write(self.style.SUCCESS(
                                f'Row {index + 1}: Created new user: {melli_code}'
                            ))
                        else:
                            self.stdout.write(self.style.SUCCESS(
                                f'Row {index + 1}: User already exists: {melli_code}'
                            ))

                        # Create or update UserProfile
                        profile, prof_created = UserProfile.objects.get_or_create(
                            user=user,
                            defaults={
                                'melli_code': melli_code,
                                'full_name': row['نام و نام خانوادگی'],
                                'father_name': row['نام پدر'],
                            }
                        )
                        
                        if not prof_created:
                            # Update existing profile
                            profile.full_name = row['نام و نام خانوادگی']
                            profile.father_name = row['نام پدر']
                            profile.save()

                        self.stdout.write(self.style.SUCCESS(
                            f'Row {index + 1}: {"Created" if prof_created else "Updated"} profile for: {profile.full_name}'
                        ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error processing row {index + 1}: {str(e)}'
                    ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 