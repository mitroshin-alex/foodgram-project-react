import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag, Recipe

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка данных из csv в базу данных'

    @staticmethod
    def _read_csv(file_name):
        """Read CSV, return list of row."""
        file_path = os.path.join(settings.DATA_DIR, file_name)
        with open(file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', )
            result = [row for row in csv_reader]
        return result or None

    @staticmethod
    def _process_date(csv_data, foreign_keys=()):
        """Rename column if foreign key and create list of dict."""
        result = []
        if foreign_keys:
            csv_data[0] = [column + '_id'
                           if column in foreign_keys else column
                           for column in csv_data[0]]
        for index in range(1, len(csv_data)):
            result.append(dict(zip(csv_data[0], csv_data[index])))
        return result

    @staticmethod
    def _write_to_model(model, data, defaults={}):
        """Create or update objects in model."""
        for row in data:
            if model == User:
                password = row.pop('password')
            created = model.objects.update_or_create(**row, defaults=defaults)
            if model == User:
                created[0].set_password(password)
                created[0].save()
            print(f'{created} - {row}')

    def _process_file(self, model, file_name,
                      foreign_keys=(), extra_update=()):
        """Processing file and create/update objects."""
        data_raw = self._read_csv(file_name)
        data = self._process_date(data_raw, foreign_keys)
        if extra_update:
            for obj in data:
                update = {}
                for column in extra_update:
                    update['id'] = obj['id']
                    update[column] = obj.pop(column)
                self._write_to_model(model, [obj])
                self._write_to_model(model, [obj], defaults=update)
        else:
            self._write_to_model(model, data)

    @staticmethod
    def _write_to_many_to_many_model(model1, model2, data, foreign_keys):
        """Create or update objects in many to many table."""
        for row in data:
            obj_1 = model1.objects.get(id=row[foreign_keys[0]])
            obj_2 = model2.objects.get(id=row[foreign_keys[1]])
            getattr(obj_1, foreign_keys[1].split('_')[0]).add(obj_2)
            obj_1.save()
            print(f'update - {obj_1} in many to many {" ".join(foreign_keys)}')

    def _processing_many_to_many_file(self, model1, model2,
                                      file_name, foreign_keys=()):
        """Processing file and create/update objects in many to many table."""
        data_raw = self._read_csv(file_name)
        data = self._process_date(data_raw)
        self._write_to_many_to_many_model(model1, model2, data, foreign_keys)

    def handle(self, *args, **options):
        self._process_file(User, 'users.csv')
        self._process_file(Ingredient, 'ingredients.csv')
        self._process_file(Tag, 'tags.csv')
        self._process_file(Recipe, 'recipes.csv', ('author',))
