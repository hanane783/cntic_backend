from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import ValidationError
from .models import Project
from decorators import verified_and_paid_required, verified_required, paid_required


class ProjectListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @verified_required
    def get(self, request):
        projects = Project.objects.all().values('id', 'title', 'description', 'image', 'votes_count')
        return Response(list(projects), status=status.HTTP_200_OK)


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
        from django.http import HttpResponse

def home(request):
    return HttpResponse("API is running 🚀")