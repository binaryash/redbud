from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from content.models import Content
from content.serializers import ContentSerializer, ContentListSerializer, ContentSummarySerializer
from content.permissions import IsManagerOrTrainerForContent
from users.models import Training
from content.gemini_service import get_gemini_service


@extend_schema_view(
    list=extend_schema(
        summary="List training content",
        description="Get a list of training content based on user permissions. Supports filtering by training and content type.",
        tags=['Content']
    ),
    retrieve=extend_schema(
        summary="Get content details",
        description="Retrieve detailed information about specific training content.",
        tags=['Content']
    ),
    create=extend_schema(
        summary="Create training content",
        description="Create new training content - PDF, video, YouTube link, external link, or text (Manager or assigned Trainer).",
        tags=['Content']
    ),
    update=extend_schema(
        summary="Update training content",
        description="Update training content (Manager or assigned Trainer).",
        tags=['Content']
    ),
    destroy=extend_schema(
        summary="Delete training content",
        description="Delete training content (Manager or assigned Trainer).",
        tags=['Content']
    ),
)
class ContentViewSet(viewsets.ModelViewSet):
    """ViewSet for Content management with file upload support."""

    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsManagerOrTrainerForContent]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return ContentListSerializer
        return ContentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'manager':
            return Content.objects.all()
        elif user.role == 'trainer':
            training_ids = Training.objects.filter(assigned_trainer=user).values_list('id', flat=True)
            return Content.objects.filter(training_id__in=training_ids)
        else:
            training_ids = user.trainings.values_list('id', flat=True)
            return Content.objects.filter(training_id__in=training_ids, is_active=True)

    def perform_create(self, serializer):
        training = serializer.validated_data.get('training')
        user = self.request.user

        if user.role == 'trainer' and training.assigned_trainer != user:
            return Response(
                {'error': 'You can only add content to your assigned trainings'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Get content by training",
        description="Filter content by training ID.",
        parameters=[
            OpenApiParameter(
                name='training_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by training ID',
                required=True
            )
        ],
        responses={200: ContentSerializer(many=True)},
        tags=['Content']
    )
    @action(detail=False, methods=['get'])
    def by_training(self, request):
        """Get content filtered by training ID"""
        training_id = request.query_params.get('training_id', None)
        if training_id:
            contents = self.get_queryset().filter(training_id=training_id)
            serializer = self.get_serializer(contents, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'training_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Get content by type",
        description="Filter content by content type (pdf, video, youtube, link, text).",
        parameters=[
            OpenApiParameter(
                name='content_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by content type',
                enum=['pdf', 'video', 'youtube', 'link', 'text'],
                required=True
            )
        ],
        responses={200: ContentSerializer(many=True)},
        tags=['Content']
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get content filtered by content type"""
        content_type = request.query_params.get('content_type', None)
        if content_type:
            contents = self.get_queryset().filter(content_type=content_type)
            serializer = self.get_serializer(contents, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'content_type parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Toggle content active status",
        description="Toggle the is_active status of content (Manager or assigned Trainer only).",
        responses={200: ContentSerializer},
        tags=['Content']
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle is_active status of content"""
        content = self.get_object()
        content.is_active = not content.is_active
        content.save()
        serializer = self.get_serializer(content)
        return Response(serializer.data)














    # Add this method to your ContentViewSet class

    @extend_schema(
        summary="Summarize content",
        description="Generate AI-powered summary of text or PDF content using Gemini API. Available to all authenticated users.",
        request=ContentSummarySerializer,
        responses={
            200: ContentSummarySerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        },
        tags=['Content'],
        methods=['POST']
    )
    @action(detail=True, methods=['post'], url_path='summarize', url_name='summarize')
    def summarize(self, request, pk=None):
        """Generate AI summary for content (text or PDF only)"""
        content = self.get_object()

        # Validate content type
        if content.content_type not in ['text', 'pdf']:
            return Response(
                {'error': 'Summarization is only supported for text and PDF content'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get optional max_length parameter
        max_length = request.data.get('max_length', None)
        if max_length:
            try:
                max_length = int(max_length)
                if max_length < 50 or max_length > 1000:
                    return Response(
                        {'error': 'max_length must be between 50 and 1000'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'max_length must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            gemini_service = get_gemini_service()

            if content.content_type == 'text':
                if not content.text_content:
                    return Response(
                        {'error': 'No text content available to summarize'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                summary = gemini_service.summarize_text(content.text_content, max_length)

            elif content.content_type == 'pdf':
                if not content.file:
                    return Response(
                        {'error': 'No PDF file available to summarize'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                pdf_path = content.file.path
                summary = gemini_service.summarize_pdf(pdf_path, max_length)

            response_data = {
                'summary': summary,
                'content_id': content.id,
                'content_type': content.content_type,
            }

            if max_length:
                response_data['max_length'] = max_length

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate summary: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
