from django.contrib import admin
from django.urls import path, include

import tests.web.views

urlpatterns = [
    path('api/', include(
        [
            path('test/ping', tests.web.views.Tests.as_view()),
            path('user/', include('apps.account.urls')),
            path('chat/', include('apps.chat.urls')),


        ],
    )),
    path('admin/', admin.site.urls),
]
