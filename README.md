##  🏨 위앤비 [We&B] _ wecode 35기 2차 프로젝트
- 위코드에서 2차 팀 프로젝트로 진했던 프로젝트에 기능을 추가하여 업그레이드 해봤습니다.
- 구현한 기능 : 호스트 등록하기, 집 등록하기

<br>

## 🏨 Directory 구조
```
.
├── __pycache__
├── core
├── hosts
├── reservations
├── reviews
├── rooms
├── users
└── wnb
```
<br>

## 🏨 구현한 기능
- 카카오 소셜 로그인
    - Oauth2.0을 이용한 카카오 소셜 로그인 구현
    - 로그인시 JWT 발급
    - 회원 유무를 확인하는 token decorator 구현
    - 직접 구현한 API Unit test 적용
- 회원 정보 수정
    - 정규표현식을 사용한 이름, 연락처, 생년월일 유효성 검사 진행
    - 직접 구현한 API Unit test 적용
- 호스트 등록하기
- 집 등록하기
    - boto3를 사용하여 AWS S3 Bucket에 이미지 저장
- git rebase를 활용한 commit 관리
  
  
<br>
   
