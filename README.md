# README

## 마이무비리스트 백엔드

> 개발하기 너무 어려운 걸;;

### 개발 과정

#### 1. modeling

![image-20191121154302807](README.assets/image-20191121154302807.png)

> ERD

### 오류 및 해결

- serializer에서 `In order to allow non-dict objects to be serialized set the safe parameter to False.`가 발생하는 경우
  - `return JsonResponse()`에서 `safe=False`라는 속성을 부여해야합니다.
- 유저 항목 입력 시 주의사항
  - 선호 장르 추천과 같이 모델에 직접적인 수정이 필요한 경우 이를 따로 분리하여 연결하는 쪽이 유리합니다.
- 비밀번호 암호화하기
  - `passlib`를 install하고 `passlib.hash`내부에 존재하는 `django_pbkdf2_sha256`을 사용하여 암호화를 합니다.
  - `serializer`를 잠시 중단하고 password를 암호화한 뒤 `serializer`를 저장하면 완료!