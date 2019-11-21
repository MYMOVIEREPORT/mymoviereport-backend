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