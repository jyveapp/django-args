from django.contrib import admin
from django.urls import path

from djarg.tests import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'grant-staff-access/',
        views.GrantStaffView.as_view(),
        name='grant_staff_access',
    ),
    path(
        'grant-staff-access-raise-run-errors/',
        views.GrantStaffView.as_view(raise_run_errors=True),
        name='grant_staff_access_raise_run_errors',
    ),
    path(
        'grant-staff-access-object/<int:pk>/',
        views.GrantStaffObjectView.as_view(),
        name='grant_staff_access_object',
    ),
    path(
        'grant-staff-access-objects/',
        views.GrantStaffObjectsView.as_view(),
        name='grant_staff_access_objects',
    ),
    path(
        'grant-staff-access-wizard/',
        views.GrantStaffWizardView.as_view(),
        name='grant_staff_access_wizard',
    ),
    path(
        'grant-staff-access-wizard-raise-run-errors/',
        views.GrantStaffWizardView.as_view(raise_run_errors=True),
        name='grant_staff_access_wizard_raise_run_errors',
    ),
    path(
        'grant-staff-access-cond-wizard/',
        views.GrantStaffCondWizardView.as_view(),
        name='grant_staff_access_cond_wizard',
    ),
    path(
        'grant-staff-access-object-wizard/<int:pk>/',
        views.GrantStaffObjectWizardView.as_view(),
        name='grant_staff_access_object_wizard',
    ),
]
