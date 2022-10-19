import base64
import binascii
import imghdr
import io
import uuid

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_representation(self, file):
        return self.context.get('request').build_absolute_uri(file.url)

    def to_internal_value(self, data):
        if isinstance(data, str):
            file_mime_type = None
            if ';base64,' in data:
                header, base64_data = data.split(';base64,')
                if 'data:' in header:
                    file_mime_type = header.replace('data:', '')

            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(_('Загрузите корректную картинку.'))

            file_name = self.get_file_name(decoded_file)
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = file_name + '.' + file_extension
            data = SimpleUploadedFile(
                name=complete_file_name,
                content=decoded_file,
                content_type=file_mime_type
            )

            return super().to_internal_value(data)

        raise ValidationError(
            _(f'Не правильный тип. Необходима строка base64, '
              f'использован: {type(data)}'))

    @staticmethod
    def get_file_extension(filename, decoded_file):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError('Pillow не установлен.')
        extension = imghdr.what(filename, decoded_file)
        if extension is None:
            try:
                image = Image.open(io.BytesIO(decoded_file))
            except OSError:
                raise ValidationError(_('Загрузите подходящую картинку.'))
            extension = image.format.lower()
        extension = 'jpg' if extension == 'jpeg' else extension
        return extension

    @staticmethod
    def get_file_name(decoded_file):
        return str(uuid.uuid4())
