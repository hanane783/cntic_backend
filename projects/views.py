from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import ValidationError
from .models import Project
from decorators import verified_and_paid_required, verified_required, paid_required,group_required
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiExample
@extend_schema(
    description="List all projects for verified users",
    responses={200: "Paginated list of projects"}
)
class ProjectListView(APIView):
    @verified_required
    def get(self, request):
        projects = Project.objects.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(projects, request)
        projects_data = result_page.values('id', 'title', 'description', 'image', 'votes_count')
        return paginator.get_paginated_response(list(projects_data))

class VoteProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @verified_and_paid_required
    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            project.add_vote(request.user)
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": f"Vote cast successfully for '{project.title}'",
                "votes_count": project.votes_count
            },
            status=status.HTTP_200_OK
        )
  
  
@extend_schema(
    description="Get paginated list of projects with optional search (Admin only)",
    parameters=[
        {"name": "project", "type": str, "required": False, "description": "Search by project title"}
    ],
    responses={200: "Paginated list of projects"})
@api_view(['GET'])
@group_required('Admin')
def projects_list(request):
    search_project = request.GET.get('project')
    projects = Project.objects.filter(title__icontains=search_project) if search_project else Project.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(projects, request)
    projects_data = [
        {"id": p.id, "title": p.title, "description": p.description,
         "owner": p.owner.username, "votes_count": p.votes_count} for p in result_page
    ]
    return paginator.get_paginated_response(projects_data)

@extend_schema(
    description="Add a new project (Admin only)",
    request={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "image": {"type": "string"}
        },
        "required": ["title", "description", "image"]
    },
    responses={201: {"message": "Project added", "project_id": "int"}}
)
@api_view(['POST'])
@group_required('Admin')
def add_project(request):
    title = request.data.get('title')
    description = request.data.get('description')
    image = request.data.get('image')
    if not all([title, description, image]):
        return Response({"error": "All fields required"}, status=400)
    project = Project.objects.create(title=title, description=description, image=image, owner=request.user)
    return Response({"message": "Project added", "project_id": project.id}, status=201)

@extend_schema(
    description="Get overall stats and top 3 projects (Admin only)",
    responses={
        200: {
            "stats": {"total_users": "int", "total_projects": "int", "total_votes": "int"},
            "top_projects": [{"id": "int", "title": "string", "votes_count": "int"}]
        }
    }
)
@api_view(['GET'])
@group_required('Admin')
def stats(request):
    total_users = Account.objects.count()
    total_projects = Project.objects.count()
    total_votes = Project.objects.aggregate(total_votes=models.Sum('votes_count'))['total_votes'] or 0
    top_projects = Project.objects.order_by('-votes_count')[:3]
    top_projects_data = [{"id": p.id, "title": p.title, "votes_count": p.votes_count} for p in top_projects]
    return Response({
        "stats": {"total_users": total_users, "total_projects": total_projects, "total_votes": total_votes},
        "top_projects": top_projects_data
    })       