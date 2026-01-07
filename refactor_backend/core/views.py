from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import RefactoringAgent
from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')

class RefactorAPI(APIView):
    def post(self, request):
        legacy_code = request.data.get('code')
        if not legacy_code:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize your agent
        agent = RefactoringAgent()
        
        # Run the process
        # Note: This might take 30-60 seconds, so eventually we will need Celery.
        # For now, we keep it simple to test.
        refactored_code = agent.process(legacy_code)

        if refactored_code:
            return Response({
                "status": "success",
                "original_code": legacy_code,
                "refactored_code": refactored_code
            })
        else:
            return Response({
                "status": "failed",
                "message": "Could not safely refactor code."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)