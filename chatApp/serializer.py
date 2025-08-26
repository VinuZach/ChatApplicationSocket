from rest_framework import serializers

from .models import FileAttachment
import os

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = ['fileName', 'uploadedFile', 'uploaded_at',]
        read_only_fields = ['uploaded_at','fileName',]

    def create(self, validated_data):
        validated_data['fileName'] =  self.get_fileName(validated_data.get('uploadedFile'))
        validated_data['file_size'] = self.get_file_size(validated_data.get('uploadedFile'))
        validated_data['file_type'] = self.get_content_type(validated_data.get('uploadedFile'))

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['fileName'] = self.get_fileName(validated_data.get('uploadedFile'))
        return super().update(instance, validated_data)

    def get_fileName(self, obj):
        print(obj)
        """Extract filename from the file field"""
        if obj and hasattr(obj, 'name'):
            return os.path.basename(obj.name)
        return "None"

    def get_content_type(self, obj):
        if obj:
            import os
            name, extension = os.path.splitext(obj.name)
            return extension.lstrip('.')  # Remove leading dot
        return "None"

    def get_file_size(self, obj):
        """Safely get file size"""
        if obj:
            return obj.size




