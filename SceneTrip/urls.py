from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include("accounts.urls")),
    path('api/journals/', include("journals.urls")),
    path('api/communities/', include("communities.urls")),
    path('api/locations/', include("locations.urls")),
    path('api/questions/', include("questions.urls")),
    path('api/chats/', include('chats.urls')),
]