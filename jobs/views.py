from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import RegistrationForm, JobForm
from .models import RecruiterProfile, JobSeekerProfile, Job, Application

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
                
            messages.success(request, 'Registration complete!')
            return redirect('login')
    else:
        form = RegistrationForm()
        
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            typed_username = form.cleaned_data.get('username')
            typed_password = form.cleaned_data.get('password')
            user = authenticate(username=typed_username, password=typed_password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out safely.")
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    
    if user.user_type == 'jobseeker':
        profile, created = JobSeekerProfile.objects.get_or_create(user=user)
        matched_jobs = []
        
        if profile.skills:
            matched_jobs = Job.objects.filter(skills_required__icontains=profile.skills)
            
        applied_job_ids = user.applications.values_list('job_id', flat=True)
        return render(request, 'seeker_dashboard.html', {
            'matched_jobs': matched_jobs,
            'profile': profile,
            'applied_job_ids': applied_job_ids
        })
        
    if user.user_type == 'recruiter':
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        my_posted_jobs = Job.objects.filter(recruiter=user)
        return render(request, 'recruiter_dashboard.html', {
            'jobs': my_posted_jobs, 
            'profile': profile
        })
        
    return render(request, 'base.html')

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
        
    return render(request, 'job_form.html', {'form': form, 'title': 'Post a New Job Opening'})

@login_required
def job_search_view(request):
    query_text = request.GET.get('q', '')
    results = Job.objects.all()
    
    if query_text:
        results = results.filter(
            Q(title__icontains=query_text) | 
            Q(category__icontains=query_text) | 
            Q(description__icontains=query_text)
        )
        
    applied_job_ids = request.user.applications.values_list('job_id', flat=True)
    return render(request, 'job_search.html', {'results': results, 'query': query_text, 'applied_job_ids': applied_job_ids})

@login_required
def apply_job(request, job_id):
    if request.user.user_type != 'jobseeker':
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('dashboard')
        
    target_job = get_object_or_404(Job, id=job_id)
    already_applied = Application.objects.filter(job=target_job, jobseeker=request.user).exists()
    
    if already_applied:
        messages.warning(request, "You have already applied to this position.")
    else:
        Application.objects.create(job=target_job, jobseeker=request.user)
        messages.success(request, f"Application for '{target_job.title}' submitted successfully!")
        
    return redirect('dashboard')

@login_required
def profile_edit_view(request):
    user = request.user
    
    if user.user_type == 'recruiter':
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            profile.company_name = request.POST.get('company_name', '')
            profile.company_description = request.POST.get('company_description', '')
            profile.save()
            messages.success(request, "Corporate details saved successfully!")
            return redirect('dashboard')
        return render(request, 'edit_recruiter.html', {'profile': profile})
        
    if user.user_type == 'jobseeker':
        profile, created = JobSeekerProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            profile.skills = request.POST.get('skills', '')
            
            if 'resume' in request.FILES:
                uploaded_file = request.FILES['resume']
                file_name = uploaded_file.name.lower()
                if file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.doc'):
                    profile.resume = uploaded_file
                else:
                    messages.error(request, "Invalid file type. Only PDF and Word files are allowed.")
                    return render(request, 'edit_seeker.html', {'profile': profile})
                    
            profile.save()
            messages.success(request, "Skills inventory and resume updated successfully!")
            return redirect('dashboard')
            
        return render(request, 'edit_seeker.html', {'profile': profile})