from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from django.contrib import messages
from django.db.models import Avg
from django.urls import reverse

@receiver(post_save, sender='gym.Certificate')
def handle_certificate_approval(sender, instance, created, **kwargs):
    """
    Signal handler to add scores when a certificate is approved
    """
    if instance.status == 'approved' and not created:
        try:
            user_profile = instance.user.userprofile
            # Get the models using apps.get_model to avoid circular imports
            Score = apps.get_model('scores', 'Score')
            # Get all the user's scores
            user_scores = Score.objects.filter(user_profile=user_profile)
            # Calculate old average
            old_average = user_scores.aggregate(avg=Avg('score'))['avg'] or 0.0
            # Add 2 to all scores
            for score in user_scores:
                score.score += 2
                score.save()
            # Calculate new average
            new_average = user_scores.aggregate(avg=Avg('score'))['avg'] or 0.0
            # Store the grade change information in the certificate
            instance.approval_message = (
                f'۲ نمره به معدل کل شما اضافه شد.\n'
                f'معدل قبلی: {old_average:.2f}\n'
                f'معدل جدید: {new_average:.2f}'
            )
            instance.save(update_fields=['approval_message'])
            print(f"Added 2 points to all scores for {instance.user.username} after certificate approval")
            print(f"Old average: {old_average:.2f}, New average: {new_average:.2f}")
        except Exception as e:
            print(f"Error adding points for certificate approval: {str(e)}") 