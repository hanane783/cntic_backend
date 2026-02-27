from django.urls import path
from .views import ProjectListView, VoteProjectView

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('<int:project_id>/vote/', VoteProjectView.as_view(), name='vote_project'),
]