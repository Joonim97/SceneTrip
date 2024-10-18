from django.contrib import admin
from django.urls import path, include
from locations import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/accounts/', include("accounts.urls")),
    path('api/journals/', include("journals.urls")),
    path('api/communities/', include("communities.urls")),
    path('api/locations/', include("locations.urls")),
    path('api/questions/', include("questions.urls")),
    path('api/chats/', include('chats.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


