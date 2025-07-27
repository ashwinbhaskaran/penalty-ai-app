from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .models import UploadedVideo
from django.contrib import messages

def home(request):
    return HttpResponse("✅ Welcome to Penalty AI App! Test successful.")

def home_view(request):
    return render(request, 'home.html')

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get('video_file')

        if uploaded_file and not uploaded_file.content_type.startswith('video'):
            messages.error(request, "❌ Only video files are allowed. Please upload a valid video file.")
        elif form.is_valid():
            form.save()
            messages.success(request, "✅ Video uploaded successfully!")
            return redirect('upload_video')
        else:
            messages.error(request, "❌ Something went wrong. Please try again.")
    else:
        form = VideoUploadForm()
    
    videos = UploadedVideo.objects.all().order_by('-uploaded_at')
    return render(request, 'upload_video.html', {'form': form, 'videos': videos})
