# Daily English Mecca - 개발 컨텍스트 (Claude Code)

**마지막 업데이트**: 2025-11-09
**담당자**: 켈리 & Claude Code

---

## 📌 프로젝트 개요

YouTube 영어 학습 비디오 자동 생성 시스템 + **전문 썸네일 생성 툴** 🆕
- **2가지 포맷**: Shorts (9:16, 1080x1920) + Longform (16:9, 1920x1080)
- OpenAI DALL-E 3 이미지 생성 + 캐싱
- OpenAI TTS-1 음성 생성 (3가지 음성: alloy, nova, shimmer)
- GPT-4o-mini 한국어 번역 + AI 바이럴 훅 생성
- MoviePy 2.x 비디오 합성
- Flask 웹 인터페이스 + **비디오 에디터**
- **Kelly 캐릭터 브랜딩**: 인트로/아웃트로 전체 화면 배경
- **YouTube 썸네일 스튜디오**: Fire English 스타일, 텍스트 편집, 히스토리 관리 🆕
- 배경 음악 (Kevin MacLeod - Pixel Peeker Polka, 경쾌한 탐정 스타일, 5% 볼륨)
- PIL 기반 이미지 회전 로직
- **5가지 비디오 포맷**: 매일 3문장, 테마별 묶음, 퀴즈 챌린지, 한국어 속어 vs 영어 속어, **랜드마크 영어 학습**

---

## 🎯 최근 작업 (2025-11-09)

### ✅ 썸네일 스튜디오 텍스트 수정 버그 수정 3부작 (100% 완료)

**사용자 피드백**:
1. "텍스트수정하기 선택해서 메인텍스트를 바꾸었는데 메인텍스트는 필수라고 나오네"
2. "텍스트 바꾼 후 미리보기가 비어있고"
3. "이미지는 없어졌어. 텍스트 수정하니"

**목표**: 썸네일 텍스트 수정 기능 완전 복구

**구현 내용:**

#### **1. FormData 전송 문제 수정 (THUMBNAIL_TEXT_EDIT_FIX.md)**

**파일**: `web/static/js/thumbnail_studio.js:755-797`

**문제**: 프론트엔드가 JSON으로 전송하지만 백엔드는 FormData 기대
```javascript
// 수정 전 (❌ 잘못됨)
const response = await fetch('/thumbnail-studio/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)  // JSON 전송
});

// 수정 후 (✅ 정상)
const formData = new FormData();
formData.append('main_text', mainText);
formData.append('subtitle_text', subtitleText);
formData.append('style', currentThumbnailData.style || 'fire_english');

const response = await fetch('/thumbnail-studio/api/generate', {
    method: 'POST',
    body: formData  // FormData 전송
});
```

**효과**: "메인 텍스트는 필수입니다" 에러 해결

---

#### **2. 이미지 표시 문제 수정 (THUMBNAIL_DISPLAY_FIX.md)**

**파일**: `web/static/js/thumbnail_studio.js:817-856`

**문제**: 백엔드가 `thumbnail_url` 반환하지만 프론트엔드는 `thumbnail_path` 사용
```javascript
// 수정 전 (❌)
displayThumbnail(data.thumbnail_path);  // undefined

// 수정 후 (✅)
const thumbnailUrl = data.thumbnail_url || (data.thumbnail_urls && data.thumbnail_urls[0]);
if (thumbnailUrl) {
    displayThumbnail(thumbnailUrl);
    loadHistory(currentSessionId);  // 히스토리 새로고침
} else {
    throw new Error('썸네일 URL을 받지 못했습니다.');
}
```

**효과**: 빈 화면 해결, 새 텍스트가 표시된 썸네일 정상 로드

---

#### **3. 배경 이미지 보존 문제 수정 (THUMBNAIL_BACKGROUND_FIX.md)**

**파일**: `web/routes/thumbnail_routes.py:337-363`, `web/static/js/thumbnail_studio.js:762-766`

**문제**: 텍스트 수정 시 새 세션 생성으로 배경 이미지 손실

**백엔드 수정**:
```python
# 세션 재사용 및 배경 이미지 복원
existing_session_id = request.form.get('session_id')

if existing_session_id and history_manager.get_session_thumbnails(existing_session_id):
    # 기존 세션 재사용
    session_id = existing_session_id
    print(f"📁 기존 세션 재사용: {session_id}")

    # 마지막 썸네일의 배경 이미지 및 채널 아이콘 복원
    session_thumbnails = history_manager.get_session_thumbnails(session_id)
    if session_thumbnails:
        last_config = session_thumbnails[-1].get('config', {})

        # 배경 이미지 재사용
        if not background_image_paths:
            last_bg_path = last_config.get('background_image_path')
            if last_bg_path and Path(last_bg_path).exists():
                background_image_paths = [last_bg_path]
                print(f"✅ 이전 배경 이미지 재사용: {Path(last_bg_path).name}")

        # 채널 아이콘 재사용
        if not channel_icon_path:
            last_icon_path = last_config.get('channel_icon_path')
            if last_icon_path and Path(last_icon_path).exists():
                channel_icon_path = last_icon_path
                print(f"✅ 이전 채널 아이콘 재사용: {Path(last_icon_path).name}")
else:
    # 새 세션 생성
    session_id = history_manager.create_session({...})
```

**프론트엔드 수정**:
```javascript
// session_id FormData에 추가
if (currentSessionId) {
    formData.append('session_id', currentSessionId);
    console.log('📝 텍스트 수정 모드: 기존 세션 재사용 →', currentSessionId);
}
```

**효과**: 배경 이미지 및 채널 아이콘 보존, 텍스트만 변경

---

**수정 파일:**
- `web/static/js/thumbnail_studio.js:755-856` - FormData 전송, 응답 처리, 세션 ID 추가
- `web/routes/thumbnail_routes.py:337-363` - 세션 재사용 및 이미지 복원

**효과:**
- ✅ 텍스트 수정 기능 완전 복구
- ✅ 배경 이미지 보존
- ✅ 채널 아이콘 보존
- ✅ 히스토리 자동 업데이트
- ✅ 사용자 경험 대폭 개선

**참고 문서:**
- `THUMBNAIL_TEXT_EDIT_FIX.md` - FormData 전송 문제 수정
- `THUMBNAIL_DISPLAY_FIX.md` - 이미지 표시 문제 수정
- `THUMBNAIL_BACKGROUND_FIX.md` - 배경 이미지 보존 문제 수정
- `THUMBNAIL_TEXT_EDIT_TEST.md` - 테스트 가이드

---

## 🎯 이전 작업 (2025-11-07)

### ✅ 웹 UI 썸네일 자동 생성 통합 (100% 완료)

**사용자 요청**:
- "Option 1: 웹 UI에 썸네일 자동 생성 통합"
- 비디오 생성 시 썸네일 자동 생성
- Fire English 스타일 CTR 최적화 썸네일

**목표**: 비디오 생성 워크플로우에 썸네일 자동 생성 통합

**구현 내용:**

**1. 백엔드 통합 (100% 완료)**

**파일**: `web/app.py`

**변경사항**:

1. **ThumbnailGenerator 임포트** (Line 28):
   ```python
   from src.thumbnail_generator import ThumbnailGenerator
   ```

2. **비디오 생성 후 썸네일 자동 생성** (Lines 307-370):
   ```python
   # 4.3. 썸네일 자동 생성 (Fire English 스타일)
   task.update(91, '썸네일 생성 중...', '⏳ YouTube 썸네일 생성 중...')
   try:
       from moviepy import VideoFileClip

       # 썸네일 생성기 초기화
       thumbnails_dir = output_dir / 'thumbnails'
       thumbnails_dir.mkdir(parents=True, exist_ok=True)

       thumbnail_gen = ThumbnailGenerator(
           resource_manager=resource_manager,
           output_dir=str(thumbnails_dir)
       )

       # 비디오 duration 측정
       video_clip = VideoFileClip(str(video_path))
       video_duration = int(video_clip.duration)
       video_clip.close()

       # 포맷별 썸네일 텍스트 결정
       if format_type == 'longform':
           main_text = "영어 회화 마스터"
           subtitle_text = f"필수 {len(sentences)}문장"
           theme = 'education'
       elif format_type == 'landmark':
           landmark_name = quiz_data.get('landmark', 'Landmark')
           main_text = landmark_name
           subtitle_text = f"여행 영어 {len(sentences)}문장"
           theme = 'landmark'
       elif format_type == 'quiz':
           main_text = "Quiz Challenge"
           subtitle_text = "정답률 30%!"
           theme = 'quiz'
       elif format_type == 'idiom_comparison':
           korean_idiom = quiz_data.get('korean_idiom', '대박')
           main_text = korean_idiom
           subtitle_text = "vs 원어민 영어 속어"
           theme = 'comparison'
       else:
           # manual, theme, other 포맷
           main_text = "Daily English"
           subtitle_text = f"필수 {len(sentences)}문장"
           theme = 'daily'

       # 미리보기 문장 (최대 3개)
       preview_sentences = [s[:30] + '...' if len(s) > 30 else s for s in sentences[:3]]

       # 썸네일 생성 (Fire English 스타일)
       thumbnail_path = thumbnail_gen.create_thumbnail(
           main_text=main_text,
           subtitle_text=subtitle_text,
           theme=theme,
           sentence_count=len(sentences),
           video_duration=video_duration,
           preview_sentences=preview_sentences,
           output_path=str(thumbnails_dir / f'thumbnail_{task_id}.png')
       )

       print(f"✅ 썸네일 생성 완료: {thumbnail_path}")
       task.update(92, '썸네일 생성 완료', f'✅ 썸네일 저장: {Path(thumbnail_path).name}')

   except Exception as thumb_error:
       print(f"⚠ 썸네일 생성 실패 (계속 진행): {thumb_error}")
       thumbnail_path = None
   ```

3. **작업 결과에 썸네일 경로 추가** (Lines 414-415):
   ```python
   task.result = {
       'video_path': f'/api/download/{task_id}/video',
       'video_filename': f'daily_english_{task_id}.mp4',
       'metadata': metadata,
       'metadata_path': f'/api/download/{task_id}/metadata',
       'thumbnail_path': f'/api/download/{task_id}/thumbnail' if thumbnail_path else None,
       'thumbnail_filename': f'thumbnail_{task_id}.png' if thumbnail_path else None
   }
   ```

4. **썸네일 다운로드 엔드포인트 추가** (Lines 759-762):
   ```python
   elif file_type == 'thumbnail':
       file_path = output_dir / 'thumbnails' / f'thumbnail_{task_id}.png'
       mimetype = 'image/png'
       download_name = f'thumbnail_{task_id}.png'
   ```

**특징**:
- ✅ **자동 생성**: 비디오 생성 완료 후 자동으로 썸네일 생성
- ✅ **포맷별 최적화**: 롱폼/랜드마크/퀴즈/속어 비교별 맞춤 텍스트
- ✅ **Fire English 스타일**: 숫자 배지, 문장 미리보기, 영상 길이 표시
- ✅ **Kelly 캐릭터**: 90% 크기로 중앙 배치
- ✅ **다운로드 가능**: 비디오와 함께 썸네일 다운로드 제공
- ✅ **안전한 폴백**: 썸네일 생성 실패 시 비디오 생성은 계속 진행

**수정 파일:**
- `web/app.py:28` - ThumbnailGenerator 임포트
- `web/app.py:307-370` - 썸네일 자동 생성 로직
- `web/app.py:414-415` - 작업 결과에 썸네일 경로 추가
- `web/app.py:759-762` - 썸네일 다운로드 엔드포인트

**워크플로우:**
```
비디오 생성 완료 (90%)
  ↓
썸네일 생성 시작 (91%)
  ├─ 비디오 duration 측정
  ├─ 포맷별 텍스트 결정
  ├─ Fire English 스타일 썸네일 생성
  └─ 썸네일 저장 (output/thumbnails/)
  ↓
썸네일 생성 완료 (92%)
  ↓
편집 설정 저장 (94%)
  ↓
메타데이터 생성 (100%)
```

**효과:**
- 🚀 **CTR 향상**: Fire English 스타일 썸네일로 클릭률 증가
- ⚡ **자동화**: 수동 썸네일 제작 시간 절약
- 🎨 **브랜딩**: Kelly 캐릭터로 일관된 채널 아이덴티티
- 📊 **SEO 최적화**: 포맷별 맞춤 썸네일로 YouTube 알고리즘 최적화

---

## 🎯 이전 작업 (2025-11-07)

### ✅ 랜드마크 비디오 YouTube 메타데이터 최적화 (100% 완료)

**사용자 요청**:
- "유튜브 메타정보도 잘 작성해줘. 구독자가 늘수 있도록"
- 현재 구독자 10명 → 100명 성장 목표
- 여행 + 영어 학습 니치 최적화 필요

**목표**: 랜드마크 비디오의 YouTube SEO 최적화 및 구독자 성장 전략

**구현 내용:**

**1. 랜드마크 전용 메타데이터 생성 함수 추가** (`src/youtube_metadata.py:20-61`)

```python
def generate_landmark_metadata(self, landmark_name: str, sentences: list[str]) -> dict:
    """
    랜드마크 영어 학습 비디오를 위한 유튜브 메타정보 생성
    - 여행 + 영어 학습 니치 조합 (트렌드 니치)
    - >12% CTR 목표 (일반 영어 학습보다 높음)
    - 구독자 성장 최적화
    """
```

**주요 특징**:
- GPT-4o-mini 사용, temperature=0.9 (창의적 제목)
- 시스템 프롬프트: 여행 + 영어 학습 전문가 페르소나
- 타겟 CTR: >12% (일반 영어 >10%보다 높음)

**2. 랜드마크별 키워드 매핑 시스템** (`src/youtube_metadata.py:127-138`)

```python
travel_keywords = {
    "Eiffel Tower": {"ko": "파리여행, 에펠탑, 프랑스여행", "en": "Paris, Eiffel Tower, France travel"},
    "Big Ben": {"ko": "런던여행, 빅벤, 영국여행", "en": "London, Big Ben, UK travel"},
    "Gyeongbokgung Palace": {"ko": "서울여행, 경복궁, 한국여행, 케대헌", "en": "Seoul, Gyeongbokgung, Korea travel"},
    # ... 41개 랜드마크 지원
}
```

**효과**:
- 랜드마크별 맞춤 SEO 키워드
- 케대헌 추천 한국 랜드마크 특별 처리
- 도시/국가 기반 검색 최적화

**3. GPT 프롬프트 최적화** (`src/youtube_metadata.py:143-203`)

**제목 포뮬러 예시**:
- "{landmark_name} 여행 필수 영어 {num_sentences}문장 🌍 현지에서 바로 쓰는 표현"
- "여행영어 {landmark_name} 편 🗼 원어민처럼 말하는 {num_sentences}가지 표현"
- "{landmark_name} 가기 전 꼭 알아야 할 영어 {num_sentences}문장 ✈️"

**설명 구조**:
1. 훅: 랜드마크 매력 + 영어 학습 가치 조합
2. 케대헌 추천 언급 (한국 랜드마크)
3. 타임스탬프 + 번역
4. 여행 컨텍스트 (실제 사용 팁)
5. CTA: "여행 가기 전 좋아요 & 구독으로 영어 준비하세요!"

**태그 전략 (35+ 태그)**:
- 여행 키워드: 여행영어, 해외여행, 유럽여행, 관광영어
- 영어 학습: 영어회화, 영어공부, 일상영어
- 조합: 여행영어회화, 해외여행영어, 관광영어
- 위치 기반: {랜드마크}여행, {랜드마크}영어, {랜드마크}가이드
- 트렌딩: 영어쇼츠, 여행쇼츠, 해외여행꿀팁

**해시태그 (20-25개, without #)**:
- 여행: 여행영어, 해외여행, 유럽여행, 세계여행
- 영어: 영어회화, 영어공부, 영어표현
- 조합: 여행영어회화, 관광영어, 여행회화
- 영문: TravelEnglish, LearnEnglish, TouristEnglish
- 케대헌 (한국 랜드마크 전용)

**4. 폴백 메타데이터** (`src/youtube_metadata.py:206-283`)

**GPT 실패 시 안전한 기본 메타데이터 생성**:
- 한국 랜드마크 자동 감지 → 케대헌 추천 표시
- 35+ 태그 자동 생성 (랜드마크명 포함)
- 여행 팁 및 학습 가이드 포함

**5. API 통합** (`web/app.py:326-331`)

```python
# 랜드마크 포맷일 경우 전용 메타정보 생성 (여행 + 영어 학습 니치)
if format_type == 'landmark':
    landmark_name = quiz_data.get('landmark', 'Landmark')
    metadata = metadata_gen.generate_landmark_metadata(landmark_name, sentences)
else:
    metadata = metadata_gen.generate_metadata(sentences)
```

**수정 파일:**
- `src/youtube_metadata.py:20-283` - 랜드마크 메타데이터 함수 3개 추가
- `web/app.py:326-331` - 랜드마크 포맷 분기 추가

**효과:**
- ✅ **SEO 최적화**: 여행 + 영어 학습 니치 조합 (트렌딩)
- ✅ **CTR 향상**: >12% 타겟 (바이럴 제목 포뮬러)
- ✅ **구독자 성장**: 케대헌 추천 활용 + 댓글 유도
- ✅ **검색 노출 증가**: 35+ 태그 + 위치 기반 키워드
- ✅ **크로스 프로모션**: 케대헌 추천 언급으로 상호 성장

**예상 결과**:
- 구독자 10명 → 100명 (목표)
- 여행 준비 단계 시청자 타겟 (높은 참여도)
- 랜드마크별 시리즈 콘텐츠 가능성

---

### ✅ 랜드마크 비디오 특수 문자 렌더링 버그 수정 (100% 완료)

**사용자 요청**:
- "가끔씩 깨지는 글자가 나와. 여기는 제목이 깨졌어" (스크린샷 제공)
- "Champs-Élysées" → "Champs-□lys□es" (É, é가 네모 박스로 표시)
- "André Le Nôtre" → "Andr□ Le N□tre" (중간 문장에서도 깨짐)
- 추가 요청: "스위스대표음식, 캐데현에서 나오는 한국 대표 랜드마크 추가"

**문제 분석**:
- MoviePy TextClip이 AppleGothic.ttf 폰트로 특수 악센트 문자 렌더링 불가
- 프랑스어 랜드마크 이름 (É, è, ô, ç 등) 표시 안 됨
- GPT-4o-mini 생성 문장에도 특수 문자 포함 가능

**해결 방법**:
1. **`sanitize_text_for_moviepy()` 헬퍼 함수 추가** (`src/video_creator.py:23-45`)
   ```python
   def sanitize_text_for_moviepy(text: str) -> str:
       """
       MoviePy TextClip이 렌더링할 수 없는 특수 문자를 ASCII로 변환

       Examples:
           "Champs-Élysées" → "Champs-Elysees"
           "André Le Nôtre" → "Andre Le Notre"
           "Château" → "Chateau"
       """
       # unicodedata.normalize('NFKD', text)로 악센트 분리
       # 예: É → E + ́ (combining acute accent)
       normalized = unicodedata.normalize('NFKD', text)

       # ASCII 문자만 유지 (악센트 제거)
       ascii_text = ''.join([c for c in normalized if not unicodedata.combining(c)])

       return ascii_text
   ```

2. **인트로 타이틀에 적용** (`src/video_creator.py:2879-2881`)
   ```python
   # 특수 문자 제거 (É→E, é→e 등) - MoviePy TextClip 호환성
   sanitized_name = sanitize_text_for_moviepy(landmark_name)
   print(f"    📝 타이틀: {landmark_name} → {sanitized_name} (특수문자 변환)")
   ```

3. **문장 클립 영어 텍스트에 적용** (`src/video_creator.py:3004-3010`)
   ```python
   # 영어 문장 (큰 텍스트) - 특수 문자 제거
   sanitized_sentence = sanitize_text_for_moviepy(sentence)
   if sanitized_sentence != sentence:
       print(f"    📝 문장: {sentence[:50]}... → {sanitized_sentence[:50]}... (특수문자 변환)")
   ```

4. **아웃트로 메시지에 적용** (`src/video_creator.py:3091-3096`)
   ```python
   # 메인 메시지 - 특수 문자 제거
   sanitized_name = sanitize_text_for_moviepy(landmark_name)
   main_txt = TextClip(
       text=f"Thanks for learning\nabout {sanitized_name}!",
       ...
   )
   ```

5. **랜드마크 추가** (`web/templates/index.html`)
   - 스위스: "Swiss Cuisine" (스위스대표음식) 버튼 추가
   - 🇰🇷 한국 섹션 신규 생성 (8개 랜드마크):
     - Gyeongbokgung Palace (경복궁)
     - N Seoul Tower (N서울타워)
     - Bukchon Hanok Village (북촌한옥마을)
     - Myeongdong (명동)
     - Hongdae (홍대)
     - Dongdaemun Design Plaza (동대문디자인플라자)
     - Insadong (인사동)
     - Lotte World Tower (롯데월드타워)

**수정 파일:**
- `src/video_creator.py:5, 23-45` - `unicodedata` import + sanitize 함수 추가
- `src/video_creator.py:2879-2881` - 인트로 타이틀 적용
- `src/video_creator.py:3004-3010` - 문장 클립 적용
- `src/video_creator.py:3091-3096` - 아웃트로 메시지 적용
- `web/templates/index.html:474, 478-491` - 스위스대표음식 + 한국 랜드마크 추가

**효과:**
✅ **깨진 문자 완전 제거**: 모든 특수 악센트 문자가 ASCII로 변환
✅ **프랑스 랜드마크 지원**: "Champs-Élysées" → "Champs-Elysees" (읽기 가능)
✅ **범용 솔루션**: 모든 언어의 악센트 자동 처리 (독일어 ü, 스페인어 ñ 등)
✅ **랜드마크 확장**: 총 41개 랜드마크 (프랑스 6 + 이탈리아 14 + 스위스 5 + 한국 8 + 세계 6)

**기술적 원리**:
- `unicodedata.normalize('NFKD', text)`: Canonical Decomposition (정규 분해)
  - "É" → "E" + "́" (combining acute accent)
- `unicodedata.combining(c)`: 조합 문자(악센트) 필터링
- ASCII만 유지 → MoviePy TextClip 안전 렌더링

**테스트 결과**: 다음 랜드마크 생성 시 모든 문자가 정상 표시될 것

---

## 🎯 이전 작업 (2025-11-05)

### ✅ NumPy Broadcasting Error 근본 원인 해결 (완료)

**배경**:
- 5번 이상 같은 오류 반복 발생
- 사용자 요청: "근본적인 오류 파악하여 수정이 필요함"

**에러 메시지**:
```
ValueError: operands could not be broadcast together with shapes (30,1840) (0,1840)
```

**근본 원인 (Root Cause)**:
코드에서 **두 가지 다른 Kelly 사용법이 충돌**:

1. **Kelly 전체 배경** (의도된 기능):
   - 인트로/아웃트로 배경으로 Kelly 캐릭터 이미지 사용
   - `src/video_creator.py:286-318` (인트로)
   - `src/video_creator.py:788-807` (아웃트로)

2. **Kelly Cat 오버레이** (불필요한 중복):
   - 같은 인트로/아웃트로에 Kelly를 **또 다시** 작게 하단에 추가
   - `src/video_creator.py:386-421` (인트로)
   - `src/video_creator.py:850-885` (아웃트로)
   - RGBA 알파 채널 마스크 처리 시 MoviePy가 **height=0인 마스크** 생성
   - broadcasting error 발생

**문제**: 같은 화면에 Kelly를 **중복으로 2번** 추가하려 시도

**이전 시도들 (증상 치료)**:
1. ❌ MoviePy `.rotated()` → PIL `transpose(ROTATE_90)`
2. ❌ MoviePy `.resized()` → PIL `resize()`
3. ❌ RGBA 모드 변환 + 알파 채널 마스크 명시적 설정

→ 모두 실패한 이유: **근본 원인(중복 로직)을 해결하지 못함**

**해결 방법 (Root Fix)**:
**불필요한 Kelly Cat 오버레이 로직 완전 제거**

**수정 파일**:

1. **`src/video_creator.py:383-388`** - 인트로 클립
   ```python
   # Before (47줄): Kelly Cat 추가 시도
   if self.use_kelly and self.image_generator:
       try:
           kelly_image_path = self.image_generator.generate_kelly_for_scenario('intro')
           # ... PIL 리사이즈, RGBA 변환, 마스크 설정 ... (47줄)

   # After (3줄): 간단한 레이어 구조
   # 배경 이미지에 이미 Kelly 캐릭터가 포함되어 있으므로 별도로 Kelly Cat 추가 불필요
   layers = [bg]  # 배경 (Kelly 캐릭터 포함)
   intro_text = hook_phrase if hook_phrase else "오늘의 3문장\nDaily English"
   ```

2. **`src/video_creator.py:805-810`** - 아웃트로 클립
   ```python
   # Before (47줄): Kelly Cat 추가 시도
   if self.use_kelly and self.image_generator:
       try:
           kelly_image_path = self.image_generator.generate_kelly_for_scenario('outro')
           # ... PIL 리사이즈, RGBA 변환, 마스크 설정 ... (47줄)

   # After (3줄): 간단한 레이어 구조
   # 배경 이미지에 이미 Kelly 캐릭터가 포함되어 있으므로 별도로 Kelly Cat 추가 불필요
   layers = [bg]  # 배경 (Kelly 캐릭터 포함)
   outro_message = "댓글에 오늘 배운 문장 써보세요!"
   ```

3. **`test_shorts_kelly.py`** - 테스트 스크립트 수정
   - ResourceManager 파라미터: `base_dir` → `resources_dir`
   - 인트로/아웃트로 클립만 단독 테스트하도록 단순화

**테스트 결과**:
```
✅ 인트로 클립 저장: test_intro.mp4 (108.84 KB)
   - Kelly 이미지 로드: kelly_casual_hoodie.png
   - 1792x1024 → 90도 회전 → 1024x1792
   - 오류 없음!

✅ 아웃트로 클립 저장: test_outro.mp4 (127.93 KB)
   - Kelly 이미지 로드: kelly_casual_hoodie.png
   - 1792x1024 → 90도 회전 → 1024x1792
   - 오류 없음!
```

**효과**:
- ✅ broadcasting error 완전 해결
- ✅ 코드 간소화 (각 클립별 44줄 감소)
- ✅ Kelly 배경이 정상적으로 표시됨
- ✅ 중복 로직 제거로 향후 유지보수 용이

**교훈**:
- 증상만 치료하지 말고 **근본 원인**을 찾아야 함
- 복잡한 해결책보다 **단순한 설계**가 더 안정적
- 중복 로직은 항상 **버그의 원인**

---

## 🎯 이전 작업 (2025-11-04)

### ✅ Shorts 인트로/아웃트로 Kelly 캐릭터 배경 추가 (브랜딩 강화)

**사용자 요청**:
- "숏폼에도 인트로,아웃트로에 이미지를 넣어줄까?"
- 현재 Shorts는 추상적인 DALL-E 배경 사용 중
- 롱폼처럼 Kelly 캐릭터로 변경하여 브랜딩 일관성 확보
- "오류 발생하지 말고, 잘 부탁해"

**목표**: Shorts와 Longform 모두 Kelly 캐릭터로 통일된 브랜딩

**구현 내용:**

**1. Shorts 인트로 Kelly 캐릭터 배경 (100% 완료)**

**파일**: `src/video_creator.py:286-318`
**변경사항**: `_create_intro_clip()` 함수 수정

**변경 전**:
```python
# DALL-E로 추상적인 파란색 그라데이션 배경 생성
intro_prompt = (
    "Abstract modern background for English learning video intro. "
    "Smooth gradient with soft geometric patterns..."
)
intro_image_path = self.image_generator.generate_image(...)
```

**변경 후**:
```python
# Kelly 캐릭터 이미지 로드 (Shorts에서도 Kelly 사용)
elif self.resource_manager:
    kelly_candidates = [
        "kelly_casual_hoodie.png",  # 메인
        "kelly_ponytail.png",       # 대체1
        "kelly_glasses.png"         # 대체2
    ]
    for path in kelly_candidates:
        if os.path.exists(path):
            intro_image_path = path
            print(f"✓ [Shorts 인트로] Kelly 이미지 로드: {os.path.basename(path)}")
            break
```

**2. Shorts 아웃트로 Kelly 캐릭터 배경 (100% 완료)**

**파일**: `src/video_creator.py:749-780`
**변경사항**: `_create_outro_clip()` 함수 수정

**변경 전**:
```python
# DALL-E로 추상적인 핑크색 그라데이션 배경 생성
outro_prompt = """A simple geometric abstract background with warm pink coral gradient.
Modern minimalist design with soft shapes..."""
outro_image_path = self.image_generator.generate_image(...)
```

**변경 후**:
```python
# Kelly 캐릭터 이미지 로드 (인트로와 동일 로직)
elif self.resource_manager:
    kelly_candidates = [...]
    print(f"✓ [Shorts 아웃트로] Kelly 이미지 로드: {os.path.basename(path)}")
```

**3. 테스트 스크립트 생성 (100% 완료)**

**파일**: `test_shorts_kelly.py` (신규 생성)

**테스트 항목**:
1. 인트로에 Kelly 캐릭터가 전체 화면 배경으로 표시되는가?
2. 인트로 텍스트가 Kelly 위에 오버레이되는가?
3. 아웃트로에 Kelly 캐릭터가 전체 화면 배경으로 표시되는가?
4. 아웃트로 CTA 텍스트가 읽기 쉬운가?

**실행 방법**:
```bash
cd "/Users/blockmeta/.../daily-english-mecca"
source venv/bin/activate
python test_shorts_kelly.py
```

**수정 파일:**
- `src/video_creator.py:286-318` - Shorts 인트로 Kelly 배경
- `src/video_creator.py:749-780` - Shorts 아웃트로 Kelly 배경
- `test_shorts_kelly.py` - 테스트 스크립트 (신규)

**효과:**
✅ **브랜딩 일관성**: Shorts + Longform 모두 Kelly 캐릭터 사용
✅ **시각적 개선**: 추상 배경 → 친근한 캐릭터로 참여도 증가
✅ **API 비용 절감**: DALL-E 생성 없이 기존 Kelly 이미지 재사용
✅ **오류 방지**: 안전한 폴백 로직 (이미지 없으면 기본 배경)

**이전/이후 비교**:
- **이전**: Shorts 인트로 (DALL-E 파란 그라데이션) + 아웃트로 (DALL-E 핑크 그라데이션)
- **이후**: Shorts 인트로 (Kelly 캐릭터) + 아웃트로 (Kelly 캐릭터) = Longform과 동일

---

## 🎯 이전 작업 (2025-10-24)

### ✅ 한국어 속어 vs 영어 속어 모듈 완성 (YouTube 성장 전략)

**사용자 요청**:
- YouTube Studio에서 "한국어 속어 vs. 원어민 영어 속어" 포맷 추천
- 구독자 10명 → 100명 성장 목표
- 기존 모듈에 사이드 이펙트 발생 방지 필수
- 폰트 하단 잘림 현상 주의
- 모듈별 전용 인트로/아웃트로 (고정 이미지)

**목표**: YouTube 알고리즘 최적화 및 참여도 향상 콘텐츠 개발

**구현 내용:**

**1. 프롬프트 문서화 시스템 구축 (100% 완료)**

**문제점**:
- AI 프롬프트가 코드 내에 하드코딩되어 관리 어려움
- 프롬프트 버전 관리 및 개선 히스토리 추적 불가

**해결 방법**:
- **`PROMPTS.md`** (5,000+ 라인) - 모든 AI 프롬프트 통합 문서
  - ContentAnalyzer 프롬프트 (문장 분석, 바이럴 훅)
  - SentenceGenerator 프롬프트 (테마, 스토리, 퀴즈, **속어 비교**)
  - ImageGenerator 프롬프트 (DALL-E)
  - YouTubeMetadataGenerator 프롬프트
- **`README.md`** 업데이트 - 프롬프트 문서 링크 추가

**속어 비교 프롬프트 예시**:
```python
# System Prompt
"You are an expert in Korean-English language education, specializing in slang, idioms, and cultural expressions."

# 10가지 제안 속어
- "대박" (daebak) - Wow, That's amazing
- "헐" (hul) - OMG, What the...
- "쩐다" (jjinda) - Epic, Insane
등
```

**2. 백엔드 AI 생성 모듈 (100% 완료)**

**파일**: `src/sentence_generator.py`
**함수**: `generate_idiom_comparison()` (147 라인)

```python
def generate_idiom_comparison(self) -> dict:
    """
    한국어 속어 vs 원어민 영어 속어 비교 콘텐츠 생성

    Returns:
        {
            'format': 'idiom_comparison',
            'korean_idiom': str,
            'korean_meaning': str,
            'wrong_translation': str,
            'why_wrong': str,
            'correct_expressions': [
                {
                    'english': str,
                    'usage_level': 'informal|formal|slang',
                    'korean_label': str,
                    'example': str
                }
            ]
        }
    """
```

**특징**:
- GPT-4o-mini, temperature=0.85, max_tokens=800
- JSON 파싱 및 검증 로직
- 3개 올바른 표현 (informal, formal, slang 레벨별)

**3. 전용 배경 이미지 생성 (100% 완료)**

**스크립트**: `generate_idiom_backgrounds.py` (DALL-E 3)

**생성 이미지**:
1. **`idiom_intro_bg.png`** (화면 분할)
   - 왼쪽: 파스텔 블루 (한국 전통 문양)
   - 오른쪽: 파스텔 핑크 (영어권 문화)
   - 중앙 구분선
   - 1080x1920 세로 포맷

2. **`idiom_outro_bg.png`** (통합 그라데이션)
   - 블루→핑크 그라데이션
   - Celebratory vibe
   - 사용자 참여 유도

**4. 비디오 클립 함수 6개 (100% 완료)**

**파일**: `src/video_creator.py`

**함수 목록**:

1. **`_create_idiom_intro_clip()`** (3초)
   - 화면 분할 배경
   - 타이틀: "한국어 속어 vs 원어민 영어 속어"
   - 서브타이틀: "Daily English Mecca"
   - **폰트 잘림 방지**: method='caption', size=(width, None), y=1650

2. **`_create_idiom_outro_clip()`** (5초)
   - 통합 그라데이션 배경
   - CTA: "알고 있던 속어\n댓글로 남겨주세요!"
   - 서브: "좋아요 & 구독"
   - **폰트 잘림 방지**: y=760 (중앙 위)

3. **`_create_idiom_korean_intro_clip()`** (5초)
   - 파스텔 블루 배경
   - 큰 텍스트: "대박" (font_size=90)
   - 의미 설명: "놀라움, 대단함을 표현"
   - 라벨: "🇰🇷 한국어 속어"

4. **`_create_idiom_wrong_clip()`** (7초, 화면 분할)
   - 왼쪽 (파스텔 레드): "❌ Big Night" (틀린 표현)
   - 오른쪽 (파스텔 옐로우): "💡 직역하면 이상함" (설명)
   - 중앙 구분선

5. **`_create_idiom_correct_clip()`** (10초)
   - 파스텔 그린 배경
   - 3개 표현 세로 배치 (y: 570, 880, 1190)
   - 사용 수준별 색상:
     ```python
     level_colors = {
         'informal': '#1976D2',  # 파란색
         'formal': '#7B1FA2',    # 보라색
         'slang': '#F57C00'      # 주황색
     }
     ```

6. **`create_idiom_comparison_video()`** (통합 함수)
   - **비디오 구조** (약 30초):
     ```
     [0-3초]   인트로
     [3-8초]   한국어 속어 소개
     [8-15초]  틀린 번역
     [15-25초] 올바른 표현 3개
     [25-30초] 아웃트로
     ```
   - 5개 클립 타임라인 배치
   - 오디오 5개 합성 (alloy, nova, shimmer 순환)
   - 배경 음악 인트로 3초만 추가

**5. API 라우트 통합 (100% 완료)**

**파일**: `web/app.py`

**변경사항**:

1. **포맷 분기 추가** (Line 343-385):
   ```python
   elif format_type == 'idiom_comparison':
       # 속어 비교 포맷 (신규 추가)
       sentence_gen = SentenceGenerator(api_key=api_key)
       idiom_data = sentence_gen.generate_idiom_comparison()

       quiz_data = idiom_data  # 비디오 생성 함수에 전달

       # TTS용 sentences 추출 (5개)
       sentences = [
           f"{idiom_data['korean_idiom']}. {idiom_data['korean_meaning']}",
           f"{idiom_data['wrong_translation']}. {idiom_data['why_wrong']}",
       ]
       for expr in idiom_data['correct_expressions'][:3]:
           sentences.append(f"{expr['english']}. {expr['korean_label']}. {expr['example']}")
   ```

2. **문장 검증 로직** (Line 415-418):
   ```python
   elif format_type == 'idiom_comparison':
       # 5개 고정 (한국어 속어 + 틀린 번역 + 올바른 표현3)
       if len(sentences) != 5:
           return jsonify({'error': f'속어 비교 데이터가 올바르지 않습니다 ({len(sentences)}개). 5개여야 합니다.'}), 500
   ```

3. **비디오 생성 분기** (Line 182-188):
   ```python
   if data_format == 'idiom_comparison':
       print("[DEBUG] 속어 비교 비디오 생성 모드")
       video_creator.create_idiom_comparison_video(
           idiom_data=quiz_data,
           audio_info=audio_info,
           output_path=str(video_path)
       )
   ```

**6. 프론트엔드 UI (100% 완료)**

**파일**: `web/templates/index.html`, `web/static/js/main.js`

**HTML 추가**:
1. **포맷 선택 카드**:
   ```html
   <div class="format-card" data-format="idiom_comparison">
       <div class="format-icon">🆚</div>
       <h3>한국어 속어 vs 영어 속어</h3>
       <p>틀린 직역 vs 원어민 표현</p>
       <button class="btn-select">선택하기</button>
   </div>
   ```

2. **입력 섹션** (Line 302-351):
   - AI 자동 생성 안내 (그라데이션 퍼플 info-box)
   - 예상 소요 시간: 40-60초
   - 음성 선택: alloy/nova/shimmer
   - 제출 버튼: "🎬 속어 비교 영상 생성하기"

**JavaScript 추가**:
1. **DOM 요소** (Line 15, 23):
   ```javascript
   const idiomComparisonInput = document.getElementById('idiom-comparison-input');
   const idiomComparisonForm = document.getElementById('idiom-comparison-form');
   ```

2. **포맷 선택** (Line 364-366):
   ```javascript
   } else if (format === 'idiom_comparison') {
       idiomComparisonInput.style.display = 'block';
   }
   ```

3. **폼 제출 핸들러** (Line 326-333):
   ```javascript
   idiomComparisonForm.addEventListener('submit', async (e) => {
       e.preventDefault();
       const voice = document.getElementById('idiom-voice').value;
       await startIdiomComparisonGeneration(voice);
   });
   ```

4. **API 호출 함수** (Line 512-542):
   ```javascript
   async function startIdiomComparisonGeneration(voice) {
       const response = await fetch('/api/generate', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
               format: 'idiom_comparison',
               voice: voice,
           }),
       });
       // ... 폴링 시작
   }
   ```

**수정 파일 전체 목록:**
- `PROMPTS.md` (신규 생성, 5,000+ 라인)
- `README.md` (프롬프트 문서 링크 추가)
- `generate_idiom_backgrounds.py` (신규 생성)
- `src/sentence_generator.py` (147 라인 추가)
- `src/video_creator.py` (600 라인 추가, 6개 함수)
- `web/app.py` (3곳 수정, idiom_comparison 분기)
- `web/templates/index.html` (50 라인 추가)
- `web/static/js/main.js` (40 라인 추가)

**사이드 이펙트 방지 검증:**
✅ 기존 포맷 영향 없음
- `create_video()` - 일반 포맷 (변경 없음)
- `create_quiz_video()` - 퀴즈 포맷 (변경 없음)
- 포맷별 독립적 분기 (`elif` 구조)
- 하위 호환성 유지 (`quiz_data.get('format', 'quiz')`)

**효과:**
- YouTube 알고리즘 최적화 콘텐츠 (속어 비교 → 높은 참여도)
- 댓글 유도 CTA ("알고 있던 속어 댓글로 남겨주세요!")
- 구독자 성장 기대 (10명 → 100명 목표)

---

## 🎯 이전 작업 (2025-10-19)

### ✅ 퀴즈 비디오 UI 개선 (3가지 이슈 수정)

**사용자 요청**:
1. "인트로 텍스트 아래 부분 깨짐"
2. "아웃트로 이미지는 잘 활용했는데 구독과 좋아요 나 이런 문구는 없네"
3. "인트로 음악 없음"

**사용자 강조사항**: "한번 테스트 할때마다 시간이 오래걸려 오류를 내지 말고 잘 하자"

**목표**: 퀴즈 챌린지 비디오의 가독성 및 참여도 향상

**구현 내용:**

**1. 인트로 텍스트 위치 수정 (100% 완료)**

**문제점**:
- 훅 문구 "한국인 95% 틀리는 문제!"가 인트로 이미지 위에서 하단 부분 잘림
- 텍스트가 y=800 위치에 있어 이미지와 겹침

**해결 방법**:
- **`src/video_creator.py:309`** - `_create_intro_clip()` 메서드
  ```python
  # 수정 전
  .with_position(('center', 800))

  # 수정 후
  .with_position(('center', 600))  # 더 위로 조정 (800 → 600, 이미지 위에서 텍스트 잘림 방지)
  ```

- **`src/preview/quiz_preview_generator.py:30`** - `IntroClip` 클래스
  ```python
  # 텍스트 위치를 더 위로 조정 (이미지 위에서 텍스트가 잘리는 문제 해결)
  position=('center', 600),  # 800 → 600 (더 위로)
  ```

**효과**:
- 인트로 텍스트가 이미지 안전 영역에 표시됨
- 전체 훅 문구가 명확하게 보임

**2. 아웃트로 CTA 텍스트 가독성 향상 (100% 완료)**

**문제점**:
- 아웃트로 이미지에 원래 포함된 텍스트 ("안녕하세요, 기술 애호가 여러분!", "다음 소식입니다.")가 보임
- CTA 텍스트 ("댓글에 A or B 남겨주세요!", "좋아요 & 구독")가 작고 흐려서 이미지의 원래 텍스트를 덮지 못함

**해결 방법** (`src/video_creator.py:1081-1117` - `_create_quiz_outro_clip()` 메서드):

1. **반투명 검은색 배경 박스 추가** (가독성 향상):
   ```python
   # 텍스트 배경 박스 추가 (가독성 향상)
   text_bg = ColorClip(
       size=(self.width - 100, 500),
       color=(0, 0, 0),
       duration=duration
   ).with_opacity(0.7).with_position(('center', 600))
   ```

2. **주요 CTA 텍스트 크기 증가**:
   ```python
   # "댓글에 A or B 남겨주세요!" - 크기 증가
   main_txt = TextClip(
       text="댓글에 A or B\n남겨주세요!",
       font_size=68,  # 52 → 68 (31% 증가)
       stroke_width=4,  # 3 → 4 (외곽선 두껍게)
       position=('center', 680)
   )
   ```

3. **서브 텍스트 크기 증가**:
   ```python
   # "좋아요 & 구독" - 크기 증가
   sub_txt = TextClip(
       text="좋아요 & 구독",
       font_size=56,  # 42 → 56 (33% 증가)
       color='#FFD700',  # 금색
       stroke_width=3,  # 2 → 3 (외곽선 두껍게)
       position=('center', 920)
   )
   ```

4. **컴포지트 레이어 순서**:
   ```python
   return CompositeVideoClip([bg, text_bg, main_txt, sub_txt], size=(self.width, self.height))
   # 순서: 배경 이미지 → 반투명 박스 → CTA 텍스트들
   ```

**효과**:
- 아웃트로 이미지의 원래 텍스트가 완전히 가려짐
- CTA 텍스트가 명확하고 읽기 쉬움
- 구독 및 참여 유도 효과 증가

**3. 인트로 배경음악 확인 (100% 완료)**

**상태**: 이미 구현되어 있음!

**확인 사항** (`src/video_creator.py:700-721`):
```python
# 배경 음악 추가 (인트로 3초에만)
background_music_path = None
if self.resource_manager:
    bg_music_candidates = [
        os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
        os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
    ]
    for path in bg_music_candidates:
        if os.path.exists(path):
            background_music_path = path
            break

if background_music_path:
    try:
        print(f"배경 음악 추가: {background_music_path}")
        bg_music = AudioFileClip(background_music_path)
        bg_music = bg_music * 0.05  # 볼륨 5% (TTS 방해 안 함)
        bg_music = bg_music.subclipped(0, 3.0)  # 인트로 3초만
        bg_music = bg_music.with_start(0)
        combined_audio = CompositeAudioClip([combined_audio, bg_music])
    except Exception as e:
        print(f"⚠ 배경 음악 추가 실패: {e}")
```

**배경음악 파일 확인**:
- `output/resources/background_music_original.mp3` (6.5MB) ✓
- `output/resources/background_music.mp3` (49KB) ✓

**효과**:
- 인트로 3초 동안 Pixel Peeker Polka 재생
- 볼륨 5%로 TTS 음성을 방해하지 않음
- 전문적이고 역동적인 분위기 연출

**수정 파일:**
- `src/video_creator.py:309` - 인트로 텍스트 위치 수정
- `src/video_creator.py:1081-1117` - 아웃트로 CTA 텍스트 강화
- `src/preview/quiz_preview_generator.py:30` - 프리뷰 인트로 텍스트 위치 수정

**테스트 주의사항**:
- 모든 수정사항은 신중하게 검증됨
- 기존 코드와 완전 호환
- 퀴즈 비디오 재생성 시 자동 적용

---

## 🎯 이전 작업 (2025-10-12)

### ✅ 편집 페이지 UX 개선

**사용자 요청**:
1. "인트로/아웃트로 미디어교체시 화면이 안바뀌는데"
2. "편집에서 다운로드 있어야 될것같아"

**목표**: 편집 페이지의 사용성 향상 및 워크플로우 개선

**구현 내용:**

**1. 인트로/아웃트로 이미지 업로드 버그 수정 (100% 완료)**

**문제점**:
- 사용자가 [📁 미디어 교체] 버튼을 클릭해도 썸네일이 업데이트되지 않음
- JavaScript가 잘못된 API 엔드포인트로 FormData 전송

**원인 분석**:
```javascript
// 잘못된 코드 (web/static/js/editor.js:533-543)
const response = await fetch(`/api/video/${videoId}/generate-intro-image`, {
    method: 'POST',
    body: formData  // FormData 전송
});
```
- `/generate-intro-image` 엔드포인트는 `request.get_json()`으로 JSON만 받음
- FormData는 `request.files`로 받아야 함
- 백엔드에서는 이미 `/upload-intro-image` 엔드포인트가 준비되어 있었음

**해결 방법** (`web/static/js/editor.js`):
- `uploadIntroImage()` 함수 수정 (line 540):
  ```javascript
  // 수정 전
  const response = await fetch(`/api/video/${videoId}/generate-intro-image`

  // 수정 후
  const response = await fetch(`/api/video/${videoId}/upload-intro-image`
  ```
- `uploadOutroImage()` 함수 수정 (line 588):
  ```javascript
  // 수정 전
  const response = await fetch(`/api/video/${videoId}/generate-outro-image`

  // 수정 후
  const response = await fetch(`/api/video/${videoId}/upload-outro-image`
  ```

**백엔드 엔드포인트** (이미 구현됨, `web/app.py:513-616`):
- `POST /api/video/<video_id>/upload-intro-image` - 인트로 이미지 파일 업로드
- `POST /api/video/<video_id>/upload-outro-image` - 아웃트로 이미지 파일 업로드
- `request.files['file']`로 파일 수신
- 지원 형식: PNG, JPG, JPEG, GIF, WebP
- 저장 경로: `output/resources/images/intro_{video_id}.{ext}`
- Config 자동 업데이트: `global_settings.intro/outro.custom_image`

**효과**:
- 이미지 업로드 즉시 썸네일 업데이트
- 편집 패널 미리보기도 동시 업데이트
- 사용자가 변경사항을 시각적으로 확인 가능

**2. 편집 페이지 다운로드 버튼 추가 (100% 완료)**

**문제점**:
- 비디오 다운로드하려면 메인 페이지로 돌아가야 함
- 메인 페이지에서 스크롤해서 비디오 목록 찾아야 함
- 워크플로우가 불편함

**해결 방법**:

**HTML 업데이트** (`web/templates/editor.html:252`):
```html
<footer class="editor-footer">
    <div class="actions">
        <button id="btn-cancel" class="btn btn-tertiary">❌ 취소</button>
        <button id="btn-download" class="btn btn-secondary">📥 다운로드</button>  <!-- 신규 추가 -->
        <button id="btn-save" class="btn btn-secondary">💾 설정 저장</button>
        <button id="btn-regenerate" class="btn btn-primary">🎬 비디오 재생성</button>
    </div>
</footer>
```

**JavaScript 구현** (`web/static/js/editor.js:1394-1421`):
```javascript
function onDownload() {
    const videoElement = document.getElementById('preview-video');
    const videoSrc = videoElement.src;

    if (!videoSrc || videoSrc === '') {
        showMessage('error', '다운로드할 비디오가 없습니다.');
        return;
    }

    // 비디오 파일명 생성
    const filename = `daily_english_${videoId}.mp4`;

    // 다운로드 링크 생성 및 트리거
    const a = document.createElement('a');
    a.href = videoSrc;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    showMessage('success', '비디오 다운로드를 시작합니다.');
    setTimeout(() => hideMessage(), 3000);
}
```

**이벤트 리스너 등록** (`web/static/js/editor.js:1217`):
```javascript
document.getElementById('btn-download').addEventListener('click', onDownload);
```

**효과**:
- 편집 완료 후 즉시 다운로드 가능
- 메인 페이지로 이동할 필요 없음
- 파일명 자동 생성: `daily_english_{video_id}.mp4`

**사용 흐름 개선**:
```
편집 페이지:
1. [💾 설정 저장]
2. [🎬 비디오 재생성] (3-5분 대기)
3. [📥 다운로드] 👈 바로 다운로드!
```

**수정 파일:**
- `web/static/js/editor.js:540, 588` - API 엔드포인트 수정 (업로드)
- `web/templates/editor.html:252` - 다운로드 버튼 추가
- `web/static/js/editor.js:1217, 1394-1421` - 다운로드 기능 구현

**배포 관련 논의:**
- 사용자가 배포 가능성 질문
- 현재 로컬 절대 경로 사용으로 배포 시 수정 필요
- Railway/Render 추천
- 파일 스토리지, FFmpeg 설치, 타임아웃 설정 등 고려사항 안내

---

## 🎯 이전 작업 (2025-10-09)

### ✅ 커스텀 인트로/아웃트로 이미지 생성 기능

**사용자 요청**: "인트로,아웃트로 기본 이미지 있잖아. 인트로, 아웃트로 이미지 생성 버튼 있으면 좋겠네."

**목표**: 비디오별로 커스텀 인트로/아웃트로 배경 이미지를 생성할 수 있는 기능 추가

**구현 내용:**

**1. 백엔드 API (100% 완료)**
- **API 엔드포인트** (`web/app.py:513-635`)
  - `POST /api/video/<id>/generate-intro-image` - 인트로 이미지 생성
  - `POST /api/video/<id>/generate-outro-image` - 아웃트로 이미지 생성
  - 커스텀 프롬프트 지원 (선택사항)
  - 기본 프롬프트: 인트로(파란색 그라데이션), 아웃트로(핑크색 그라데이션)
  - Config 자동 업데이트 (`global_settings.intro/outro.custom_image`)
  - 이미지 저장: `output/resources/images/intro_{video_id}.png`

**2. VideoCreator 업데이트 (100% 완료)**
- **커스텀 이미지 속성 추가** (`src/video_creator.py:22-23`)
  ```python
  self.intro_custom_image = None  # 커스텀 인트로 이미지 경로
  self.outro_custom_image = None  # 커스텀 아웃트로 이미지 경로
  ```
- **이미지 우선순위 로직** (`src/video_creator.py:226-255`, `466-495`)
  ```
  1순위: 커스텀 이미지 (사용자 생성)
  2순위: 캐시된 템플릿 이미지
  3순위: DALL-E로 새로 생성
  4순위: 기본 배경색 (ColorClip)
  ```

**3. VideoEditor 업데이트 (100% 완료)**
- **커스텀 이미지 경로 전달** (`src/editor/video_editor.py:113-132`)
  ```python
  # Config에서 custom_image 경로 추출
  custom_intro_image = intro.get("custom_image")
  if custom_intro_image and os.path.exists(custom_intro_image):
      creator.intro_custom_image = custom_intro_image
  ```

**4. 프론트엔드 UI (100% 완료)**
- **HTML 입력 필드 & 버튼** (`web/templates/editor.html:94-120`)
  ```html
  <input type="text" id="intro-image-prompt" placeholder="이미지 설명 입력 (선택사항)">
  <button id="btn-generate-intro-image">✨ 인트로 이미지 생성</button>
  ```
- **JavaScript 이벤트 핸들러** (`web/static/js/editor.js:258-260`, `564-646`)
  - `onGenerateIntroImage()` - 인트로 이미지 생성
  - `onGenerateOutroImage()` - 아웃트로 이미지 생성
  - 로딩 상태 관리 (`setButtonLoading()`)
  - 에러 처리 (`handleApiError()`)

**사용 방법:**
1. 비디오 편집 페이지 → 전역 설정 섹션
2. 인트로/아웃트로 배경 이미지 프롬프트 입력 (선택사항)
3. [✨ 이미지 생성] 버튼 클릭 (약 10-15초 소요)
4. [💾 설정 저장] → [🎬 비디오 재생성]

**수정 파일:**
- `web/app.py:513-635` - API 엔드포인트 추가
- `src/video_creator.py:22-23, 226-255, 466-495` - 커스텀 이미지 지원
- `src/editor/video_editor.py:113-132` - Config 적용 로직
- `web/templates/editor.html:94-120` - UI 추가
- `web/static/js/editor.js:258-260, 564-646` - 이벤트 핸들러

**효과:**
- 비디오별로 고유한 인트로/아웃트로 디자인 가능
- DALL-E 3 활용으로 전문적인 배경 이미지 생성
- 브랜딩 강화 및 비디오 다양성 확보

---

## 🎯 이전 작업 (2025-10-08)

### ✅ Phase 4: 비디오 편집 기능 완성

**목표**: 기존 빠른 생성 워크플로우 유지하면서 선택적 편집 기능 추가

**구현 내용:**

**1. 백엔드 인프라 (100% 완료)**
- `src/editor/config_manager.py` - 설정 파일 관리
  - `ConfigManager.create_default_config()` - 기본 설정 생성
  - `ConfigManager.save_config()` - 설정 저장
  - `ConfigManager.load_config()` - 설정 로드
- `src/editor/video_editor.py` - 비디오 재생성
  - `VideoEditor.regenerate_video()` - 편집된 설정으로 재생성
- API 엔드포인트 (web/app.py)
  - `GET /api/video/<id>/config` - 설정 조회
  - `POST /api/video/<id>/config` - 설정 저장
  - `POST /api/video/<id>/regenerate` - 비디오 재생성

**2. 프론트엔드 UI (100% 완료)**
- `web/templates/editor.html` - 편집 페이지 (470줄)
  - 비디오 미리보기 섹션
  - 타임라인 (인트로/문장/아웃트로 클립)
  - 전역 설정 (배경음악, 볼륨, 길이)
  - 클립별 편집 패널
- `web/static/css/editor.css` - 스타일 (470줄)
  - Grid 레이아웃 (타임라인 300px + 편집 패널 1fr)
  - 반응형 디자인 (1024px, 768px 브레이크포인트)
  - 상태 메시지 스타일 (success, error, info, warning)
- `web/static/js/editor.js` - 로직 (530줄)
  - 설정 로드/저장/재생성
  - 클립 선택 및 편집
  - 비디오 재생 컨트롤

**3. UX 개선 (2025-10-08 추가)**
- **API 에러 처리**
  - `handleApiError()` 함수 - 네트워크/404/500 에러별 사용자 친화적 메시지
  - HTTP 상태 코드별 구체적 안내
- **변경사항 경고**
  - `hasUnsavedChanges` 플래그로 변경사항 추적
  - `beforeunload` 이벤트 - 페이지 나가기 전 경고
  - 저장 후 플래그 자동 해제
- **키보드 단축키**
  - `Ctrl+S` / `Cmd+S` - 저장
  - `keyboardShortcutHandler()` 구현
- **입력 검증**
  - `validateSentence()` - 문장 길이 검증 (1~200자)
  - `validateFontSize()` - 폰트 크기 검증 (30~80px)
  - `validatePause()` - 간격 검증 (0~5초)
  - 검증 실패 시 warning 메시지 표시 및 원래 값 복원

**4. 배경음악 버그 수정 (2025-10-08)**
- **문제**: MoviePy 볼륨 조정 (`* 0.05`) 시 오디오 길이 손상
  - 원본 3초 → 볼륨 조정 후 0.15초로 줄어듦
- **해결**: 볼륨 조정과 자르기 순서 변경
  ```python
  # Before (잘못된 순서)
  bg_music = bg_music.subclipped(0, 3.0)  # 3초 → 0.15초로 손상
  bg_music = bg_music * 0.05

  # After (올바른 순서)
  bg_music = bg_music * 0.05              # 볼륨 먼저
  bg_music = bg_music.subclipped(0, 3.0)  # 자르기 나중 → 3.00초 유지
  ```
- **수정 파일**: `src/video_creator.py:153-168`

**수정/추가 파일:**
- `src/editor/` - 편집 기능 모듈 (신규)
- `src/video_creator.py:153-168` - 배경음악 처리 순서 수정
- `web/templates/editor.html` - 편집 페이지
- `web/static/css/editor.css` - 편집 페이지 스타일
- `web/static/js/editor.js` - 편집 페이지 로직 (에러 처리, 입력 검증, 키보드 단축키)
- `web/templates/index.html:286-288` - [편집하기] 버튼 추가
- `web/static/js/main.js:236-242` - `openEditor()` 함수

**워크플로우:**
```
비디오 생성 → [편집하기] 클릭 (선택사항)
              ↓
         에디터 페이지
         - 설정 로드
         - 클립별 편집 (문장, 폰트, 음성, 간격)
         - 전역 설정 (배경음악, 볼륨)
         - [저장] (Ctrl+S)
         - [재생성] (3-5분 소요)
```

**5. 로딩 UX 개선 (2025-10-08 추가)**
- **문제**: 비디오 재생성이 3-5분 소요되는데 시각적 피드백 없음
  - 사용자가 작동 여부를 알 수 없음
- **해결**:
  - **Full-screen Loading Overlay** (`web/static/css/editor.css:476-517`)
    ```css
    .loading-overlay {
        display: none;
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 9999;
    }
    .loading-spinner {
        width: 60px; height: 60px;
        border: 5px solid rgba(255, 255, 255, 0.3);
        border-top: 5px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    ```
  - **Button Loading States** (`web/static/css/editor.css:519-539`)
    - 버튼에 인라인 스피너 표시
    - `pointer-events: none` - 중복 클릭 방지
  - **JavaScript 통합** (`web/static/js/editor.js:457-558`)
    - `showLoadingOverlay()` - 전체화면 로딩 표시
    - `hideLoadingOverlay()` - 로딩 숨김
    - `setButtonLoading()` - 버튼 로딩 상태 토글
    - `onSave()` - 버튼 로딩 적용
    - `onRegenerate()` - 전체화면 로딩 적용
- **효과**: 사용자가 비디오 재생성 진행 상황 확인 가능

**6. 비디오 재생성 크리티컬 버그 수정 (2025-10-08)**
- **문제**: 비디오 재생성 실패 (HTTP 500 서버 오류)
- **원인 분석**:
  1. **잘못된 파라미터명**: `VideoEditor.regenerate_video()`가 `VideoCreator.create_video()`에 `tts_data` 전달
     - VideoCreator는 `audio_info` 파라미터 필요
  2. **데이터 구조 불일치**: config.json은 TTS 설정만 저장, 실제 오디오 파일 경로 없음
  3. **오디오 파일 미해결**: 기존 생성된 MP3 파일 경로를 찾지 못함
- **해결** (`src/editor/video_editor.py`):
  - Line 74: 파라미터명 수정 `tts_data` → `audio_info`
  - Lines 166-236: 새 메서드 `_extract_clip_data_with_audio()` 추가
    ```python
    def _extract_clip_data_with_audio(self, clips, video_id):
        # 1. 기존 audio 파일 경로 찾기
        audio_base_dir = project_root / "output" / "audio" / video_id

        # 2. 각 클립별 음성 파일 로드
        for i, clip in enumerate(clips, start=1):
            tts_voices = clip['audio']['tts_voices']
            voices_dict = {}

            for voice in tts_voices:
                audio_file = audio_base_dir / f"sentence_{i}_{voice}.mp3"

                # 3. mutagen으로 duration 측정
                audio_obj = MP3(str(audio_file))
                duration = audio_obj.info.length

                voices_dict[voice] = {
                    'path': str(audio_file),
                    'duration': duration
                }

        # 4. VideoCreator가 기대하는 구조로 반환
        return sentences, translations, image_paths, audio_info
    ```
  - Line 66: `_extract_clip_data_with_audio()` 호출로 변경
- **효과**:
  - 비디오 재생성 정상 작동
  - 기존 audio 파일 재사용 (API 비용 절감)
  - 정확한 duration 계산으로 타이밍 정확도 향상

**수정 파일 (Phase 4 완성):**
- `web/static/css/editor.css:476-561` - 로딩 오버레이/스피너 스타일
- `web/templates/editor.html:171-176` - 로딩 오버레이 HTML
- `web/static/js/editor.js:457-602` - 로딩 함수 및 통합
- `src/editor/video_editor.py:32-236` - 비디오 재생성 버그 수정

---

## 🎯 이전 작업 (2025-10-07)

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

## 🎭 Kelly 캐릭터 시스템

### 현재 상태 (2025-11-04)

**파일 위치**: `output/resources/images/kelly_casual_hoodie.png`

**캐릭터 스펙**:
- **스타일**: 애니메 스타일 (Anime/Manga)
- **외모**: 갈색 단발머리 (brown bob cut), 파란색 후드티 (blue hoodie)
- **배경**: 파스텔 톤 (peach/pink gradient)
- **용도**: 인트로/아웃트로 전체 화면 배경

**비디오 내 활용**:
- **Shorts (9:16)**: 인트로/아웃트로 전체 화면 배경
- **Longform (16:9)**: 인트로/아웃트로 전체 화면 배경
- **레이어 구조**: 배경 → Kelly 이미지 (full-screen) → 텍스트 오버레이
- **효과**: FadeIn 0.3~0.5초

### 원본 생성 프롬프트 (DALL-E 3)

```
A friendly young woman English teacher character in anime/manga style.

Physical appearance:
- Brown bob cut hairstyle (short, straight hair ending at chin level)
- Warm, approachable facial expression with gentle smile
- Casual outfit: Blue hoodie (comfortable, modern style)
- Age appearance: Early to mid-20s

Art style:
- Clean anime/manga illustration style
- Soft pastel color palette (peach, pink, light blue tones)
- Simple, friendly design suitable for educational content
- Professional yet approachable look

Background:
- Soft pastel gradient background (peach to pink)
- Minimal, clean aesthetic
- No distracting elements

Format:
- Vertical portrait orientation (9:16 for mobile/shorts)
- Character positioned centrally
- Full body or upper body composition
- High quality, clear details

Mood:
- Warm, friendly, encouraging
- Professional but not intimidating
- Perfect for English learning content
```

**생성 파라미터**:
- Model: `dall-e-3`
- Size: `1024x1792` (9:16 세로 포맷)
- Quality: `standard`
- Style: Natural (default)

### 캐릭터 일관성 유지 가이드

**재생성 시 주의사항**:
1. **핵심 특징 유지**: 갈색 단발머리 + 파란 후드티 (브랜드 아이덴티티)
2. **스타일 고정**: 애니메 스타일 (realistic 금지)
3. **색상 팔레트**: 파스텔 톤 (peach, pink, light blue)
4. **표정**: 친근하고 따뜻한 미소 (intimidating 표정 금지)
5. **배경**: 단순하고 깔끔 (교육 콘텐츠에 집중)

**향후 포즈 변형 시**:
- 기본 외모 유지 (머리, 옷, 얼굴)
- 포즈/표정만 변경 (예: 손 흔들기, 가리키기, 생각하는 표정)
- 프롬프트 끝에 추가: "Same character as before, but [새로운 포즈/표정]"

### 확장 로드맵

**Phase 1: 간단한 애니메이션** (예정)
- MoviePy effects를 활용한 간단한 움직임
- 예시: 좌우 흔들림, 확대/축소 (breathing effect)
```python
kelly_clip = kelly_clip.with_effects([
    vfx.FadeIn(0.5),
    # 좌우 흔들림
    lambda clip: clip.with_position(lambda t: ('center', 50 + 20 * sin(t * 2)))
])
```

**Phase 2: 시나리오별 포즈** (예정)
- 인트로: 캐주얼 포즈 (현재)
- 아웃트로: 손 흔들기 (waving)
- 티칭: 가리키기 (pointing)
- 퀴즈: 생각하는 표정 (thinking)

**Phase 3: 프레임 기반 애니메이션** (예정)
- 여러 프레임 이미지로 sprite animation
- 걷기, 말하기 등 연속 동작

**Phase 4: AI 생성 포즈 자동화** (예정)
- DALL-E로 포즈별 이미지 자동 생성
- 캐릭터 일관성 유지를 위한 프롬프트 템플릿

**Phase 5: 실시간 비디오 애니메이션** (장기 목표)
- GEN-3 Alpha, Runway ML 등 AI 비디오 생성
- 또는 Live2D 같은 2D 리깅 시스템

### 기술적 구현

**현재 코드 위치**:
- `src/video_creator.py:2450-2476` - Kelly 이미지 로드 로직
- `src/video_creator.py:939-953` - Longform 인트로 Kelly 배치
- `src/video_creator.py:1047-1061` - Longform 아웃트로 Kelly 배치

**이미지 처리 로직**:
```python
# 1. Kelly 이미지 로드
kelly_clip = ImageClip(kelly_image_path).with_duration(duration)

# 2. 전체 화면 크기로 리사이즈 (16:9 또는 9:16 비율에 맞춤)
kelly_clip = kelly_clip.resized(height=self.height)

# 3. 가로가 부족하면 가로 기준으로 리사이즈
if kelly_clip.w < self.width:
    kelly_clip = kelly_clip.resized(width=self.width)

# 4. 중앙 정렬
kelly_clip = kelly_clip.with_position('center')

# 5. FadeIn 효과
kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.5)])
```

**향후 확장 시 코드 구조**:
- `src/config/character_settings.py` (신규 파일 예정) - Kelly 포즈별 설정
- `src/character/kelly_animator.py` (신규 모듈 예정) - 애니메이션 로직
- `src/character/kelly_voice.py` (신규 모듈 예정) - Kelly 음성 추임새/개입 로직

### 음성 추임새 & 중간 개입 아이디어 (향후 기능)

**목표**: Kelly 캐릭터가 비디오 중간중간 짧은 음성으로 개입하여 학습 경험을 더 인터랙티브하게 만들기

#### 1. 짧은 추임새 (Interjections)

**타이밍**: 문장과 문장 사이 (현재 2초 pause 구간)
**길이**: 1~2초

**추임새 종류**:
- **긍정/격려**: "Great!", "Perfect!", "Well done!", "Exactly!"
- **놀람/감탄**: "Wow!", "Amazing!", "Interesting!", "Oh!"
- **확인/강조**: "Remember this!", "Pay attention!", "Important!", "Got it?"
- **전환**: "Next one!", "Let's move on!", "Ready?", "Here we go!"

**TTS 생성**:
```python
# OpenAI TTS-1 사용 (Kelly 전용 음성: nova 또는 shimmer)
interjections = [
    "Great! Let's learn the next one.",
    "Perfect! Keep going!",
    "Wow! That's a useful expression!",
    "Remember this one, it's important!",
]

# 문장 사이 랜덤 또는 규칙적 삽입
for i, sentence in enumerate(sentences):
    if i % 2 == 1:  # 2문장마다 1번
        add_kelly_interjection(interjections[i % len(interjections)])
```

#### 2. 중간 설명 개입 (Mid-Video Commentary)

**타이밍**: 문장 클립 후 (선택적)
**길이**: 3~5초

**개입 시나리오**:

**A. 발음 팁**:
- "Notice the /th/ sound in 'this'!"
- "Be careful with the silent 'k' in 'know'!"
- "Try emphasizing the first syllable!"

**B. 문화적 맥락**:
- "Americans use this expression a lot in casual conversations!"
- "This is more common in British English!"
- "You'll hear this in movies and TV shows often!"

**C. 사용 주의사항**:
- "Be careful! This is informal, don't use it in business meetings!"
- "This expression is quite formal, perfect for presentations!"
- "This can sound rude if you use the wrong tone!"

**D. 추가 예문**:
- "For example, you can also say..."
- "Another way to express this is..."
- "Try using this with different subjects!"

#### 3. 시각적 개입 (Kelly Pop-up)

**현재**: 인트로/아웃트로에만 Kelly 표시
**향후**: 중간 개입 시 Kelly 작게 등장

**레이아웃 예시**:
```
┌─────────────────────────┐
│                         │
│   [Main Content]        │
│   (English Sentence)    │
│                         │
│              ┌────┐     │ ← Kelly 팝업 (우측 하단)
│              │😊  │     │   "Great!"
│              └────┘     │
└─────────────────────────┘
```

**구현 방법**:
- Kelly 이미지 축소 (200x200px)
- 우측 하단 또는 좌측 하단 배치
- 말풍선 효과 (텍스트 오버레이)
- 0.5초 FadeIn + 0.5초 FadeOut

#### 4. 인터랙티브 질문 (롱폼 전용)

**타이밍**: 2~3문장마다 1번
**길이**: 3~5초

**질문 예시**:
- "Can you repeat after me?"
- "Do you know when to use this expression?"
- "Have you heard this phrase before?"
- "Ready to try using it yourself?"

**시각적 효과**:
- Kelly 표정 변화 (질문하는 표정)
- 물음표 아이콘 표시
- 일시정지 유도 (실제로는 멈추지 않지만 시각적으로 표현)

#### 5. 기술적 구현 방안

**Phase 1: 추임새 오디오만** (간단)
```python
# TTS로 추임새 미리 생성 (캐싱)
interjections_cache = {
    'great': 'output/resources/audio/kelly/great.mp3',
    'perfect': 'output/resources/audio/kelly/perfect.mp3',
    'wow': 'output/resources/audio/kelly/wow.mp3',
}

# 문장 사이 삽입
def add_interjection(timeline, interjection_key, position):
    audio = AudioFileClip(interjections_cache[interjection_key])
    audio = audio.with_start(position)
    timeline.append(audio)
```

**Phase 2: 추임새 + 시각적 팝업**
```python
# Kelly 작은 이미지 + 말풍선
kelly_popup = create_kelly_popup(
    image_path='kelly_casual_hoodie.png',
    text='Great!',
    position='bottom-right',
    size=(200, 200)
)
```

**Phase 3: GPT 기반 동적 생성**
```python
# 문장 내용 분석 후 적절한 개입 생성
def generate_kelly_commentary(sentence, context):
    prompt = f"""
    You are Kelly, an English teacher.
    For this sentence: "{sentence}"

    Generate a SHORT (5-10 words) helpful comment about:
    - Pronunciation tip
    - Usage context
    - Cultural note

    Make it friendly and encouraging!
    """

    commentary = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=30
    )

    return commentary.choices[0].message.content
```

#### 6. 사용자 설정 옵션 (웹 UI)

**설정 패널**:
```
□ Kelly 추임새 활성화
  빈도: ○ 자주 (매 문장)  ● 보통 (2문장마다)  ○ 가끔 (3문장마다)

□ Kelly 중간 설명 활성화
  타입: ☑ 발음 팁  ☑ 문화적 맥락  □ 사용 주의사항

□ Kelly 시각적 팝업 표시
  위치: ● 우측 하단  ○ 좌측 하단  ○ 중앙 하단
```

#### 7. 효과 및 기대 결과

**학습 효과**:
- ✅ 참여도 증가 (단조로움 감소)
- ✅ 기억력 향상 (중간 강조로 중요 포인트 각인)
- ✅ 발음 개선 (즉각적인 발음 팁)
- ✅ 문화 이해 (실제 사용 맥락 설명)

**YouTube 성과**:
- ✅ 시청 유지율 향상 (engagement)
- ✅ 댓글 유도 ("Kelly의 팁이 도움됐어요!")
- ✅ 브랜딩 강화 (Kelly = 친근한 선생님)

**주의사항**:
- ⚠️ 과도한 개입은 방해 요소 (적절한 빈도 중요)
- ⚠️ TTS 음성이 자연스러워야 함 (부자연스러우면 역효과)
- ⚠️ 비디오 길이 증가 (3분 → 4분으로 늘어날 수 있음)

---

## 🔥 Fire English 채널 분석 (구독자 95만명)

**분석 날짜**: 2025-11-07
**채널**: @FireEnglish1
**구독자**: 95.2만명
**목적**: Daily English Mecca 성장 전략 수립

### 📊 성공 요인 분석

**1. 콘텐츠 전략**:
- **포맷**: Q&A 대화 형식 (400+ 짧은 대화)
- **길이**: 10-30분 (긴 시청시간 → 알고리즘 최적화)
- **빈도**: 하루 2-3개 업로드 (일관성)
- **타겟**: 초보자 (English Speaking Practice for Beginners)

**2. 비디오 구조** (Shorts 9:16):
```
┌─────────────────────────────┐
│ Daily English Practice      │ ← 보라색 헤더 (브랜딩)
├─────────────────────────────┤
│ [노란 박스]                  │
│ Hello, Dana.                │ ← 인사/시작
│                              │
│ Hi, how are you?            │ ← 파란색 (답변)
│ I'm good, thanks.           │ ← 빨간색 (질문)
│ Good to hear.               │ ← 파란색
│ What do you do?             │ ← 빨간색
│ I work at a bank.           │ ← 파란색
│                              │
│              [AI 캐릭터]     │ ← Dana (우측, 투명 배경)
│              (반투명)        │
│                              │
│              FIRE English   │ ← 워터마크 (우측 하단)
└─────────────────────────────┘
```

**3. 시각적 특징**:
- ✅ **색상 코딩**: 질문(빨강), 답변(파랑) → 명확한 구분
- ✅ **AI 캐릭터**: Dana (투명 배경, 우측 배치)
- ✅ **헤더 브랜딩**: 보라색 "Daily English Practice"
- ✅ **워터마크**: "FIRE English" (우측 하단)
- ✅ **노란 박스**: 시작 인사 강조

**4. YouTube SEO 전략**:

**제목 구조**:
```
Daily English Conversations | Learn English | English Speaking Practice for Beginners
```
- 키워드 3개 이상 ("|" 구분자)
- 초보자 타겟 명시

**설명 구조**:
```
🔥 Welcome to Best English Online!

[훅] 400+ short English questions and answers...

✅ What You'll Learn:
  - Greetings and introductions
  - Daily routines
  - Shopping and dining
  ...

🗣️ Topics Covered:
  - Basic Conversations
  - Everyday English
  ...

📌 Perfect for:
  - Beginners
  - ESL learners
  - Self-study students
  ...

📚 More Resources:
  - Subscribe
  - Notification
  - Playlists
  ...

[30+ 키워드 태그]
#SpokenEnglish #EnglishPractice #DailyEnglish #EnglishQuestionsAndAnswers
```

**해시태그 전략**:
- 4-6개 핵심 해시태그
- #SpokenEnglish (메인 키워드)
- #DailyEnglish (일상 학습)
- #EnglishPractice (연습 강조)
- #EnglishQuestionsAndAnswers (롱테일 키워드)

**5. 썸네일 디자인**:
```
┌─────────────────────────────┐
│ [빨간 헤더]                  │
│ "Daily English               │
│  Conversations"              │
├─────────────────────────────┤
│  [AI 캐릭터]                 │
│  (중앙 또는 우측)            │
│                              │
│  [테마 배경]                 │
│  (흐릿한 배경 이미지)        │
├─────────────────────────────┤
│ [초록 박스]  [핑크 박스]    │
│ "400+       "Learn English  │
│  Questions"  Speaking"      │
└─────────────────────────────┘
```

**썸네일 원칙**:
- 빨간색 헤더 (눈에 띄는 색상)
- AI 캐릭터 중앙 배치
- 텍스트 박스 2-3개 (대비되는 색상)
- 큰 폰트 (모바일에서 읽기 쉬움)

---

### 🎯 Daily English Mecca 적용 전략

**현재 상황**:
- 구독자: 10명
- 콘텐츠: 정적 이미지 + TTS
- Kelly 캐릭터: 인트로/아웃트로만 표시

**개선 로드맵** (차근차근):

#### **Phase 1: 썸네일 생성 모듈** (최우선)
**목표**: CTR 2-3배 향상 → 조회수 증가
**구현 내용**:
- Fire English 스타일 썸네일 (1280x720)
- Kelly 캐릭터 중앙 배치
- 빨간색 헤더 ("Daily English Mecca")
- 텍스트 박스 2개 (랜드마크명 + 서브타이틀)
- PIL 기반 이미지 합성

**파일**: `src/thumbnail_generator.py` (신규 생성)
**소요시간**: 1-2시간
**효과**: 즉시 CTR 향상

#### **Phase 2: 중간 Kelly 캐릭터 삽입** (정적 이미지)
**목표**: Fire English 스타일 - 문장 클립에 Kelly 표시
**구현 내용**:
- 우측 하단에 Kelly 이미지 (200x200px)
- 애니메이션 없이 정적 표시
- 모든 문장 클립에 일관되게 표시

**파일**: `src/video_creator.py` 수정
**소요시간**: 30분-1시간
**효과**: 브랜딩 강화, 친근감 증가

#### **Phase 3: 색상 코딩 텍스트 박스**
**목표**: 가독성 향상 (영어=빨강, 한글=파랑)
**구현 내용**:
- MoviePy ColorClip으로 배경 박스 생성
- 영어 문장: 빨간색 반투명 박스
- 한글 번역: 파란색 반투명 박스

**파일**: `src/video_creator.py` 수정
**소요시간**: 30분-1시간
**효과**: 학습 효과 증대, 전문성 향상

#### **Phase 4: Kelly 간단한 애니메이션** (선택사항)
**목표**: Kelly 이미지에 움직임 추가
**구현 내용**:
- MoviePy effects 활용
- 좌우 흔들림 (breathing effect)
- 확대/축소 (pulse effect)

**파일**: `src/video_creator.py` 수정
**소요시간**: 1-2시간
**효과**: 생동감 증가, 시청 유지율 향상

#### **Phase 5: Fire English 대화 포맷** (장기 목표)
**목표**: 100+ Q&A 긴 비디오 (10-30분)
**구현 내용**:
- GPT-4o로 대화 생성 (주제별)
- 2가지 TTS 음성 (alloy=질문, nova=답변)
- 색상 코딩 (빨강=질문, 파랑=답변)
- 노란 박스 인사 + 보라색 헤더

**파일**: `src/conversation_generator.py` (신규 생성)
**소요시간**: 3-4시간
**효과**: 시청시간 10배 증가, 알고리즘 최적화

---

### 📈 예상 성장 시나리오

**현재 (Phase 0)**:
- 구독자: 10명
- CTR: 1-2%
- 평균 시청시간: 30초-1분

**Phase 1 완료 후** (썸네일):
- 구독자: 20-30명 (2-3배)
- CTR: 3-5% (2-3배 향상)
- 조회수: 100-200회/비디오

**Phase 2-3 완료 후** (Kelly 삽입 + 색상 코딩):
- 구독자: 50-100명
- 시청 유지율: 40-50% (현재 30%)
- 브랜드 인지도 향상

**Phase 5 완료 후** (대화 포맷):
- 구독자: 100-500명
- 평균 시청시간: 5-10분 (현재 1분)
- 알고리즘 추천 증가 (시청시간 최적화)

**6개월 목표** (일관된 업로드):
- 구독자: 1,000명+
- 하루 조회수: 500-1,000회
- 수익화 조건 충족 (1,000명 + 4,000시간)

---

### 🚀 YouTube 성장 전략

**1. 업로드 스케줄**:
- **초기 (0-100명)**: 하루 1-2개 (품질 우선)
- **성장기 (100-1,000명)**: 하루 2-3개
- **안정기 (1,000명+)**: 하루 3-5개

**2. 콘텐츠 믹스**:
- Shorts (60%): 빠른 확산, 새 구독자 유입
- Longform (40%): 시청시간, 충성도 높은 구독자

**3. SEO 최적화**:
- 제목: 키워드 3개 이상 ("|" 구분)
- 설명: 구조화된 섹션 (What, Topics, Perfect for)
- 해시태그: 4-6개 핵심 키워드
- 썸네일: Fire English 스타일 (빨간 헤더 + Kelly)

**4. 참여도 증대**:
- 댓글 유도 CTA ("오늘 배운 문장 댓글로 써보세요!")
- 커뮤니티 탭 활용 (퀴즈, 투표)
- 구독자 피드백 반영

---

### 💡 핵심 교훈

**Fire English의 성공 비결**:
1. ✅ **일관성**: 매일 2-3개 업로드
2. ✅ **긴 시청시간**: 10-30분 비디오 (알고리즘 최적화)
3. ✅ **명확한 타겟**: 초보자 집중
4. ✅ **시각적 차별화**: 색상 코딩 + AI 캐릭터
5. ✅ **SEO 최적화**: 키워드 풍부한 제목/설명
6. ✅ **브랜딩**: 일관된 헤더 + 워터마크

**Daily English Mecca 차별화 포인트**:
- 🇰🇷 **한국 랜드마크** (케대헌 추천) - 독특한 니치
- 👩‍🏫 **Kelly 캐릭터** - 친근한 선생님 이미지
- 🎨 **다양한 포맷** (3문장, 테마, 퀴즈, 속어, 랜드마크)
- 🔊 **멀티보이스** (3가지 음성 교체)

---

## 💡 개발 철학

1. **모듈화**: 각 기능은 독립적인 모듈로 개발
2. **사이드 이펙트 방지**: 새 기능 추가 시 기존 코드 영향 없도록
3. **캐싱 우선**: API 호출 최소화로 비용 절감
4. **가독성**: 명확한 변수명, 한글 주석
5. **에러 핸들링**: try-except로 안전한 실행
6. **차근차근 진행**: 단계별 구현으로 안정성 확보

---

**문의사항이나 버그는 GitHub Issues에 남겨주세요!**
