from django.db import models


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    연번 = models.IntegerField()
    미디어타입 = models.CharField(max_length=20)
    제목 = models.CharField(max_length=300)
    장소명 = models.CharField(max_length=300)
    장소타입 = models.CharField(max_length=100)
    장소설명 = models.TextField(max_length=300)
    영업시간 = models.TextField(max_length=300)
    브레이크타임 = models.CharField(max_length=100)
    휴무일 = models.CharField(max_length=100)
    주소 = models.CharField(max_length=300)
    위도 = models.FloatField(max_length=8)
    경도 = models.FloatField(max_length=10)
    전화번호 = models.CharField(max_length=20)
    최종작성일 = models.CharField(max_length=10)

    # def __str__(self):
    #     return self.제목

    class Meta:
        managed = False
        app_label = "locationdata"
        db_table = "location"
