from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Project
from .serializers import ClientSerializer, ProjectSerializer
from django.contrib.auth.models import User

class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save(created_by=request.user)
            return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientDetailView(APIView):
    def get(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            serializer = ClientSerializer(client)
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            if client.created_by != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            serializer = ClientSerializer(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            if client.created_by != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

class ProjectCreateView(APIView):
    def post(self, request, client_id):
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['client'] = client.id
        data['created_by'] = request.user.id
        serializer = ProjectSerializer(data=data)

        if serializer.is_valid():
            project = serializer.save()
            if 'users' in request.data:
                project.users.set(User.objects.filter(id__in=request.data['users']))
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProjectsView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        projects = request.user.projects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

