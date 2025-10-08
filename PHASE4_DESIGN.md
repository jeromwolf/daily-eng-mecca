# Phase 4: 편집 기능 설계 (확장 가능한 구조)

**작성일:** 2025-10-07
**목표:** 기존 빠른 생성 플로우를 유지하면서, 선택적 편집 기능 추가

---

## 1. 핵심 원칙

### ✅ 기존 워크플로우 보존
```
[현재 - 빠른 생성 모드]
웹 UI 입력 → 비디오 자동 생성 → 완료 (계속 사용)
⏱️ 예상 시간: 3-5분
```

### 🆕 편집 모드 추가 (선택사항)
```
[신규 - 편집 모드]
웹 UI 입력 → 비디오 자동 생성 → [편집하기 버튼]
                                    ↓
                            편집 페이지 진입
                                    ↓
                            설정 수정 (배경음악, 텍스트 등)
                                    ↓
                            [재생성 버튼] → 최종 비디오
⏱️ 예상 시간: 10-15분 (편집 포함)
```

**핵심:** 편집하지 않으면 기존과 100% 동일하게 작동

---

## 2. 시스템 아키텍처

### 2.1 디렉토리 구조
```
daily-english-mecca/
├── src/
│   ├── video_creator.py          (기존 - 변경 없음)
│   ├── editor/                    (신규)
│   │   ├── __init__.py
│   │   ├── video_editor.py        # 편집 설정 적용 엔진
│   │   ├── config_manager.py      # JSON 설정 관리
│   │   └── plugins/               # 미래 확장용
│   │       ├── __init__.py
│   │       ├── text_plugin.py
│   │       ├── audio_plugin.py
│   │       └── filter_plugin.py
├── web/
│   ├── app.py                     (기존 API 유지 + 신규 API 추가)
│   ├── templates/
│   │   ├── index.html             (기존 - 변경 없음)
│   │   └── editor.html            (신규)
│   └── static/
│       ├── css/
│       │   └── editor.css         (신규)
│       └── js/
│           └── editor.js          (신규)
└── output/
    └── edit_configs/              (신규 - 편집 설정 저장)
        └── video_123_config.json
```

### 2.2 데이터 구조

#### 비디오 편집 설정 (JSON)
```json
{
  "version": "1.0",
  "video_id": "daily_english_20251007_123",
  "created_at": "2025-10-07T13:30:00",
  "edited_at": "2025-10-07T13:45:00",

  "global_settings": {
    "background_music": {
      "file": "carefree.mp3",
      "volume": 0.05,
      "enabled": true
    },
    "intro": {
      "enabled": true,
      "duration": 3,
      "text": "오늘의 3문장",
      "font_size": 65,
      "position": "center"
    },
    "outro": {
      "enabled": true,
      "duration": 2
    }
  },

  "clips": [
    {
      "clip_id": "sentence_0",
      "type": "sentence",
      "sentence_index": 0,
      "sentence_text": "Hello, how are you?",
      "translation": "안녕하세요, 어떻게 지내세요?",

      "audio": {
        "tts_voice": "alloy",
        "pause_after": 2.0
      },

      "text": {
        "font_size": 48,
        "position": "center",
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 3,
        "enabled": true
      },

      "image": {
        "path": "output/resources/images/image_0.jpg",
        "filter": null
      }
    },
    {
      "clip_id": "sentence_1",
      "type": "sentence",
      "sentence_index": 1,
      "sentence_text": "I'm fine, thank you.",
      "translation": "잘 지내요, 감사합니다.",

      "audio": {
        "tts_voice": "nova",
        "pause_after": 2.0
      },

      "text": {
        "font_size": 52,
        "position": "center",
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 3,
        "enabled": true
      },

      "image": {
        "path": "output/resources/images/image_1.jpg",
        "filter": null
      }
    }
  ]
}
```

---

## 3. API 설계

### 3.1 기존 API (변경 없음)
```python
POST /api/generate
- 입력: sentences, translations, format 등
- 출력: video_path
- 동작: 기존과 100% 동일
```

### 3.2 신규 편집 API
```python
# 1. 편집 설정 가져오기
GET /api/video/<video_id>/config
Response:
{
  "config": { ... },  # 위 JSON 구조
  "video_path": "/output/videos/xxx.mp4",
  "thumbnail": "/output/thumbnails/xxx.jpg"
}

# 2. 편집 설정 저장
POST /api/video/<video_id>/config
Request:
{
  "global_settings": { ... },
  "clips": [ ... ]
}
Response:
{
  "success": true,
  "message": "설정이 저장되었습니다"
}

# 3. 편집된 설정으로 비디오 재생성
POST /api/video/<video_id>/regenerate
Request:
{
  "config": { ... }  # 편집된 설정
}
Response:
{
  "success": true,
  "video_path": "/output/videos/xxx_edited.mp4",
  "processing_time": 45.2
}

# 4. 특정 클립 미리보기 (미래 기능)
POST /api/video/<video_id>/preview_clip
Request:
{
  "clip_id": "sentence_0",
  "settings": { ... }
}
Response:
{
  "preview_path": "/output/previews/xxx_clip0.mp4"
}
```

---

## 4. UI 설계

### 4.1 기존 페이지 (index.html) - 변경 사항
```html
<!-- 비디오 생성 완료 후 -->
<div id="result">
  <h2>✅ 비디오 생성 완료!</h2>
  <video controls src="/output/videos/xxx.mp4"></video>

  <!-- 신규 추가 -->
  <div class="actions">
    <button onclick="downloadVideo()">💾 다운로드</button>
    <button onclick="openEditor()">✏️ 편집하기</button>  <!-- 신규 -->
  </div>
</div>
```

### 4.2 신규 편집 페이지 (editor.html)
```html
<!DOCTYPE html>
<html>
<head>
  <title>비디오 편집 - Daily English Mecca</title>
  <link rel="stylesheet" href="/static/css/editor.css">
</head>
<body>
  <!-- 상단: 미리보기 -->
  <div class="preview-section">
    <h2>📹 비디오 미리보기</h2>
    <video id="preview" controls></video>
    <div class="playback-controls">
      <button id="play">▶ 재생</button>
      <button id="pause">⏸ 일시정지</button>
      <span id="timestamp">00:00 / 01:30</span>
    </div>
  </div>

  <!-- 좌측: 타임라인 -->
  <div class="timeline-section">
    <h3>📝 타임라인</h3>
    <div class="timeline">
      <div class="clip" data-type="intro">인트로 (3s)</div>
      <div class="clip active" data-type="sentence" data-index="0">문장 1 (5s)</div>
      <div class="clip" data-type="sentence" data-index="1">문장 2 (5s)</div>
      <div class="clip" data-type="sentence" data-index="2">문장 3 (5s)</div>
      <div class="clip" data-type="outro">아웃트로 (2s)</div>
    </div>
  </div>

  <!-- 우측: 편집 패널 -->
  <div class="editor-panel">
    <!-- 전역 설정 -->
    <section class="global-settings">
      <h3>⚙️ 전역 설정</h3>

      <label>🎵 배경음악</label>
      <select id="bgMusic">
        <option value="carefree.mp3" selected>Carefree (경쾌한)</option>
        <option value="scheming_weasel.mp3">Scheming Weasel (탐정)</option>
        <option value="none">없음</option>
      </select>

      <label>🔊 배경음악 볼륨</label>
      <input type="range" id="bgVolume" min="0" max="100" value="5">
      <span id="volumeValue">5%</span>

      <label>⏱️ 인트로 길이</label>
      <select id="introDuration">
        <option value="0">없음</option>
        <option value="1">1초</option>
        <option value="3" selected>3초</option>
        <option value="5">5초</option>
      </select>
    </section>

    <!-- 클립별 설정 (선택된 클립) -->
    <section class="clip-settings">
      <h3>✏️ 클립 편집 (문장 1)</h3>

      <label>📝 텍스트</label>
      <input type="text" id="sentenceText" value="Hello, how are you?">

      <label>📏 폰트 크기</label>
      <input type="range" id="fontSize" min="30" max="80" value="48">
      <span id="fontValue">48px</span>

      <label>📍 텍스트 위치</label>
      <div class="button-group">
        <button data-position="top">⬆ 상단</button>
        <button data-position="center" class="active">■ 중앙</button>
        <button data-position="bottom">⬇ 하단</button>
      </div>

      <label>🗣️ TTS 음성</label>
      <select id="ttsVoice">
        <option value="alloy" selected>Alloy (중성)</option>
        <option value="nova">Nova (여성)</option>
        <option value="shimmer">Shimmer (밝은 여성)</option>
      </select>

      <label>⏸️ 문장 후 간격</label>
      <input type="range" id="pauseAfter" min="0" max="5" step="0.5" value="2">
      <span id="pauseValue">2.0초</span>

      <label>🖼️ 이미지</label>
      <div class="image-preview">
        <img id="clipImage" src="/output/resources/images/image_0.jpg">
        <button id="changeImage">📷 이미지 변경</button>
      </div>
    </section>
  </div>

  <!-- 하단: 액션 버튼 -->
  <div class="actions">
    <button id="save" class="secondary">💾 설정 저장</button>
    <button id="regenerate" class="primary">🎬 비디오 재생성</button>
    <button id="cancel" class="tertiary">❌ 취소</button>
  </div>

  <script src="/static/js/editor.js"></script>
</body>
</html>
```

---

## 5. 구현 단계

### Phase 4.1: 기본 인프라 (1-2일)
- [x] 설계 문서 작성 ✅
- [ ] `src/editor/config_manager.py` 구현
  - JSON 설정 읽기/쓰기
  - 기본 설정 생성
- [ ] `src/editor/video_editor.py` 구현
  - 편집 설정을 VideoCreator에 적용
- [ ] 기존 `/api/generate` 수정
  - 비디오 생성 시 기본 config.json 자동 생성

### Phase 4.2: 백엔드 API (2-3일)
- [ ] `/api/video/<id>/config` (GET) 구현
- [ ] `/api/video/<id>/config` (POST) 구현
- [ ] `/api/video/<id>/regenerate` (POST) 구현
- [ ] 에러 핸들링 및 검증

### Phase 4.3: 프론트엔드 UI (3-4일)
- [ ] `editor.html` 페이지 생성
- [ ] `editor.css` 스타일링
- [ ] `editor.js` 인터랙션
  - 타임라인 클릭 → 클립 선택
  - 설정 변경 → 실시간 UI 업데이트
  - 저장/재생성 버튼 동작
- [ ] 기존 `index.html`에 [편집하기] 버튼 추가

### Phase 4.4: 통합 테스트 (1일)
- [ ] 기존 플로우 정상 작동 확인
- [ ] 편집 플로우 E2E 테스트
- [ ] 버그 수정

---

## 6. 미래 확장성

### Phase 5: 고급 편집 기능
- [ ] 타임라인 드래그 앤 드롭
- [ ] 클립 자르기/합치기
- [ ] 실시간 미리보기
- [ ] 이미지 필터/효과

### Phase 6: 플러그인 시스템
- [ ] 플러그인 아키텍처 구현
- [ ] 커스텀 효과 추가
- [ ] 템플릿 저장/불러오기

---

## 7. 기술 스택

**백엔드:**
- Python 3.13
- Flask (기존 유지)
- MoviePy 2.x (기존 유지)
- JSON (설정 저장)

**프론트엔드:**
- Vanilla JS (기존 유지, 프레임워크 없이 가볍게)
- CSS Grid/Flexbox (레이아웃)
- Fetch API (비동기 통신)

---

## 8. 성능 고려사항

### 8.1 빠른 응답
- 편집 설정 저장: 즉시 (< 100ms)
- 비디오 재생성: 기존과 동일 (3-5분)

### 8.2 캐싱
- 편집 중에는 TTS/이미지 캐시 재사용
- 변경된 클립만 재생성 (미래 최적화)

### 8.3 에러 복구
- 편집 설정 자동 저장 (5초마다)
- 재생성 실패 시 기존 비디오 보존

---

## 9. 사용자 시나리오

### 시나리오 1: 빠른 생성 (편집 없음)
```
1. 웹 접속
2. 3문장 입력
3. [생성] 클릭
4. 3분 대기
5. 완료 → 다운로드
⏱️ 총 소요 시간: 5분
```

### 시나리오 2: 편집 후 생성
```
1. 웹 접속
2. 3문장 입력
3. [생성] 클릭
4. 3분 대기
5. [편집하기] 클릭
6. 배경음악 변경, 폰트 크기 조정
7. [재생성] 클릭
8. 3분 대기
9. 완료 → 다운로드
⏱️ 총 소요 시간: 10분
```

---

## 10. 체크리스트

### 기능 요구사항
- [x] 기존 플로우 100% 보존
- [ ] 편집 설정 JSON 저장/로드
- [ ] 배경음악 선택 (3개 이상)
- [ ] 배경음악 볼륨 조절
- [ ] 텍스트 폰트 크기 조절
- [ ] 텍스트 위치 조절 (상/중/하)
- [ ] TTS 음성 선택 (alloy/nova/shimmer)
- [ ] 문장 간격 조절
- [ ] 비디오 재생성

### 비기능 요구사항
- [ ] 편집 설정 저장 < 100ms
- [ ] 비디오 재생성 시간 = 기존과 동일
- [ ] 모바일 반응형 (나중에)
- [ ] 접근성 (키보드 네비게이션)

---

**작성자:** Claude
**검토자:** Kelly
**승인일:** 2025-10-07
