from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tablib import Dataset

class BaseUploadAPIView(APIView):
    parser_class = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    resource_class = None

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        dataset = Dataset()
        try:
            fmt = "xlsx" if file_obj.name.endswith('.xlsx') else "csv"
            data = dataset.load(file_obj.read() if fmt == 'xlsx' else file_obj.read().decode("utf-8"), format=fmt)
        except Exception as e:
            return Response({'error': str(e)})

        resource = self.resource_class()
        result = resource.import_data(data, dry_run=True)
        if result.has_errors():
            return Response({'errors': result.errors})
        resource.import_data(data, dry_run=False)
        return Response(
            {
                'success': True,
                'message': 'Uploaded successfully',
            }
        )