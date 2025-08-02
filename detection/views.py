from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .models import UploadedVideo
from django.contrib import messages
from django.conf import settings
import os

from .video_processor import extract_frames, process_video

def home(request):
    return HttpResponse("✅ Welcome to Penalty AI App! Test successful.")

def home_view(request):
    return render(request, 'home.html')

def upload_video(request):
    if request.method == 'POST':
        print("📥 POST request received.")
        form = VideoUploadForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get('video_file')

        print(f"📁 uploaded_file: {uploaded_file}")
        print(f"✅ form.is_valid(): {form.is_valid()}")

        if uploaded_file and not uploaded_file.content_type.startswith('video'):
            print("⛔ Invalid file type.")
            messages.error(request, "❌ Only video files are allowed. Please upload a valid video file.")
        elif form.is_valid():
            try:
                video_instance = form.save()
                print(f"💾 Saved video instance: {video_instance}")

                video_path = os.path.join(settings.MEDIA_ROOT, str(video_instance.video_file))
                output_dir = os.path.join(settings.MEDIA_ROOT, 'frames', os.path.splitext(video_instance.video_file.name)[0])

                # Processed video name (matching codec output, e.g., .avi)
                processed_name = f"processed_{os.path.splitext(uploaded_file.name)[0]}.avi"
                processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_name)
                os.makedirs(os.path.dirname(processed_path), exist_ok=True)

                print("🧠 Extracting frames...")
                frame_count = extract_frames(video_path, output_dir)
                print(f"🖼️ Extracted {frame_count} frames.")

                print("🔍 Running MediaPipe processing + behavior analysis...")
                success, behavior_summary = process_video(video_path, processed_path)

                if success:
                    print("✅ Processing complete. Behavior summary:", behavior_summary)
                    processed_video_url = settings.MEDIA_URL + f"processed/{processed_name}"
                    messages.success(request, f"✅ Uploaded, extracted {frame_count} frames, and processed!")

                    return render(request, 'detection_result.html', {
                        'video_title': video_instance.title,
                        'processed_video_url': processed_video_url,
                        'frame_count': frame_count,
                        'behavior_summary': behavior_summary,
                    })
                else:
                    print("⚠️ MediaPipe processing failed.")
                    messages.error(request, "⚠️ Upload succeeded, but processing failed.")
            except Exception as e:
                print(f"🚨 Exception during processing: {e}")
                messages.error(request, f"🚨 Upload succeeded, but processing failed: {e}")
        else:
            print("⛔ Form invalid!")
            messages.error(request, "❌ Something went wrong. Please try again.")
    else:
        form = VideoUploadForm()

    videos = UploadedVideo.objects.all().order_by('-uploaded_at')
    return render(request, 'upload_video.html', {
        'form': form,
        'videos': videos
    })
