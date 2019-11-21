from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class User(AbstractUser):
    age = models.IntegerField(
        validators=(MinValueValidator(0, '올바른 나이를 입력해주세요.'),
                    MaxValueValidator(200, '올바른 나이를 입력해주세요.')
                    ),
        null=True
        )  # 나이를 validator로 검증, 선택 정보
    thumbnail = models.CharField(max_length=500)  # 썸네일 기본값 필요

    def __str__(self):
        return self.username
