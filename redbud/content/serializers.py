#!/usr/bin/env python3

from rest_framework import serializers
from .models import Content
from users.serializers import UserListSerializer
from typing import Optional

class ContentSerializer(serializers.ModelSerializer):
    """
    Serializer for Content model
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    training_name = serializers.CharField(source='training.name', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'training', 'training_name', 'title', 'description',
                  'content_type', 'content_type_display', 'file', 'file_url',
                  'url', 'text_content', 'order', 'is_active',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_file_url(self, obj)-> Optional[str]:
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None

    def validate(self, data):
        """
        Validate that appropriate field is filled based on content_type
        """
        content_type = data.get('content_type')

        if content_type in ['pdf', 'video']:
            if not data.get('file'):
                raise serializers.ValidationError(
                    f'File is required for {content_type} content type'
                )
        elif content_type in ['youtube', 'link']:
            if not data.get('url'):
                raise serializers.ValidationError(
                    f'URL is required for {content_type} content type'
                )
        elif content_type == 'text':
            if not data.get('text_content'):
                raise serializers.ValidationError(
                    'Text content is required for text content type'
                )

        return data


class ContentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing contents
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    training_name = serializers.CharField(source='training.name', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)

    class Meta:
        model = Content
        fields = ['id', 'training', 'training_name', 'title', 'content_type',
                  'content_type_display', 'order', 'is_active', 'created_by_name', 'created_at']



# Add this to the existing serializers.py file

class ContentSummarySerializer(serializers.Serializer):
    """
    Serializer for content summary responses
    """
    summary = serializers.CharField(read_only=True)
    content_id = serializers.IntegerField(read_only=True)
    content_type = serializers.CharField(read_only=True)
    max_length = serializers.IntegerField(required=False, min_value=50, max_value=1000)

    class Meta:
        fields = ['summary', 'content_id', 'content_type', 'max_length']
