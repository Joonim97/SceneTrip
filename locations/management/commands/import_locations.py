# 데이터베이스 업데이트 시, python manage.py import_locations 실행하여 db에 촬영지 데이터 넣기.
import csv
from locations.models import Location
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **kwargs):
        with open(r"C:\SceneTrip\한국문화정보원_미디어콘텐츠 영상 촬영지 데이터_20221125.csv", newline="", encoding="cp949") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                location, created = Location.objects.update_or_create(
                    title=row["제목"],
                    place_name=row["장소명"],
                    place_description=row["장소설명"],
                    defaults = {
                    'media_type':row["미디어타입"],
                    'title':row["제목"],
                    'place_name':row["장소명"],
                    'place_type':row["장소타입"],
                    'place_description':row["장소설명"],
                    'opening_hours':row["영업시간"],
                    'break_time':row["브레이크타임"] if row["브레이크타임"] else None,
                    'closed_day':row["휴무일"],
                    'address':row["주소"],
                    'latitude':float(row["위도"]),
                    'longitude':float(row["경도"]),
                    'tel':row["전화번호"],
                    'created_at':row["최종작성일"],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new location: {row["제목"]} - {row["장소명"]}'))
