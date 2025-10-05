# Daily English Mecca - 웹 버전 개발 계획

## 📋 개요

CLI 버전을 웹 애플리케이션으로 전환하여 더 쉽고 편리하게 사용할 수 있도록 개발

---

## 🎯 목표

- **사용 편의성**: 브라우저에서 클릭만으로 영상 제작
- **실시간 피드백**: 진행 상황을 시각적으로 표시
- **결과 관리**: 생성된 영상 미리보기 및 다운로드
- **배치 처리**: 여러 영상을 한번에 제작 (향후)

---

## 🛠 기술 스택

### 백엔드
- **Flask**: 경량 Python 웹 프레임워크
- **Flask-CORS**: CORS 처리
- **기존 모듈**: 현재 개발한 모든 모듈 재사용

### 프론트엔드
- **HTML5**: 구조
- **CSS3**: 스타일링 (반응형 디자인)
- **JavaScript (Vanilla)**: 인터랙션
- **Fetch API**: 백엔드 통신

---

## 📂 프로젝트 구조 (웹 버전)

```
daily-english-mecca/
├── src/                          # 기존 모듈 (재사용)
│   ├── image_generator.py
│   ├── tts_generator.py
│   ├── content_analyzer.py
│   ├── youtube_metadata.py
│   └── video_creator.py
├── web/                          # 웹 버전 추가
│   ├── app.py                    # Flask 메인 앱
│   ├── static/                   # 정적 파일
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   │       └── logo.png
│   └── templates/                # HTML 템플릿
│       ├── index.html            # 메인 페이지
│       ├── create.html           # 영상 생성 페이지
│       └── result.html           # 결과 페이지
├── output/                       # 생성된 파일
├── main.py                       # CLI 버전 (유지)
├── requirements.txt              # 패키지 목록 (Flask 추가)
└── README.md
```

---

## 🎨 UI/UX 설계

### 1. 메인 페이지 (index.html)
- **헤더**: Daily English Mecca 로고 + 소개
- **입력 폼**:
  - 문장 1 입력란
  - 문장 2 입력란
  - 문장 3 입력란
  - [영상 생성] 버튼
- **옵션 설정** (접기/펼치기):
  - 음성 선택 (nova, alloy, shimmer)
  - 비디오 스타일 (향후)

### 2. 생성 진행 페이지 (create.html)
- **진행 상황 표시**:
  - ⏳ 문장 분석 중... (10%)
  - ⏳ 이미지 생성 중... (30%)
  - ⏳ 음성 생성 중... (60%)
  - ⏳ 비디오 생성 중... (80%)
  - ⏳ 메타정보 생성 중... (90%)
  - ✅ 완료! (100%)
- **프로그레스 바**
- **로그 출력** (실시간)

### 3. 결과 페이지 (result.html)
- **비디오 플레이어**: 생성된 영상 미리보기
- **메타정보 표시**:
  - 제목
  - 설명
  - 태그
- **다운로드 버튼**:
  - 비디오 다운로드
  - 메타정보 다운로드 (JSON)
- **새로운 영상 만들기** 버튼

---

## 🔌 API 엔드포인트 설계

### POST /api/generate
**요청**:
```json
{
  "sentences": [
    "I'm going to spend time with family.",
    "I plan to hang out with my loved ones.",
    "I prefer to have some alone time."
  ],
  "voice": "nova"
}
```

**응답**:
```json
{
  "task_id": "20251005_143022",
  "status": "processing"
}
```

### GET /api/status/<task_id>
**응답**:
```json
{
  "task_id": "20251005_143022",
  "status": "processing",
  "progress": 60,
  "current_step": "음성 생성 중...",
  "logs": [
    "✅ 문장 분석 완료",
    "✅ 이미지 2개 생성 완료",
    "⏳ 음성 생성 중..."
  ]
}
```

### GET /api/result/<task_id>
**응답**:
```json
{
  "task_id": "20251005_143022",
  "status": "completed",
  "video_url": "/output/videos/daily_english_20251005_143022.mp4",
  "metadata": {
    "title": "매일 3문장 영어회화 | 가족과 함께하는 시간 🌟",
    "description": "...",
    "tags": ["영어회화", "영어공부", ...]
  }
}
```

### GET /api/download/<task_id>/<file_type>
- `file_type`: `video` 또는 `metadata`
- 파일 다운로드

---

## 🔄 작업 흐름 (Workflow)

### 사용자 관점
1. 웹사이트 접속
2. 3개 문장 입력
3. [영상 생성] 버튼 클릭
4. 진행 상황 확인 (실시간 업데이트)
5. 완료 후 영상 미리보기
6. 다운로드 또는 유튜브 업로드

### 시스템 관점
1. 사용자가 폼 제출
2. Flask가 요청 받음
3. 백그라운드 태스크로 영상 생성 시작
4. 진행 상황을 DB/파일에 저장
5. 프론트엔드가 주기적으로 상태 확인 (폴링)
6. 완료 시 결과 페이지로 리디렉션

---

## 📦 추가 패키지

requirements.txt에 추가 필요:
```
flask>=3.0.0
flask-cors>=4.0.0
```

---

## 🚀 개발 단계

### Phase 1: 백엔드 개발
- [x] 웹 개발 계획 수립
- [ ] Flask 앱 기본 구조 생성
- [ ] API 엔드포인트 개발
  - [ ] POST /api/generate
  - [ ] GET /api/status/<task_id>
  - [ ] GET /api/result/<task_id>
  - [ ] GET /api/download/<task_id>/<file_type>
- [ ] 백그라운드 작업 처리 (threading)
- [ ] 진행 상황 추적 시스템

### Phase 2: 프론트엔드 개발
- [ ] HTML 템플릿 작성
  - [ ] index.html (메인)
  - [ ] create.html (진행 상황)
  - [ ] result.html (결과)
- [ ] CSS 스타일링
  - [ ] 반응형 디자인
  - [ ] 모던한 UI
- [ ] JavaScript 개발
  - [ ] 폼 제출 처리
  - [ ] 진행 상황 폴링
  - [ ] 결과 표시

### Phase 3: 통합 및 테스트
- [ ] 백엔드-프론트엔드 통합
- [ ] 실제 테스트 실행
- [ ] 버그 수정
- [ ] 성능 최적화

### Phase 4: 배포 준비
- [ ] 프로덕션 설정
- [ ] README 업데이트 (웹 버전 추가)
- [ ] 배포 가이드 작성

---

## 📊 예상 일정

- **Phase 1 (백엔드)**: 2-3시간
- **Phase 2 (프론트엔드)**: 2-3시간
- **Phase 3 (통합/테스트)**: 1-2시간
- **Phase 4 (배포)**: 1시간

**총 예상 시간**: 6-9시간

---

## 💡 향후 개선 사항

### v1.1
- [ ] 배치 처리 (CSV 업로드)
- [ ] 사용자 계정 시스템
- [ ] 생성 히스토리 관리

### v1.2
- [ ] 유튜브 자동 업로드
- [ ] 템플릿 시스템 (다양한 스타일)
- [ ] A/B 테스팅

### v2.0
- [ ] React/Vue.js로 마이그레이션
- [ ] WebSocket으로 실시간 진행 상황
- [ ] 클라우드 배포 (AWS/GCP)

---

**작성일**: 2025-10-05
**버전**: 1.0
