# Daily English Mecca - 개발 컨텍스트 (Claude Code)

**마지막 업데이트**: 2025-10-19
**담당자**: 켈리 & Claude Code

---

## 📌 프로젝트 개요

YouTube Shorts 영어 학습 비디오 자동 생성 시스템
- 9:16 세로 포맷 (1080x1920)
- OpenAI DALL-E 3 이미지 생성 + 캐싱
- OpenAI TTS-1 음성 생성 (3가지 음성: alloy, nova, shimmer)
- GPT-4o-mini 한국어 번역 + AI 바이럴 훅 생성
- MoviePy 2.x 비디오 합성
- Flask 웹 인터페이스 + **비디오 에디터** 🆕
- 인트로/아웃트로 "Daily English Mecca" 브랜딩 (gold stroke)
- 배경 음악 (Kevin MacLeod - Pixel Peeker Polka, 경쾌한 탐정 스타일, 5% 볼륨)
- PIL 기반 이미지 회전 로직

---

## 🎯 최근 작업 (2025-10-19)

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

## 💡 개발 철학

1. **모듈화**: 각 기능은 독립적인 모듈로 개발
2. **사이드 이펙트 방지**: 새 기능 추가 시 기존 코드 영향 없도록
3. **캐싱 우선**: API 호출 최소화로 비용 절감
4. **가독성**: 명확한 변수명, 한글 주석
5. **에러 핸들링**: try-except로 안전한 실행

---

**문의사항이나 버그는 GitHub Issues에 남겨주세요!**
