from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    #  AUTH + USERS
    path('api/auth/', include('apps.users.urls')),

    #  TICKETS
    path('api/tickets/', include('apps.tickets.urls')),

    #  WORKFLOW
    path('api/workflow/', include('apps.workflow.urls')),

    #  SLA
    path('api/sla/', include('apps.sla.urls')),

    #  QA
    path('api/qa/', include('apps.qa.urls')),

    #  NOTIFICATIONS
    path('api/notifications/', include('apps.notifications.urls')),

    #  REPORTS
    path('api/reports/', include('apps.reports.urls')),

    # CHANNELS
     path('api/channels/', include('apps.channels.urls')),

    # AUDIT LOGS
     path('api/audit/', include('apps.audit_logs.urls')),

     #Locations
     path('api/locations/', include('apps.locations.urls')),
     #categories
     path('api/categories/', include('apps.categories.urls')),
     #priority
     path('api/priorities/', include('apps.priorities.urls')),
     #roles
     path("api/roles/", include("apps.roles.urls")),
     #permissions
    path("api/", include("apps.faqs.urls")),
  
  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)