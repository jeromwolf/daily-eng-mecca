# 전문 비디오 편집기 설계 문서

**프로젝트**: Daily English Mecca
**버전**: 2.0 (VREW 수준 전문 편집기)
**작성일**: 2025-10-11
**담당**: Kelly & Claude Code

---

## 📌 프로젝트 목표

현재 기본 편집기를 **VREW 수준의 전문 비디오 편집기**로 업그레이드

### 핵심 원칙
1. **사용자 경험 최우선**: 직관적이고 빠른 워크플로우
2. **웹 기반 유지**: 추후 Electron 전환 가능하도록 모듈화
3. **YouTube Shorts 특화**: 9:16 세로 포맷에 최적화
4. **AI 자동화 + 수동 미세 조정**: 빠른 생성 + 세밀한 편집

---

## 🎯 VREW 수준 필수 기능 분석

### 1. 타임라인 (Timeline)
**VREW 특징:**
- 정확한 시간축 표시 (0.1초 단위)
- 드래그앤드롭으로 클립 순서 변경
- 시간축 확대/축소 (Zoom In/Out)
- 클립 양 끝 드래그로 길이 조정
- 시간 눈금자 (Ruler)
- 재생 헤드 (Playhead) 드래그

**현재 시스템:**
- ❌ 시간축 없음 (단순 리스트)
- ❌ 드래그앤드롭 없음
- ❌ 클립 길이 조정 불가

**개선 방향:**
```
[0s]────[3s]────[10s]───[17s]───[24s]───[27s]
│ Intro │ Sent1│ Sent2 │ Sent3 │ Outro│
└───────┴──────┴───────┴───────┴──────┘
        ↑ 재생 헤드 (Playhead)
```

### 2. 멀티트랙 (Multi-track)
**VREW 특징:**
- 비디오 트랙 (Video Track)
- 오디오 트랙 (Audio Track)
  - TTS 음성
  - 배경 음악
  - 효과음 (선택사항)
- 자막 트랙 (Subtitle Track)
- 각 트랙 독립적으로 볼륨/표시 제어

**현재 시스템:**
- ❌ 단일 클립 구조 (모든 요소가 하나로 합쳐짐)
- ❌ 트랙별 편집 불가

**개선 방향:**
```
Video Track:  [────────────────────────────────]
Audio Track:  [TTS 1][TTS 2][TTS 3]
Music Track:  [════════════════════════════════]
              (배경 음악, 페이드 인/아웃)
Subtitle:     [EN + KO][EN + KO][EN + KO]
```

### 3. 실시간 미리보기 (Live Preview)
**VREW 특징:**
- 타임라인 클립 클릭 → 비디오 해당 시점 즉시 이동
- 재생 헤드 드래그 → 비디오 scrubbing
- 편집 중 실시간 반영 (텍스트 변경 → 즉시 미리보기)

**현재 시스템:**
- ✅ 비디오 미리보기 있음
- ❌ 타임라인과 동기화 약함

**개선 방향:**
- 타임라인 클립 클릭 → `video.currentTime = clipStartTime`
- 재생 헤드 드래그 → `video.currentTime` 업데이트
- Canvas 기반 실시간 렌더링 (텍스트 오버레이)

### 4. 텍스트 애니메이션 (Text Animation)
**VREW 특징:**
- Fade In/Out (페이드 인/아웃)
- Slide (슬라이드 등장)
- Typing Effect (타이핑 효과)
- Bounce (바운스)
- 애니메이션 시작/종료 시간 설정

**현재 시스템:**
- ❌ 정적 텍스트만 표시

**개선 방향:**
```javascript
{
  "text_animation": {
    "in": "fade",           // fade, slide, typing, bounce
    "out": "fade",
    "in_duration": 0.5,     // 초
    "out_duration": 0.5,
    "in_delay": 0           // 딜레이
  }
}
```

### 5. 클립 전환 효과 (Transitions)
**VREW 특징:**
- 클립 간 전환: Fade, Dissolve, Slide, Zoom
- 전환 길이 조정 (0.5초~2초)

**현재 시스템:**
- ❌ 클립 간 컷 편집만 (Hard Cut)

**개선 방향:**
```javascript
{
  "transition": {
    "type": "fade",         // fade, dissolve, slide, zoom
    "duration": 0.5         // 초
  }
}
```

### 6. 프로퍼티 패널 (Properties Panel)
**VREW 특징:**
- 선택된 클립의 상세 속성 편집
- 키프레임 편집 (위치, 크기, 투명도)
- 애니메이션 곡선 (Easing)

**현재 시스템:**
- ✅ 기본 속성 편집 (문장, 폰트, 음성)
- ❌ 키프레임 없음

**개선 방향:**
```javascript
{
  "keyframes": {
    "position_y": [
      { "time": 0, "value": 960, "easing": "ease-in" },
      { "time": 1, "value": 500, "easing": "ease-out" }
    ],
    "opacity": [
      { "time": 0, "value": 0 },
      { "time": 0.5, "value": 1 }
    ]
  }
}
```

### 7. 단축키 (Keyboard Shortcuts)
**VREW 특징:**
- `Space`: 재생/일시정지
- `Delete`: 클립 삭제
- `Ctrl+C/V`: 클립 복사/붙여넣기
- `Ctrl+Z/Y`: 실행취소/재실행
- `→/←`: 프레임 이동
- `+/-`: 타임라인 확대/축소

**현재 시스템:**
- ✅ `Ctrl+S`: 저장
- ❌ 기타 단축키 없음

---

## 🏗️ 시스템 아키텍처

### 기술 스택 선택

#### 옵션 A: Canvas 기반 (추천)
**라이브러리**: Fabric.js 또는 Konva.js

**장점:**
- 정밀한 렌더링 제어
- 키프레임 애니메이션 용이
- 드래그앤드롭 자유도 높음
- 실시간 미리보기 구현 쉬움

**단점:**
- DOM 조작보다 학습 곡선 높음
- 접근성(Accessibility) 낮음

**예시:**
```javascript
const canvas = new fabric.Canvas('timeline-canvas');
const clip = new fabric.Rect({
  left: 100,
  top: 50,
  width: 200,
  height: 60,
  fill: 'blue'
});
canvas.add(clip);
```

#### 옵션 B: HTML5 + CSS3 + JavaScript
**라이브러리**: Interact.js (드래그앤드롭)

**장점:**
- 기존 코드베이스와 통합 쉬움
- DOM 기반 접근성 좋음
- CSS 애니메이션 활용

**단점:**
- 복잡한 애니메이션 구현 어려움
- 성능 한계 (클립 많을 때)

#### 옵션 C: 비디오 편집 전문 라이브러리
**라이브러리**: Video.js + Wavesurfer.js (오디오 파형)

**장점:**
- 비디오 플레이어 기능 완벽
- 오디오 시각화 기본 제공

**단점:**
- 커스터마이징 제한적
- 번들 크기 큼

### 선택: 옵션 A (Canvas 기반 - Fabric.js)

**이유:**
1. VREW 수준의 정교한 UI 구현 가능
2. 키프레임 애니메이션 필수
3. 추후 Electron 전환 시 동일 코드 사용 가능
4. 타임라인 확대/축소 등 인터랙션 자유도 높음

---

## 📐 새 편집기 UI 구조

```
┌─────────────────────────────────────────────────────────────┐
│ [← 돌아가기]  비디오 편집 - Video ID: 20251011_153045       │
└─────────────────────────────────────────────────────────────┘

┌───────────────────┬─────────────────────────────────────────┐
│                   │                                         │
│   📹 미리보기      │         🎬 타임라인 (Timeline)           │
│                   │                                         │
│  ┌─────────────┐  │  [0s]─[3s]──[10s]─[17s]─[24s]─[27s]    │
│  │ 9:16 Video  │  │  │    │     │     │     │     │         │
│  │             │  │  └────┴─────┴─────┴─────┴─────┘         │
│  │   1080px    │  │        ↑ Playhead                       │
│  │     ×       │  │                                         │
│  │   1920px    │  │  🎞️ Video Track                         │
│  │             │  │  [──────────────────────────────]       │
│  │             │  │                                         │
│  └─────────────┘  │  🎤 Audio Track (TTS)                   │
│                   │  [───][───][───]                        │
│  [▶ 재생] [⏸]     │                                         │
│  00:15 / 00:27    │  🎵 Music Track                         │
│                   │  [════════════════════════════]         │
│  ⏱️ 타임라인 제어  │                                         │
│  [+] [-] [100%]   │  📝 Subtitle Track                      │
│                   │  [EN+KO][EN+KO][EN+KO]                  │
├───────────────────┼─────────────────────────────────────────┤
│                   │                                         │
│  📌 레이어 목록    │    ⚙️ 프로퍼티 패널 (Properties)         │
│                   │                                         │
│  [👁 Video]       │  선택된 클립: 문장 1                     │
│  [👁 TTS]         │                                         │
│  [👁 Music]       │  📝 텍스트:                              │
│  [👁 Subtitle]    │  ┌─────────────────────────────┐        │
│                   │  │ The weather is nice today. │        │
│  [+ 트랙 추가]     │  └─────────────────────────────┘        │
│                   │                                         │
│                   │  🎨 애니메이션:                          │
│                   │  In: [Fade ▼] 0.5s                      │
│                   │  Out: [Fade ▼] 0.5s                     │
│                   │                                         │
│                   │  📏 위치 & 크기:                         │
│                   │  X: [540] Y: [960]                      │
│                   │  폰트: [48px]                            │
│                   │                                         │
│                   │  🔑 키프레임:                            │
│                   │  [위치] [크기] [투명도]                  │
│                   │  ┌─────────────────────────┐            │
│                   │  │   ●─────────●──────●   │            │
│                   │  └─────────────────────────┘            │
└───────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ [❌ 취소]  [💾 저장 (Ctrl+S)]  [🎬 비디오 재생성 (Ctrl+R)] │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 구현 단계별 계획

### Phase 1: 타임라인 기초 구조 (1주)
**목표**: Canvas 기반 타임라인 구현

**작업:**
1. Fabric.js 설치 및 초기 설정
2. 시간축 렌더링 (0초~비디오 길이)
3. 클립 블록 렌더링 (Rect 객체)
4. 재생 헤드 (Playhead) 구현
5. 클립 클릭 이벤트 핸들러

**코드 예시:**
```javascript
// src/editor/timeline.js
class Timeline {
  constructor(canvasId, duration) {
    this.canvas = new fabric.Canvas(canvasId);
    this.duration = duration;
    this.scale = 100; // 100px per second
    this.renderRuler();
    this.renderClips();
  }

  renderRuler() {
    for (let i = 0; i <= this.duration; i++) {
      const line = new fabric.Line([i * this.scale, 0, i * this.scale, 20], {
        stroke: '#ccc'
      });
      this.canvas.add(line);

      const text = new fabric.Text(`${i}s`, {
        left: i * this.scale,
        top: 25,
        fontSize: 12
      });
      this.canvas.add(text);
    }
  }

  renderClip(clip, index) {
    const rect = new fabric.Rect({
      left: clip.start * this.scale,
      top: 60,
      width: clip.duration * this.scale,
      height: 50,
      fill: '#6366f1',
      stroke: '#4f46e5',
      strokeWidth: 2,
      rx: 5,
      ry: 5
    });

    rect.clipData = clip;
    rect.on('selected', () => this.onClipSelected(clip));

    this.canvas.add(rect);
  }
}
```

**테스트:**
- [ ] 타임라인 렌더링 확인
- [ ] 클립 클릭 시 선택 이벤트 발생

---

### Phase 2: 드래그앤드롭 (1주)
**목표**: 클립 순서 변경 및 길이 조정

**작업:**
1. 클립 드래그 이벤트 핸들러
2. 드롭 시 순서 재정렬
3. 클립 양 끝 핸들 (Resize Handle)
4. 스냅 (Snap) 기능 (다른 클립에 맞춤)

**코드 예시:**
```javascript
rect.on('moving', (e) => {
  const target = e.target;
  const newTime = target.left / this.scale;

  // 스냅 (0.5초 단위)
  const snappedTime = Math.round(newTime * 2) / 2;
  target.left = snappedTime * this.scale;

  this.updateClipData(target, snappedTime);
});
```

**테스트:**
- [ ] 클립 드래그 가능
- [ ] 순서 변경 후 config 업데이트
- [ ] 클립 길이 조정 가능

---

### Phase 3: 멀티트랙 시스템 (1.5주)
**목표**: 비디오/오디오/자막 트랙 분리

**작업:**
1. 트랙 구조 설계
2. 각 트랙별 클립 렌더링
3. 트랙 높이 조정
4. 트랙 뮤트/솔로 버튼

**데이터 구조:**
```javascript
{
  "tracks": {
    "video": {
      "name": "Video",
      "height": 80,
      "clips": [
        { "type": "intro", "start": 0, "duration": 3 },
        { "type": "sentence", "start": 3, "duration": 7 }
      ]
    },
    "tts": {
      "name": "TTS Audio",
      "height": 60,
      "clips": [
        { "file": "sentence_1.mp3", "start": 3, "duration": 3 },
        { "file": "sentence_1.mp3", "start": 6, "duration": 3 }
      ]
    },
    "music": {
      "name": "Background Music",
      "height": 40,
      "clips": [
        { "file": "background.mp3", "start": 0, "duration": 27, "volume": 0.15 }
      ]
    },
    "subtitle": {
      "name": "Subtitles",
      "height": 40,
      "clips": [
        { "text": "The weather...", "start": 3, "duration": 7 }
      ]
    }
  }
}
```

**테스트:**
- [ ] 4개 트랙 렌더링 확인
- [ ] 각 트랙별 클립 독립 편집

---

### Phase 4: 실시간 미리보기 동기화 (1주)
**목표**: 타임라인과 비디오 미리보기 완벽 동기화

**작업:**
1. 타임라인 클립 클릭 → `video.currentTime` 이동
2. 재생 헤드 드래그 → 비디오 scrubbing
3. 비디오 재생 중 → 재생 헤드 이동
4. Canvas 기반 실시간 오버레이 (텍스트)

**코드 예시:**
```javascript
// 클립 클릭 시 비디오 이동
rect.on('selected', () => {
  const video = document.getElementById('preview-video');
  video.currentTime = clip.start;
});

// 비디오 재생 중 재생 헤드 업데이트
video.addEventListener('timeupdate', () => {
  const currentTime = video.currentTime;
  playhead.left = currentTime * timeline.scale;
  timeline.canvas.renderAll();
});
```

**테스트:**
- [ ] 클립 클릭 시 비디오 이동
- [ ] 재생 중 타임라인 동기화

---

### Phase 5: 텍스트 애니메이션 (1.5주)
**목표**: Fade, Slide, Typing 애니메이션 구현

**작업:**
1. 애니메이션 프리셋 정의
2. Canvas 기반 렌더링 (requestAnimationFrame)
3. 프로퍼티 패널에서 애니메이션 선택
4. 애니메이션 시작/종료 시간 설정

**애니메이션 프리셋:**
```javascript
const animations = {
  fade: {
    in: (progress) => ({ opacity: progress }),
    out: (progress) => ({ opacity: 1 - progress })
  },
  slide: {
    in: (progress) => ({
      opacity: progress,
      translateY: (1 - progress) * 100
    }),
    out: (progress) => ({
      opacity: 1 - progress,
      translateY: progress * 100
    })
  },
  typing: {
    in: (progress, text) => ({
      text: text.substring(0, Math.floor(text.length * progress))
    })
  }
};
```

**테스트:**
- [ ] Fade 애니메이션 작동
- [ ] Slide 애니메이션 작동
- [ ] Typing 애니메이션 작동

---

### Phase 6: 클립 전환 효과 (1주)
**목표**: Fade, Dissolve 전환 구현

**작업:**
1. 클립 간 오버랩 영역 계산
2. 전환 효과 렌더링
3. 전환 길이 조정 UI

**코드 예시:**
```javascript
if (clip1.end > clip2.start) {
  const overlapDuration = clip1.end - clip2.start;
  const transitionType = clip1.transition || 'fade';

  // Fade 전환
  for (let t = 0; t < overlapDuration; t += 0.033) {
    const progress = t / overlapDuration;
    renderFrame(clip1, 1 - progress); // 페이드 아웃
    renderFrame(clip2, progress);     // 페이드 인
  }
}
```

**테스트:**
- [ ] Fade 전환 작동
- [ ] Dissolve 전환 작동

---

### Phase 7: 키프레임 시스템 (2주)
**목표**: 위치, 크기, 투명도 키프레임 편집

**작업:**
1. 키프레임 데이터 구조
2. 키프레임 에디터 UI (그래프)
3. Easing 함수 (ease-in, ease-out, linear)
4. 키프레임 보간 (Interpolation)

**데이터 구조:**
```javascript
{
  "keyframes": {
    "position": {
      "y": [
        { "time": 0, "value": 960, "easing": "ease-in" },
        { "time": 1, "value": 500, "easing": "ease-out" },
        { "time": 2, "value": 500, "easing": "linear" }
      ]
    },
    "opacity": [
      { "time": 0, "value": 0 },
      { "time": 0.5, "value": 1 },
      { "time": 6.5, "value": 1 },
      { "time": 7, "value": 0 }
    ]
  }
}
```

**Easing 함수:**
```javascript
const easings = {
  linear: t => t,
  easeIn: t => t * t,
  easeOut: t => t * (2 - t),
  easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
};

function interpolate(keyframes, currentTime) {
  const prev = findPrevKeyframe(keyframes, currentTime);
  const next = findNextKeyframe(keyframes, currentTime);

  const progress = (currentTime - prev.time) / (next.time - prev.time);
  const easedProgress = easings[prev.easing](progress);

  return prev.value + (next.value - prev.value) * easedProgress;
}
```

**테스트:**
- [ ] 키프레임 추가/삭제
- [ ] 애니메이션 보간 확인
- [ ] Easing 함수 작동

---

### Phase 8: 단축키 시스템 확장 (0.5주)
**목표**: VREW 수준 단축키 지원

**작업:**
1. 단축키 맵 정의
2. 실행취소/재실행 스택
3. 클립 복사/붙여넣기

**단축키 맵:**
```javascript
const shortcuts = {
  'Space': togglePlayPause,
  'Delete': deleteSelectedClip,
  'Ctrl+C': copyClip,
  'Ctrl+V': pasteClip,
  'Ctrl+Z': undo,
  'Ctrl+Y': redo,
  'Ctrl+S': save,
  'Ctrl+R': regenerateVideo,
  'ArrowLeft': () => seekVideo(-0.033),  // 1 프레임 뒤로
  'ArrowRight': () => seekVideo(0.033),  // 1 프레임 앞으로
  '+': () => zoomTimeline(1.2),
  '-': () => zoomTimeline(0.8)
};

document.addEventListener('keydown', (e) => {
  const key = e.ctrlKey ? `Ctrl+${e.key}` : e.key;
  if (shortcuts[key]) {
    e.preventDefault();
    shortcuts[key]();
  }
});
```

**테스트:**
- [ ] Space: 재생/일시정지
- [ ] Delete: 클립 삭제
- [ ] Ctrl+Z/Y: 실행취소/재실행
- [ ] +/-: 타임라인 확대/축소

---

## 📊 진행 상황 추적

| Phase | 작업 | 예상 시간 | 상태 |
|-------|------|----------|------|
| 1 | 타임라인 기초 구조 | 1주 | 대기 중 |
| 2 | 드래그앤드롭 | 1주 | 대기 중 |
| 3 | 멀티트랙 시스템 | 1.5주 | 대기 중 |
| 4 | 실시간 미리보기 동기화 | 1주 | 대기 중 |
| 5 | 텍스트 애니메이션 | 1.5주 | 대기 중 |
| 6 | 클립 전환 효과 | 1주 | 대기 중 |
| 7 | 키프레임 시스템 | 2주 | 대기 중 |
| 8 | 단축키 시스템 확장 | 0.5주 | 대기 중 |

**총 예상 시간**: 9.5주 (약 2.5개월)

---

## 🔧 기술 스택 정리

### 프론트엔드
- **타임라인 렌더링**: Fabric.js (Canvas)
- **드래그앤드롭**: Fabric.js 내장 기능
- **오디오 파형**: Wavesurfer.js (선택사항)
- **애니메이션**: requestAnimationFrame + Easing Functions
- **상태 관리**: Vanilla JS (추후 Redux 고려)

### 백엔드
- **Flask**: 기존 유지
- **비디오 재생성**: MoviePy 2.x (기존 유지)
- **API**: RESTful JSON

### 라이브러리 설치
```bash
cd web/static
npm init -y
npm install fabric
npm install wavesurfer.js  # 선택사항
```

---

## 🎨 UI/UX 개선 포인트

### 1. 반응형 레이아웃
- 데스크탑: 3칼럼 (미리보기 | 타임라인 | 프로퍼티)
- 태블릿: 2칼럼 (타임라인+프로퍼티 | 미리보기)
- 모바일: 1칼럼 (읽기 전용 모드)

### 2. 다크 모드
- VREW처럼 다크 테마 기본
- 배경: `#1e1e1e`
- 타임라인: `#252525`
- 클립: `#3a3a3a`

### 3. 색상 체계
```css
:root {
  --timeline-bg: #252525;
  --clip-video: #6366f1;      /* 인디고 */
  --clip-audio: #10b981;      /* 초록 */
  --clip-music: #f59e0b;      /* 주황 */
  --clip-subtitle: #8b5cf6;   /* 보라 */
  --playhead: #ef4444;        /* 빨강 */
}
```

### 4. 접근성
- 키보드 내비게이션 지원
- ARIA 라벨 추가
- 고대비 모드 지원

---

## 🐛 예상 문제 및 해결 방안

### 문제 1: Canvas 성능 저하 (클립 많을 때)
**해결:**
- Virtual Scrolling (보이는 영역만 렌더링)
- 클립 수 제한 (최대 50개)
- 디바운싱 (Debouncing)

### 문제 2: 실시간 미리보기 동기화 지연
**해결:**
- Web Workers로 계산 오프로드
- requestAnimationFrame 최적화
- 미리보기 해상도 다운스케일 (540x960)

### 문제 3: 브라우저 호환성 (Safari)
**해결:**
- Polyfill 추가 (ES6+ 기능)
- CSS Grid Fallback
- `-webkit-` prefix 추가

---

## 🚢 배포 전략

### Phase 1-3 완료 후: 베타 테스트
- 내부 테스트 (Kelly)
- 기본 편집 기능 검증

### Phase 4-6 완료 후: 알파 출시
- 일부 사용자 공개
- 피드백 수집

### Phase 7-8 완료 후: 정식 출시
- 전체 사용자 공개
- YouTube 링크 공유

---

## 📚 참고 자료

### VREW 경쟁 제품 분석
1. **CapCut**: TikTok 소유, AI 자막 자동 생성
2. **Adobe Premiere Rush**: 모바일+데스크탑 하이브리드
3. **DaVinci Resolve**: 전문가급, 무료

### 비디오 편집 라이브러리 비교
| 라이브러리 | 장점 | 단점 | 추천도 |
|-----------|------|------|--------|
| Fabric.js | Canvas 제어 용이 | 학습 곡선 | ⭐⭐⭐⭐⭐ |
| Konva.js | 성능 우수 | 문서 부족 | ⭐⭐⭐⭐ |
| Video.js | 플레이어 완벽 | 편집 기능 약함 | ⭐⭐⭐ |

---

## 💡 추가 아이디어 (Backlog)

### 고급 기능 (Phase 9+)
- [ ] 멀티 선택 (Shift+클릭)
- [ ] 그룹화 (Ctrl+G)
- [ ] 템플릿 저장 (자주 쓰는 설정)
- [ ] AI 자동 편집 제안
- [ ] 오디오 파형 시각화
- [ ] 색상 그레이딩
- [ ] 크로마 키 (Green Screen)
- [ ] 3D 텍스트
- [ ] 파티클 효과

### 협업 기능
- [ ] 프로젝트 공유 (링크)
- [ ] 실시간 공동 편집
- [ ] 댓글 시스템

### 분석 기능
- [ ] 편집 시간 통계
- [ ] 재생 횟수 추적
- [ ] A/B 테스트

---

## ✅ 다음 단계

1. **켈리 검토 및 승인**
   - 이 문서 검토
   - 우선순위 조정
   - Phase 1 시작 승인

2. **Phase 1 시작 준비**
   - Fabric.js 설치
   - 새 파일 구조 생성
     - `web/static/js/editor/timeline.js`
     - `web/static/js/editor/tracks.js`
     - `web/static/js/editor/playhead.js`

3. **개발 환경 설정**
   - npm 프로젝트 초기화
   - 빌드 도구 설정 (Webpack or Rollup)

---

**문의사항이나 제안은 Issues에 남겨주세요!**

**마지막 업데이트**: 2025-10-11
