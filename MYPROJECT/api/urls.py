from django.urls import path  # Import path here
from .views import ClientListView, ClientDetailView, ProjectCreateView, UserProjectsView

urlpatterns = [
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:client_id>/projects/', ProjectCreateView.as_view(), name='project-create'),
    path('projects/', UserProjectsView.as_view(), name='user-projects'),
]
