# Daily English Mecca - 개발 컨텍스트 (Claude Code)

**마지막 업데이트**: 2025-10-07
**담당자**: 켈리 & Claude Code

---

## 📌 프로젝트 개요

YouTube Shorts 영어 학습 비디오 자동 생성 시스템
- 9:16 세로 포맷 (1080x1920)
- OpenAI DALL-E 3 이미지 생성 + 캐싱
- OpenAI TTS-1 음성 생성 (3가지 음성: alloy, nova, shimmer)
- GPT-4o-mini 한국어 번역 + AI 바이럴 훅 생성
- MoviePy 2.x 비디오 합성
- Flask 웹 인터페이스
- 인트로/아웃트로 "Daily English Mecca" 브랜딩 (gold stroke)
- 배경 음악 (Kevin MacLeod - Carefree, 5% 볼륨)
- PIL 기반 이미지 회전 로직

---

## 🎯 최근 작업 (2025-10-07)

### ✅ Phase 1: 참여도 향상 (YouTube 알고리즘 최적화)

**목표**: 구독자 8명 → 100명, 좋아요/댓글 증가

**구현 내용:**
1. **AI 자동 생성 바이럴 훅**
   - `ContentAnalyzer.generate_hook_phrase()` 추가
   - GPT-4o-mini (temperature 0.9) 사용
   - 예시: "99% 틀리는 표현", "이거 모르면 손해!"
   - 이모지 제거 로직 (MoviePy TextClip 호환)
   - 인트로 3초에 표시

2. **강화된 CTA (Call-to-Action)**
   - 아웃트로 메시지 변경: "좋아요 & 구독하기!"
   - 댓글 유도 추가: "댓글에 오늘 배운 문장 써보세요!"
   - 참여도 증가 목적

**수정 파일:**
- `src/content_analyzer.py:182-220` - `generate_hook_phrase()` 추가
- `src/video_creator.py:201-288` - 인트로에 AI 훅 적용
- `src/video_creator.py:409-508` - 아웃트로 CTA 강화
- `web/app.py:121-124` - 훅 생성 파이프라인 통합

### ✅ Phase 2: 학습 효과 향상 (반복 학습)

**문제**: 음성이 단조롭고 빠름 → 따라 말할 시간 부족

**구현 내용:**
1. **멀티보이스 TTS 시스템**
   - `TTSGenerator.generate_speech_per_sentence_multi_voice()` 추가
   - 3가지 음성 사용: Alloy (남성), Nova (여성), Shimmer (여성)
   - 각 문장을 3번 반복 (각 반복마다 다른 음성)

2. **간격 증가**
   - 문장 사이 pause: 1초 → 2초
   - 사용자가 따라 말할 시간 확보

3. **데이터 구조 변경**
   ```python
   # OLD:
   [{'path': str, 'duration': float, 'sentence': str}]

   # NEW:
   [{
       'sentence': str,
       'voices': {
           'alloy': {'path': str, 'duration': float},
           'nova': {'path': str, 'duration': float},
           'shimmer': {'path': str, 'duration': float}
       }
   }]
   ```

**수정 파일:**
- `src/tts_generator.py:151-211` - 멀티보이스 생성 함수 추가
- `src/video_creator.py:68-111` - 3회 반복, 음성 교체 로직
- `src/video_creator.py:121` - duration 계산 수정 (KeyError 해결)
- `web/app.py:143-152` - 멀티보이스 TTS 호출

### ✅ 시스템 개선

**1. 이미지 관리 통합**
- **문제**: 이미지가 `output/images`와 `output/resources/images`에 중복 저장
- **해결**:
  - `output/images` 폴더 완전 제거
  - 모든 이미지를 `output/resources/images`에서만 관리
  - 중복 저장 로직 제거
  - 130개 중복 파일 제거
- **수정 파일**:
  - `web/app.py:91-99` - `images_dir` 제거
  - `web/app.py:130-142` - resources 경로로 직접 저장
  - `src/image_generator.py:37-49` - 중복 저장 방지 로직
  - `src/image_generator.py:85-97` - 조건부 캐시 저장

**2. 'duration' KeyError 수정**
- **문제**: Phase 2 데이터 구조 변경으로 OLD 코드에서 KeyError 발생
- **해결**: `audio_info[i]['duration']` → `audio_info[i]['voices']['alloy']['duration']`
- **수정 파일**: `src/video_creator.py:121`

### ✅ Phase 3: 가독성 향상 (동적 폰트 크기)

**문제**:
- 폰트 크기가 고정(42px)되어 짧은 문장은 너무 작고, 긴 문장은 오버플로우 가능성
- 사용자 요구: "글씨가 많을 경우도 생각해야되고"

**구현 내용:**
1. **동적 폰트 크기 계산**
   - `VideoCreator._calculate_font_size()` 메서드 추가
   - 텍스트 길이에 따라 자동 조정:
     - < 50자: 58px (매우 짧은 문장 → 크게)
     - 50-79자: 52px (짧은 문장)
     - 80-119자: 46px (보통 길이)
     - 120-159자: 42px (긴 문장, 기존 기본값)
     - ≥ 160자: 38px (매우 긴 문장 → 작게, 오버플로우 방지)

2. **_create_sentence_clip 업데이트**
   - `combined_text` 길이 기반 폰트 크기 계산
   - `font_size=42` (고정) → `font_size=dynamic_font_size` (동적)

**수정 파일:**
- `src/video_creator.py:290-312` - `_calculate_font_size()` 메서드 추가
- `src/video_creator.py:410-416` - 동적 폰트 크기 적용

**효과:**
- 짧은 문장: 가독성 향상 (폰트 크기 증가)
- 긴 문장: 오버플로우 방지 (폰트 크기 감소)
- 텍스트 박스 크기: 960px (width) × 350px (height)

---

## 🎯 이전 작업 (2025-10-06)

### ✅ 포맷 선택 기능 완성

**3개 포맷 옵션 추가:**
1. **매일 3문장 (Manual)**: 사용자가 직접 3문장 입력 (기존 방식)
2. **테마별 묶음 (Theme)**: AI가 주제별로 3~6문장 자동 생성
   - 8개 테마: 여행/비즈니스/일상/레스토랑/쇼핑/건강/취미/공부
   - OpenAI GPT-4o-mini 사용 (temperature 0.8)
   - 내용에 따라 문장 개수 가변 (3~6개)
3. **다른 포맷 (Other)**: 다양한 학습 형식
   - 스토리 시리즈 (Day 1-7 연결, temperature 0.9)
   - 영화 명대사 (3문장)
   - 발음 집중 훈련 (3문장)
   - 오늘의 뉴스 (3문장)

**핵심 요구사항:**
- **"모듈별로 작성해서. 추가시마다 사이드 이펙트 주지 않도록 개발"**
- **"OpenAI API로 테마별 3문장~6문장 자동 생성(내용에 따라 다를수 있어서)"**

---

## 📂 수정된 파일

### 1. `web/templates/index.html`
- 메인 화면 포맷 선택 UI 추가 (3개 카드)
- 테마별 묶음 입력 폼 (8개 테마 선택)
- 다른 포맷 입력 폼 (스토리 시리즈 옵션 포함)
- 뒤로가기 버튼 추가

### 2. `web/static/css/style.css`
- 포맷 선택 그리드 스타일
- 포맷 카드 호버 효과
- 뒤로가기 버튼 스타일

### 3. `web/static/js/main.js`
- 포맷 선택 이벤트 핸들러
- `initializeFormatSelection()` 함수
- `selectFormat()` - 포맷별 화면 전환
- `startThemeGeneration()` - 테마별 API 호출
- `startOtherFormatGeneration()` - 다른 포맷 API 호출
- **기존 코드 유지** (backward compatibility)

### 4. `src/sentence_generator.py` (신규 모듈)
```python
class SentenceGenerator:
    def generate_theme_sentences(theme, theme_detail) -> list[str]
        # 3~6문장 가변 생성 (내용에 따라)

    def generate_story_series(story_theme, day, previous_context) -> list[str]
        # Day 1-7 연결된 스토리 (3~6문장)

    def generate_movie_quotes() -> list[str]
        # 영화 명대사 3문장

    def generate_pronunciation_sentences() -> list[str]
        # 발음 집중 3문장

    def generate_news_sentences() -> list[str]
        # 뉴스 스타일 3문장
```

### 5. `web/app.py`
- `format` 파라미터 처리 (`manual`, `theme`, `other`)
- `SentenceGenerator` 통합
- 포맷별 문장 생성 분기 처리
- 검증 로직:
  - manual: 정확히 3문장
  - theme/other: 3~6문장 허용
- 생성된 문장 반환 (디버깅용)

### 6. `TASKS.md`
- Phase 7.1 업데이트 (포맷 선택 기능 완료 체크)
- 현재 진행 상황 업데이트

---

## 🔧 기술 스택

- **Backend**: Python 3.11+, Flask, Threading
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Services**:
  - OpenAI GPT-4o-mini (문장 생성, 번역, 메타데이터)
  - OpenAI DALL-E 3 (이미지 생성, 1024x1792)
  - OpenAI TTS-1 (음성 생성, nova voice)
- **Video**: MoviePy 2.x
- **Image**: PIL (Pillow) - 회전, 리사이즈
- **Audio**: mutagen (오디오 길이 측정)
- **Caching**: MD5 기반 리소스 캐싱

---

## 🚀 실행 방법

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. Flask 웹 서버 실행
cd web
python app.py

# 3. 브라우저에서 접속
# http://localhost:5001
```

---

## 📋 비디오 생성 파이프라인

```
1. 포맷 선택 (manual/theme/other)
   ↓
2. 문장 생성/입력
   - Manual: 사용자 직접 입력 (3문장)
   - Theme: GPT-4o-mini 자동 생성 (3~6문장)
   - Other: 포맷별 GPT-4o-mini 생성 (3~6문장)
   ↓
3. ContentAnalyzer - 문장 분석 및 이미지 프롬프트 생성
   ↓
4. ImageGenerator - DALL-E 3 이미지 생성 (캐싱)
   ↓
5. TTSGenerator - TTS 음성 생성 (각 문장별, 캐싱)
   ↓
6. VideoCreator - MoviePy 비디오 합성
   - 인트로 (2초, "Daily English Mecca" 타이틀)
   - 문장 클립 (이미지 + 영어 텍스트 + 한글 번역 + 음성)
   - 아웃트로 (3초, "좋아요 & 구독 & 알림 설정")
   - 배경 음악 (-20dB)
   ↓
7. YouTubeMetadataGenerator - 제목/설명/태그 생성
   ↓
8. 다운로드 가능 (video.mp4 + metadata.json)
```

---

## 🎨 UI 구조

```
메인 화면 (index.html)
├── 포맷 선택 섹션 (format-selection)
│   ├── 매일 3문장 카드 → manual-input
│   ├── 테마별 묶음 카드 → theme-input
│   └── 다른 포맷 카드 → other-input
│
├── Manual 입력 섹션 (manual-input)
│   └── 3개 문장 직접 입력
│
├── Theme 입력 섹션 (theme-input)
│   ├── 테마 선택 (8개 옵션)
│   └── 세부 주제 (선택사항)
│
├── Other 입력 섹션 (other-input)
│   ├── 포맷 선택 (4개 옵션)
│   └── 스토리 시리즈 옵션 (주제, Day)
│
├── 진행 상황 섹션 (progress-section)
│   ├── 프로그레스 바
│   ├── 현재 단계
│   └── 로그 출력
│
└── 결과 섹션 (result-section)
    ├── 비디오 미리보기
    ├── 다운로드 버튼
    └── 메타데이터 다운로드
```

---

## 🔑 주요 코드 위치

### Frontend
- **포맷 선택 UI**: `web/templates/index.html:60-100`
- **포맷 선택 로직**: `web/static/js/main.js:150-200`
- **테마 생성 API 호출**: `web/static/js/main.js:250-280`

### Backend
- **포맷별 분기**: `web/app.py:196-298`
- **테마별 문장 생성**: `src/sentence_generator.py:18-96`
- **스토리 시리즈 생성**: `src/sentence_generator.py:98-170`

### 검증 로직
- **Manual 검증**: `web/app.py:256-261` (정확히 3문장)
- **Theme/Other 검증**: `web/app.py:264-273` (3~6문장)

---

## 🐛 알려진 이슈 & 해결 방법

### 1. 이미지 회전 문제
**문제**: DALL-E 생성 이미지가 가로 방향일 때 간헐적으로 회전 안 됨
**해결**: PIL 기반 회전 로직 강화 (`src/image_generator.py:180-220`)
- EXIF Orientation 체크
- 가로 이미지 자동 90도 회전
- 1080x1920 세로 포맷 강제

### 2. 배경 음악 볼륨
**문제**: 배경 음악이 TTS 음성을 덮음
**해결**: 배경 음악 -20dB 감소 (`src/video_creator.py:450`)

### 3. 타이틀 가독성
**문제**: 인트로/아웃트로 타이틀이 배경에 묻힘
**해결**: Gold stroke (4px) + 반투명 배경 박스 추가 (`src/video_creator.py:250-280`)

---

## 📊 API 사용량

### OpenAI API 호출 (비디오 1개당)
- **GPT-4o-mini**: 3~5회
  - 문장 생성 (theme/other 포맷): 1회
  - 문장 분석: 1회
  - 번역: 1회 (문장 개수만큼)
  - 메타데이터 생성: 1회
- **DALL-E 3**: 1~3회 (캐싱으로 재사용)
- **TTS-1**: 3~6회 (문장 개수만큼, 캐싱으로 재사용)

### 캐싱 시스템
- **이미지 캐싱**: MD5 해시 기반 (`output/resources/images/`)
- **음성 캐싱**: MD5 해시 기반 (`output/resources/audio/`)
- 동일 프롬프트/텍스트 재사용 시 API 호출 없음

---

## 🔄 Git 저장소

- **Repository**: `git@github.com:jeromwolf/daily-eng-mecca.git`
- **Branch**: `main`
- **Last Commit**: "포맷 선택 기능 추가: 매일3문장/테마별묶음/다른포맷 (AI 자동 생성 3~6문장)"

---

## 📝 다음 단계

### 완료 대기
- [ ] 새 포맷 기능 실제 테스트
- [ ] 스토리 시리즈 Day 연결 로직 완성 (Day 2-7 컨텍스트 전달)
- [ ] README 업데이트 (포맷 선택 기능 설명)

### 향후 개선 (Backlog)
- [ ] 문장 품질 검증 (GPT로 생성된 문장 검토)
- [ ] 배치 처리 모드 (여러 비디오 동시 생성)
- [ ] 유튜브 자동 업로드 (YouTube Data API)
- [ ] 썸네일 자동 생성
- [ ] 다국어 지원 (일본어, 중국어 등)
- [ ] 성과 분석 대시보드

---

## 💡 개발 철학

1. **모듈화**: 각 기능은 독립적인 모듈로 개발
2. **사이드 이펙트 방지**: 새 기능 추가 시 기존 코드 영향 없도록
3. **캐싱 우선**: API 호출 최소화로 비용 절감
4. **가독성**: 명확한 변수명, 한글 주석
5. **에러 핸들링**: try-except로 안전한 실행

---

**문의사항이나 버그는 GitHub Issues에 남겨주세요!**
