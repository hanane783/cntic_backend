from django.urls import path
from .views import ProjectListView, VoteProjectView, projects_list, add_project, stats

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('<int:project_id>/vote/', VoteProjectView.as_view(), name='vote_project'),

    path('admin/projects/', projects_list, name='admin-projects-list'),
    path('admin/projects/add/', add_project, name='admin-add-project'),
    path('admin/stats/', stats, name='admin-stats'),

]