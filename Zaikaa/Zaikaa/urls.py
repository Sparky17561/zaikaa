from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('food/', include('food.urls')),  # Include food app URLs

]
