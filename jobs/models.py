from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('recruiter', 'Recruiter'),
        ('jobseeker', 'Job Seeker'),
    )
    display_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.username


class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name if self.company_name else self.user.username


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated items (e.g. Python, Django)")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'recruiter'})
    title = models.CharField(max_length=200)
    number_of_openings = models.IntegerField(default=1)
    category = models.CharField(max_length=100)
    description = models.TextField()
    skills_required = models.CharField(max_length=500, help_text="Comma-separated required skills tags list")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    jobseeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'jobseeker')

    def __str__(self):
        return f"{self.jobseeker.username} applied to {self.job.title}"
