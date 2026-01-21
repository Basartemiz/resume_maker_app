from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pathlib import Path
import json

from .utils.parser import parse_resume_input
from .models import ResumeModel, ResumeJson
from .templates.template import create_pdf
from payment.models import Payment
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
        normalized_data = parse_resume_input(user_input)
        resume_json = ResumeJson.objects.create(
                user=request.user,
                json_input=normalized_data
        )
        return Response(normalized_data)



class ResumePdfFromJsonView(APIView):
    """
    POST: Generate a PDF resume from a JSON input.
    Requires payment verification - payment_id must be provided and valid.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        json_input = request.data.get("json_input", "{}")
        payment_id = request.data.get("payment_id")

        # Verify payment
        if not payment_id:
            return Response({"error": "Payment required. Missing payment_id"}, status=402)

        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        if payment.status != 'succeeded':
            return Response({"error": "Payment not completed"}, status=402)

        if payment.resume_downloaded:
            return Response({"error": "Payment already used for download"}, status=400)

        try:
            normalized_data = json.loads(json_input)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON input"}, status=400)

        # Create PDF
        template_name = request.data.get("template_name", "harward_style")
        css_name = request.data.get("css_name", "harward")

        try:
            pdf_path = create_pdf(normalized_data, template_name=template_name, css_name=css_name)
        except Exception as e:
            import traceback
            print(f"PDF generation error: {e}")
            print(traceback.format_exc())
            return Response({"error": f"PDF generation failed: {str(e)}"}, status=500)

        # Mark payment as used
        payment.resume_downloaded = True
        payment.save()

        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resume.pdf"'
            return response


class ResumeDataView(APIView):
    """
    GET: Retrieve user's saved resume JSON data.
    POST: Save/update user's resume JSON data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resume = ResumeJson.objects.filter(user=request.user).order_by('-id').first()
        if not resume:
            return Response({"data": None}, status=200)
        return Response({"data": resume.json_input}, status=200)

    def post(self, request):
        json_data = request.data.get("data")
        if not json_data:
            return Response({"error": "Missing data"}, status=400)

        # Update existing or create new
        resume, created = ResumeJson.objects.update_or_create(
            user=request.user,
            defaults={"json_input": json_data}
        )
        return Response({"message": "Resume saved successfully"}, status=200)




