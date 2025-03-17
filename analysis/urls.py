from django.urls import path
from .views import upload_audio  # Import your view function

urlpatterns = [
    path('', upload_audio, name='upload_audio'),  # Define the route for your upload page
]
