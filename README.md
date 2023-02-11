# Mary Talk
서울시 소재 미용실 및 헤어스타일 추천 챗봇

# Overview
본 프로젝트(Mary Talk) 의 목차는 다음과 같습니다.
- [Overview](#overview)
- [프로젝트 목표](#프로젝트-목표)
- [개발 일정](#개발-일정)
- [서비스 사용 샘플](#서비스-사용-샘플)

# 프로젝트 목표
프로젝트 목표 : 서울시에 소재한 미용실에 대한 추천 및 질문답변을 제공하는 챗봇 제작
1. 대화형 헤어샵 추천 서비스
   - 위생 / 서비스 / 분위기 / 위치 / 헤어 관련 만족도 / 기타 총 6개 평가 항목에 대한 자체 Rating System 구축
   - Rating 에 기반한 미용실 추천 기능
2. 미용실 관련 문의사항에 대한 맞춤 답변 제공
   - 위치, 후기, 가격 문의에 대한 상담 기능
3. 사진 검색을 통한 헤어스타일 정보 제공
   - 사용자가 전송한 사진에 해당하는 헤어스타일 정보 제공
   - 추후 해당 헤어스타일에 특화된 미용실 추천으로 서비스 연계 가능

# 개발 일정
2020.04.09. ~ 2020.06.08.

```mermaid
gantt
    title WBS
    dateFormat  YYYY-MM-DD
    section 데이터 수집<br>(전처리)
    미용실 리스트 수집             :2020-04-09, 28d
    텍스트 데이터 수집 (미용실 리뷰)  :2020-04-27, 28d
    이미지 데이터 수집 (헤어스타일)   :2020-04-09, 28d
    section 데이터 분석
    질문 데이터 생성 및 한글 형태소 분석   :2020-05-18, 14d
    분류 모델 생성 및 학습 (질문의도, NER, 이미지)   :2020-05-18, 14d
    section 챗봇 구현
    Flask App 개발 :2020-05-25, 14d
    DB 연동 :2020-05-25, 7d
    카카오 플랫폼 연동 :2020-06-01, 7d
```



# 서비스 사용 샘플
<img src="https://github.com/DongWon-Sehr/project_marytalk/blob/master/sample%20image/marytalk_conversation_20200521_sample1.png" width="500">
<img src="https://github.com/DongWon-Sehr/project_marytalk/blob/master/sample%20image/marytalk_conversation_20200521_sample2.png" width="500">
