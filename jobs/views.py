from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import RegistrationForm, JobForm
from .models import RecruiterProfile, JobSeekerProfile, Job, Application

@login_required
def dashboard_view(request):
    user = request.user
    if user.user_type == 'jobseeker':
        profile, created = JobSeekerProfile.objects.get_or_create(user=user)
        matched_jobs = []
        if profile.skills:
            seeker_skills = [s.strip().lower() for s in profile.skills.split(',')]
            for job in Job.objects.all():
                if job.skills_required:
                    job_skills = [s.strip().lower() for s in job.skills_required.split(',')]
                    if any(skill in seeker_skills for skill in job_skills):
                        matched_jobs.append(job)
        
        
        applied_job_ids = request.user.applications.values_list('job_id', flat=True)
        return render(request, 'jobs/seeker_dashboard.html', {
            'matched_jobs': matched_jobs, 
            'profile': profile,
            'applied_job_ids': applied_job_ids
        })
        
    elif user.user_type == 'recruiter':
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        my_posted_jobs = Job.objects.filter(recruiter=user)
        return render(request, 'jobs/recruiter_dashboard.html', {'jobs': my_posted_jobs, 'profile': profile})
    return render(request, 'jobs/base.html')


@login_required
def apply_job(request, job_id):
    if request.user.user_type != 'jobseeker':
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('dashboard')
        
    job = get_object_or_404(Job, id=job_id)
    
    
    already_applied = Application.objects.filter(job=job, jobseeker=request.user).exists()
    if already_applied:
        messages.warning(request, "You have already applied to this position.")
    else:
        Application.objects.create(job=job, jobseeker=request.user)
        messages.success(request, f"Application for '{job.title}' submitted successfully!")
        
    return redirect('dashboard')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            if user.user_type == 'recruiter':
                RecruiterProfile.objects.create(user=user)
            else:
                JobSeekerProfile.objects.create(user=user)
            messages.success(request, 'Registration complete! Welcome aboard.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'jobs/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'jobs/login.html', {'form': form})

@login_required
def job_create(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied: Only recruiters can publish jobs.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, 'Job opening successfully posted!')
            return redirect('dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Post a New Job Opening'})

@login_required
def job_search_view(request):
    query = request.GET.get('q', '')
    results = Job.objects.all()
    if query:
        results = results.filter(Q(title__icontains=query) | Q(category__icontains=query) | Q(description__icontains=query))
    
    applied_job_ids = request.user.applications.values_list('job_id', flat=True)
    return render(request, 'jobs/job_search.html', {'results': results, 'query': query, 'applied_job_ids': applied_job_ids})

@login_required
def profile_edit_view(request):
    user = request.user
    if user.user_type == 'recruiter':
        profile = user.recruiter_profile
        if request.method == 'POST':
            profile.company_name = request.POST.get('company_name', '')
            profile.company_description = request.POST.get('company_description', '')
            profile.save()
            messages.success(request, "Corporate details saved successfully!")
            return redirect('dashboard')
        return render(request, 'jobs/edit_recruiter.html', {'profile': profile})
    else:
        profile = user.jobseeker_profile
        if request.method == 'POST':
            profile.skills = request.POST.get('skills', '')
            # ➕ Handles file tracking data stream securely for the CV resume document
            if 'resume' in request.FILES:
                profile.resume = request.FILES['resume']
            profile.save()
            messages.success(request, "Skills inventory and resume updated successfully!")
            return redirect('dashboard')
        return render(request, 'jobs/edit_seeker.html', {'profile': profile})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out safely.")
    return redirect('login')
