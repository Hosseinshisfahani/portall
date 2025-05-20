from django.core.management.base import BaseCommand
import pandas as pd

class Command(BaseCommand):
    help = 'Read and display Excel file content'

    def handle(self, *args, **kwargs):
        try:
            # Read the Excel file
            self.stdout.write('Reading Excel file...')
            df = pd.read_excel('/root/Gym_web/Book1.xlsx')
            
            # Display column names
            self.stdout.write('\nColumn names in Excel:')
            for col in df.columns:
                self.stdout.write(f'- {col}')
            
            # Display first few rows
            self.stdout.write('\nFirst 3 rows of data:')
            for index, row in df.head(3).iterrows():
                self.stdout.write(f'\nRow {index + 1}:')
                for col in df.columns:
                    self.stdout.write(f'{col}: {row[col]}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 