from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from food.views import landing_page
urlpatterns = [
    path('admin/', admin.site.urls),
    path('food/', include('food.urls')),  # Include food app URLs
    path('', landing_page, name='landing_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)