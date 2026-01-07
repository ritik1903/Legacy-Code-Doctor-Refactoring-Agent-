from django.contrib import admin
from django.urls import path
from core.views import RefactorAPI, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/refactor/', RefactorAPI.as_view()),  # Our new endpoint
    path('', index, name='home'),  # Serve the index page
]