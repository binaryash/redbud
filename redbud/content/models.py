from django.db import models
from users.models import User, Training


class ContentType(models.TextChoices):
    PDF = 'pdf', 'PDF Document'
    VIDEO = 'video', 'Video'
    YOUTUBE = 'youtube', 'YouTube Link'
    LINK = 'link', 'External Link'
    TEXT = 'text', 'Text Content'


class Content(models.Model):
    """
    Content model to store training materials
    """
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices)

    # File upload for PDFs and other documents
    file = models.FileField(upload_to='training_content/', blank=True, null=True)

    # For YouTube links and external links
    url = models.URLField(max_length=500, blank=True, null=True)

    # For text content
    text_content = models.TextField(blank=True, null=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contents')
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['training', 'order']
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'

    def __str__(self):
        return f"{self.training.name} - {self.title}"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validate that appropriate field is filled based on content_type
        if self.content_type in ['pdf', 'video']:
            if not self.file:
                raise ValidationError(f'File is required for {self.content_type} content type')
        elif self.content_type in ['youtube', 'link']:
            if not self.url:
                raise ValidationError(f'URL is required for {self.content_type} content type')
        elif self.content_type == 'text':
            if not self.text_content:
                raise ValidationError('Text content is required for text content type')
