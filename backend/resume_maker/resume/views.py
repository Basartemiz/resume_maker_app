from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pathlib import Path
import json

from .utils.parser import parse_resume_input
from .models import ResumeModel, ResumeJson
from .templates.template import create_pdf
# Create your views here.


class ResumeView(APIView):
    """
    POST: Generate a PDF resume from raw user input text.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get user input
        user_input = request.data.get("user_input", "")
        if not user_input:
            return Response({"error": "Missing user_input"}, status=400)
        print(user_input)
        # Parse and normalize
        normalized_data = parse_resume_input(user_input)

        # Create model entry
        resume_model = ResumeModel.objects.create(
            user=request.user,
            user_input=user_input
        )
        resume_json = ResumeJson.objects.create(
            user=request.user,
            json_input=normalized_data
        )
        # Create PDF
        template_name = request.data.get("template_name", "harward_style")
        css_name = request.data.get("css_name", "harward")
        pdf_path = create_pdf(normalized_data, template_name=template_name, css_name=css_name)

        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resume.pdf"'
            return response


class ResumeJsonView(APIView):
    """
    POST: Parse raw resume text and return normalized JSON.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_input = request.data.get("user_input", "")
        if not user_input:
            return Response({"error": "Missing user_input"}, status=400)
        resume_json = ResumeJson.objects.create(
                user=request.user,
                json_input=normalized_data
        )
        normalized_data = parse_resume_input(user_input)
        return Response(normalized_data)

class ResumePdfFromJsonView(APIView):
    """
    POST: Generate a PDF resume from a JSON input.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        json_input = request.data.get("json_input", "{}")

        try:
            normalized_data = json.loads(json_input)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON input"}, status=400)

        # Create PDF
        template_name = request.data.get("template_name", "harward_style")
        css_name = request.data.get("css_name", "harward")
        pdf_path = create_pdf(normalized_data, template_name=template_name, css_name=css_name)

        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resume.pdf"'
            return response




