# VREW 실제 화면 분석 보고서

**작성일**: 2025-10-11
**분석 대상**: VREW 3.2.5 (스크린샷 8장)
**목적**: Daily English Mecca 편집기 개선을 위한 벤치마킹

---

## 🔍 핵심 발견: VREW는 "타임라인 중심"이 아니라 "문장 리스트 중심"!

### 놀라운 발견
기존 설계 문서에서 **타임라인(Timeline)을 핵심 기능**으로 생각했지만,
VREW는 **"문장 리스트(Sentence List)"를 중심**으로 설계되어 있습니다.

**이유:**
- YouTube Shorts/TikTok 같은 짧은 영상에서는 복잡한 타임라인보다 **문장 단위 편집**이 더 직관적
- 영어 학습 비디오는 문장 중심 콘텐츠 → 문장별 편집이 자연스러움
- 타임라인은 하단에 **간략하게** 표시 (클립 레벨만)

---

## 📐 VREW 레이아웃 분석

### 화면 구성 (3칼럼)

```
┌────────────────────────────────────────────────────────────────┐
│ [파일] [편집] [효과] [자막] [AI 복사리] [효과별] [프로] [도움말] │ ← 메뉴바
├───────────────┬──────────────────────────────────┬─────────────┤
│               │                                  │             │
│  📹 미리보기   │         우측 패널                │  우측 사이드 │
│               │    (문장 리스트 또는 설정)         │    바       │
│  ┌─────────┐  │                                  │             │
│  │         │  │  1. [🔊 태호 ☰] 안녕하십니까...  │  [내보내기]  │
│  │ 9:16    │  │     [이미지] 안녕하십니까, 시청자 │             │
│  │ Video   │  │     00:00 ~ 2.61초              │  개요        │
│  │         │  │                                  │  상세        │
│  │1080x1920│  │  2. [🔊 태호 ☰] 오늘 환율 소식을  │             │
│  │         │  │     [이미지] 오늘 환율 소식을...  │             │
│  └─────────┘  │     00:02 ~ 3.53초              │             │
│               │                                  │             │
│  [▶ 재생]      │  3. [🔊 태호 ☰] 현재 환율은...   │             │
│  00:02 / 01:42│     [이미지] 현재 환율은 경제...  │             │
│  [1x] [⚙]     │     00:06 ~ 3.74초              │             │
│               │                                  │             │
├───────────────┼──────────────────────────────────┴─────────────┤
│ 클립1         │                                                │
│ [비디오]      │  (하단 공간 - 선택된 에셋 등)                   │
└───────────────┴────────────────────────────────────────────────┘
```

### 주요 섹션

1. **좌측 패널 (미리보기)**
   - 비디오 미리보기 (세로 포맷)
   - 재생 컨트롤 (재생/일시정지)
   - 타임스탬프 (00:02 / 01:42)
   - 재생 속도 (1x)
   - 설정 버튼

2. **중앙 패널 (문장 리스트)** ⭐ **핵심 영역**
   - 문장별 카드 형식
   - 각 문장마다:
     - 번호
     - 음성 아이콘 (🔊)
     - 화자 이름 (태호)
     - 메뉴 버튼 (☰)
     - 썸네일 이미지
     - 전체 텍스트 표시
     - 시간 범위 (00:00 ~ 2.61초)
     - 편집 버튼 ([.] 아이콘)
   - 스크롤 가능

3. **우측 사이드바**
   - [내보내기] 버튼 (파란색, 눈에 띄게)
   - 탭: [개요] [상세]
   - 알림 아이콘

4. **하단 패널 (클립 타임라인)**
   - 간략한 클립 목록
   - "클립1 [비디오]" 형태
   - 선택된 에셋 정보

---

## 🎨 UI/UX 특징

### 1. 문장 카드 디자인
```
┌──────────────────────────────────────────────────────────────┐
│ 1   🔊 태호  ☰        안녕하십니까,  시청자  여러분  [.]  🎤  │
├──────────────────────────────────────────────────────────────┤
│ [썸네일 이미지]                                               │
│                                                              │
│ 📄 안녕하십니까, 시청자 여러분                                │
│                                                              │
│ 00:00 ~ 2.61초                                              │
└──────────────────────────────────────────────────────────────┘
```

**요소:**
- 좌측 상단: 번호 (1, 2, 3...)
- 음성 아이콘 (🔊)
- 화자 선택 드롭다운
- 메뉴 버튼 (☰) → 우클릭 메뉴
- 텍스트 단어별 표시 (클릭 가능)
- 편집 버튼 ([.])
- 음성 녹음 버튼 (🎤)
- 썸네일 이미지 (가로 비율)
- 전체 텍스트
- 시간 범위

### 2. 우클릭 컨텍스트 메뉴
```
📹 재우기              >
🔄 교체
( ) 비디오 시작점 변경
🔊 볼륨 조절          >
📏 적용 범위 변경      >
🎬 새 클립으로 변경
🗑️ 삭제
```

**기능:**
- 재우기: 이미지를 화면에 맞게 크롭
- 교체: 다른 이미지/비디오로 교체
- 시작점 변경: 비디오 시작 시점 조정
- 볼륨 조절: 오디오 볼륨
- 적용 범위 변경: 클립 길이 조정
- 새 클립으로 변경: 분리
- 삭제

### 3. AI 이미지 생성 모달
```
┌──────────────────────────────────────────────────────────────┐
│ 다른 이미지 또는 비디오로 교체하기                 [X]         │
├──────────────────────────────────────────────────────────────┤
│ [이미지] [비디오 ⭐]                                          │
│                                                              │
│ 이미지 문자                                                   │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ 안녕하십니까, 시청자 여러분                              │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ 모델        [Basic ▼]                                        │
│                                                              │
│ 고화질 ⭐   [토글]                                           │
│ (+1 크레딧/장)                                               │
│                                                              │
│ 스타일      [사진 >]                                         │
│                                                              │
│ 이미지 비율  기로 (4:3)                                       │
│ [_] [_] [_] [_]                                             │
│                                                              │
│ 💳 1 크레딧 사용 (나의 크레딧: 4,980)                        │
│                                                              │
│ [✨ 이미지 1장 생성]                    [▼]                  │
└──────────────────────────────────────────────────────────────┘
```

**특징:**
- 탭: [이미지] [비디오 ⭐ 프리미엄]
- 이미지 프롬프트 자동 추출 (문장 텍스트)
- 모델 선택: Basic, Pro 등
- 고화질 옵션 (추가 크레딧)
- 스타일 선택 (사진, 일러스트 등)
- 비율 선택 (4:3, 16:9, 1:1, 9:16)
- 크레딧 시스템 (1장당 1크레딧)
- 생성 버튼 (파란색, 강조)

### 4. 이미지 미리보기 및 편집
```
┌──────────────────────────────────────────────────────────────┐
│ 다른 이미지 또는 비디오로 교체하기                 [X]         │
├──────────────────────────────────────────────────────────────┤
│ [이미지] [비디오 ⭐]                 [PC에서 불러오기]         │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                        │   │
│ │              [생성된 이미지 표시]                       │   │
│ │          (뉴스 앵커 여성 이미지)                        │   │
│ │                                                        │   │
│ │         [+ 내 이미지 · 비디오에 추가]                   │   │
│ │         [🌐 타운로드]                                  │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ [🤖 AI와 이미지 수정하기]  [삽입하기]                        │
│                                                              │
│ 내 이미지 · 비디오                                           │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ [PC에서 불러오기]                                       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ 무료 이미지 · 비디오                                         │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ [이미지1] [이미지2] [이미지3]                           │   │
│ │ [이미지4] [이미지5] [이미지6]                           │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**특징:**
- 생성된 이미지 큰 미리보기
- "+ 내 이미지 · 비디오에 추가" (라이브러리 저장)
- "AI와 이미지 수정하기" (추가 편집)
- "삽입하기" (비디오에 적용)
- 내 이미지 라이브러리
- 무료 이미지 갤러리

### 5. 텍스트 편집 인터페이스
```
┌──────────────────────────────────────────────────────────────┐
│ 좌측: 미리보기                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                        │   │
│ │    [텍스트 오버레이]                                    │   │
│ │    "환율 폭등? 당신의 돈은 안전할까!"                   │   │
│ │                                                        │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ 하단: 텍스트 편집 툴바                                        │
│ [B] [I] [Pretendard ▼] [🔍 200] [◀ ▶ ▣] [🎨] [📐] [=]      │
│                                                              │
│ 우측: AI 배경 이미지                                          │
│ [✨ AI 배경 추천 설정하기]                                    │
│                                                              │
│ 내 배경 이미지                                                │
│ [이미지1] [이미지2]                                          │
│                                                              │
│ 무료 배경 이미지                                              │
│ [이미지3] [이미지4] [이미지5]                                │
│ [이미지6] [이미지7] [이미지8]                                │
└──────────────────────────────────────────────────────────────┘
```

**텍스트 툴바 기능:**
- **B**: 굵게
- **I**: 기울임
- **Pretendard**: 폰트 선택
- **200**: 폰트 크기
- **◀ ▶ ▣**: 정렬 (좌/중앙/우)
- **🎨**: 색상
- **📐**: 외곽선/그림자
- **=**: 줄 간격

---

## 🆚 기존 설계 vs VREW 실제

| 항목 | 기존 설계 (Canvas 타임라인) | VREW 실제 (문장 리스트) |
|------|----------------------------|------------------------|
| **핵심 UI** | 타임라인 (시간축 기반) | 문장 리스트 (카드 형식) |
| **편집 단위** | 클립 (Clip) | 문장 (Sentence) |
| **시간 표시** | 정밀한 시간축 (0.1초) | 간략한 시간 범위 (00:00 ~ 2.61초) |
| **드래그앤드롭** | 클립을 타임라인에서 이동 | 문장 카드 순서 변경 |
| **멀티트랙** | 비디오/오디오/자막 분리 | 문장 카드 내 통합 |
| **이미지 생성** | 별도 모듈 | 문장 카드에서 직접 생성 |
| **복잡도** | 높음 (전문가용) | 낮음 (초보자 친화적) |

---

## 💡 Daily English Mecca 적용 제안

### 옵션 A: VREW 방식 채택 (추천) ⭐

**이유:**
1. **영어 학습 콘텐츠는 문장 중심**
   - 사용자가 "3개 문장"을 생성
   - 문장별 편집이 직관적

2. **초보자 친화적**
   - 타임라인보다 이해하기 쉬움
   - 카드 형식이 시각적으로 명확

3. **개발 난이도 낮음**
   - Canvas 기반 타임라인보다 구현 쉬움
   - HTML/CSS로 충분히 구현 가능

4. **웹 기반 최적화**
   - 반응형 레이아웃 구현 용이
   - 모바일 지원 쉬움

**구현 방향:**
```
┌────────────────────────────────────────────────────────────────┐
│ [← 돌아가기]  비디오 편집 - Daily English Mecca                │
├───────────────┬──────────────────────────────────┬─────────────┤
│               │                                  │             │
│  📹 미리보기   │    📝 문장 리스트                │  [내보내기]  │
│               │                                  │             │
│  ┌─────────┐  │  ┌────────────────────────────┐  │             │
│  │ 9:16    │  │  │ 1. Intro (3초)            │  │             │
│  │ Video   │  │  │ [이미지] Daily English... │  │             │
│  │1080×1920│  │  └────────────────────────────┘  │             │
│  │         │  │                                  │             │
│  └─────────┘  │  ┌────────────────────────────┐  │             │
│               │  │ 2. [🔊 Alloy ▼]          │  │             │
│  [▶] [⏸]     │  │ The weather is nice...    │  │             │
│  00:00 / 00:27│  │ [이미지] 햇살 밝은 공원    │  │             │
│               │  │ 오늘 날씨 정말 좋네요      │  │             │
│               │  │ 00:03 ~ 10초             │  │             │
│               │  │ [편집 ✏️] [AI 이미지 생성]│  │             │
│               │  └────────────────────────────┘  │             │
│               │                                  │             │
│               │  ┌────────────────────────────┐  │             │
│               │  │ 3. [🔊 Nova ▼]           │  │             │
│               │  │ I love studying English.  │  │             │
│               │  │ [이미지] 공부하는 학생     │  │             │
│               │  │ 영어 공부가 너무 좋아요    │  │             │
│               │  │ 00:10 ~ 17초             │  │             │
│               │  │ [편집 ✏️] [AI 이미지 생성]│  │             │
│               │  └────────────────────────────┘  │             │
│               │                                  │             │
│               │  ... (더 많은 문장)              │             │
│               │                                  │             │
│               │  ┌────────────────────────────┐  │             │
│               │  │ Outro (2초)               │  │             │
│               │  │ [이미지] 좋아요 & 구독    │  │             │
│               │  └────────────────────────────┘  │             │
├───────────────┴──────────────────────────────────┴─────────────┤
│ 🎵 배경음악: Pixel Peeker Polka [15%]   [재생성]              │
└────────────────────────────────────────────────────────────────┘
```

### 문장 카드 상세 설계
```html
<!-- 문장 카드 컴포넌트 -->
<div class="sentence-card" data-index="1">
  <div class="card-header">
    <span class="sentence-number">2</span>
    <select class="voice-select">
      <option value="alloy">🔊 Alloy</option>
      <option value="nova">🔊 Nova</option>
      <option value="shimmer">🔊 Shimmer</option>
    </select>
    <button class="menu-btn">☰</button>
  </div>

  <div class="card-body">
    <!-- 영어 문장 (단어별 표시) -->
    <div class="sentence-text">
      <span class="word">The</span>
      <span class="word">weather</span>
      <span class="word">is</span>
      <span class="word">nice</span>
      <span class="word">today.</span>
      <button class="edit-text-btn">✏️</button>
    </div>

    <!-- 썸네일 이미지 -->
    <div class="thumbnail">
      <img src="image.png" alt="햇살 밝은 공원">
      <button class="generate-image-btn">✨ AI 이미지 생성</button>
    </div>

    <!-- 한글 번역 -->
    <div class="translation">
      <span class="icon">📄</span>
      <span class="text">오늘 날씨 정말 좋네요</span>
    </div>

    <!-- 시간 범위 -->
    <div class="time-range">
      <span class="start-time">00:03</span>
      <span class="separator">~</span>
      <span class="duration">10초</span>
    </div>
  </div>

  <div class="card-footer">
    <button class="btn-secondary">편집 ✏️</button>
    <button class="btn-primary">AI 이미지 생성</button>
  </div>
</div>
```

### CSS 스타일
```css
.sentence-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.sentence-card:hover {
  border-color: #6366f1;
}

.sentence-card.active {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.sentence-number {
  width: 28px;
  height: 28px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.voice-select {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.sentence-text {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.sentence-text .word {
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.sentence-text .word:hover {
  background: #e5e7eb;
}

.thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #f9fafb;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.generate-image-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  padding: 8px 16px;
  background: rgba(99, 102, 241, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  backdrop-filter: blur(8px);
}

.translation {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.time-range {
  font-size: 13px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
```

---

### 옵션 B: 하이브리드 (타임라인 + 문장 리스트)

**구조:**
- 상단: 간략한 타임라인 (Canvas 기반)
- 중앙: 문장 리스트 (VREW 방식)

**장점:**
- 타임라인으로 전체 구조 파악
- 문장 리스트로 상세 편집

**단점:**
- UI 복잡도 증가
- 개발 시간 2배

---

## 📊 우선순위 재조정

### Phase 1 (1주): 문장 리스트 UI ⭐ **최우선**
- [ ] 문장 카드 컴포넌트 (HTML/CSS)
- [ ] 문장별 데이터 로드
- [ ] 카드 클릭 → 비디오 seek
- [ ] 스크롤 동기화

### Phase 2 (1주): AI 이미지 생성 통합
- [ ] "AI 이미지 생성" 버튼
- [ ] 모달 UI (프롬프트 입력)
- [ ] DALL-E API 호출
- [ ] 이미지 미리보기 및 삽입

### Phase 3 (1주): 문장 편집 기능
- [ ] 텍스트 편집 (인라인)
- [ ] 번역 편집
- [ ] 음성 선택 (Alloy/Nova/Shimmer)
- [ ] 설정 저장

### Phase 4 (1주): 우클릭 메뉴
- [ ] 컨텍스트 메뉴 구현
- [ ] 재우기 (이미지 크롭)
- [ ] 교체 (이미지 변경)
- [ ] 삭제

### Phase 5 (0.5주): 배경음악 컨트롤
- [ ] 하단 배경음악 컨트롤바
- [ ] 볼륨 슬라이더
- [ ] 음악 선택

### Phase 6 (0.5주): 내보내기
- [ ] [내보내기] 버튼 (우측 상단)
- [ ] 비디오 재생성 진행 표시
- [ ] 다운로드 링크

**총 예상 시간**: 5주 (1.25개월)

---

## 🎯 핵심 기능 비교

| 기능 | VREW | 현재 시스템 | 새 설계 (문장 리스트) |
|------|------|------------|---------------------|
| **문장별 편집** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AI 이미지 생성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (별도) | ⭐⭐⭐⭐⭐ (통합) |
| **타임라인** | ⭐⭐ (간략) | ⭐⭐ (리스트) | ⭐⭐ (간략) |
| **텍스트 편집** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **음성 선택** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **우클릭 메뉴** | ⭐⭐⭐⭐⭐ | ⭐ (없음) | ⭐⭐⭐⭐ |
| **배경음악** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 즉시 실행 가능한 개선 사항

### 1. 현재 편집기 → 문장 리스트 변환

**기존 코드 (editor.html:45-61):**
```html
<aside class="timeline-section">
  <h3>📝 타임라인</h3>
  <div id="timeline" class="timeline">
    <!-- 인트로 -->
    <div class="clip intro-clip" data-type="intro" data-index="-1">
      <span class="clip-label">인트로</span>
      <span class="clip-duration">3s</span>
    </div>

    <!-- 문장 클립들 (JavaScript로 동적 생성) -->
    <div id="sentence-clips-container"></div>

    <!-- 아웃트로 -->
    <div class="clip outro-clip" data-type="outro" data-index="-2">
      <span class="clip-label">아웃트로</span>
      <span class="clip-duration">2s</span>
    </div>
  </div>
</aside>
```

**새 코드 (VREW 스타일 문장 리스트):**
```html
<section class="sentence-list-section">
  <h3>📝 문장 리스트</h3>
  <div id="sentence-list" class="sentence-list">
    <!-- 인트로 -->
    <div class="sentence-card intro-card">
      <div class="card-header">
        <span class="sentence-number">🎬</span>
        <span class="card-title">Intro</span>
      </div>
      <div class="card-body">
        <div class="thumbnail">
          <img src="/path/to/intro-bg.png" alt="Intro">
        </div>
        <div class="time-range">00:00 ~ 3초</div>
      </div>
    </div>

    <!-- 문장 카드들 (JavaScript로 동적 생성) -->
    <div id="sentence-cards-container"></div>

    <!-- 아웃트로 -->
    <div class="sentence-card outro-card">
      <div class="card-header">
        <span class="sentence-number">🎭</span>
        <span class="card-title">Outro</span>
      </div>
      <div class="card-body">
        <div class="thumbnail">
          <img src="/path/to/outro-bg.png" alt="Outro">
        </div>
        <div class="time-range">00:25 ~ 27초</div>
      </div>
    </div>
  </div>
</section>
```

### 2. JavaScript 수정 (editor.js)

**기존 코드:**
```javascript
function createTimelineClips() {
  const container = document.getElementById('sentence-clips-container');
  container.innerHTML = '';

  config.clips.forEach((clip, index) => {
    const clipElement = document.createElement('div');
    clipElement.className = 'clip sentence-clip';
    clipElement.dataset.type = 'sentence';
    clipElement.dataset.index = index;

    const estimatedDuration = (clip.audio.repeat_count * 3) + clip.audio.pause_after;

    clipElement.innerHTML = `
      <span class="clip-label">문장 ${index + 1}</span>
      <span class="clip-duration">~${estimatedDuration.toFixed(0)}s</span>
    `;

    clipElement.addEventListener('click', () => selectClip(index));
    container.appendChild(clipElement);
  });
}
```

**새 코드 (VREW 스타일):**
```javascript
function createSentenceCards() {
  const container = document.getElementById('sentence-cards-container');
  container.innerHTML = '';

  config.clips.forEach((clip, index) => {
    const cardElement = document.createElement('div');
    cardElement.className = 'sentence-card';
    cardElement.dataset.index = index;

    // 예상 클립 길이 계산
    const estimatedDuration = (clip.audio.repeat_count * 3) + clip.audio.pause_after;
    const startTime = calculateStartTime(index); // 이전 클립 길이 누적
    const endTime = startTime + estimatedDuration;

    cardElement.innerHTML = `
      <div class="card-header">
        <span class="sentence-number">${index + 1}</span>
        <select class="voice-select" data-index="${index}">
          <option value="alloy" ${clip.audio.tts_voices[0] === 'alloy' ? 'selected' : ''}>🔊 Alloy</option>
          <option value="nova" ${clip.audio.tts_voices[0] === 'nova' ? 'selected' : ''}>🔊 Nova</option>
          <option value="shimmer" ${clip.audio.tts_voices[0] === 'shimmer' ? 'selected' : ''}>🔊 Shimmer</option>
        </select>
        <button class="menu-btn" data-index="${index}">☰</button>
      </div>

      <div class="card-body">
        <div class="sentence-text">
          ${clip.sentence_text.split(' ').map(word =>
            `<span class="word">${word}</span>`
          ).join('')}
          <button class="edit-text-btn" data-index="${index}">✏️</button>
        </div>

        <div class="thumbnail">
          <img src="${getImagePath(clip.image.path)}" alt="${clip.sentence_text}">
          <button class="generate-image-btn" data-index="${index}">✨ AI 이미지 생성</button>
        </div>

        <div class="translation">
          <span class="icon">📄</span>
          <span class="text">${clip.translation}</span>
        </div>

        <div class="time-range">
          <span class="start-time">${formatTime(startTime)}</span>
          <span class="separator">~</span>
          <span class="duration">${estimatedDuration.toFixed(0)}초</span>
        </div>
      </div>

      <div class="card-footer">
        <button class="btn-secondary btn-edit" data-index="${index}">편집 ✏️</button>
      </div>
    `;

    // 카드 클릭 시 비디오 seek
    cardElement.addEventListener('click', (e) => {
      if (!e.target.closest('button') && !e.target.closest('select')) {
        selectCard(index);
        seekVideoToCard(index, startTime);
      }
    });

    container.appendChild(cardElement);
  });

  // 이벤트 리스너 등록
  attachCardEventListeners();
}

function seekVideoToCard(index, startTime) {
  const video = document.getElementById('preview-video');
  video.currentTime = startTime;
  video.play();

  // 선택된 카드 하이라이트
  document.querySelectorAll('.sentence-card').forEach(card => {
    card.classList.remove('active');
  });
  document.querySelector(`.sentence-card[data-index="${index}"]`).classList.add('active');
}

function calculateStartTime(index) {
  // 인트로 길이
  let totalTime = config.global_settings.intro.duration;

  // 이전 클립들 길이 누적
  for (let i = 0; i < index; i++) {
    const clip = config.clips[i];
    totalTime += (clip.audio.repeat_count * 3) + clip.audio.pause_after;
  }

  return totalTime;
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function getImagePath(fullPath) {
  // 절대 경로를 상대 경로로 변환
  return fullPath.replace(/.*\/daily-english-mecca\//, '/');
}
```

---

## 🎨 최종 권장 UI 레이아웃

```
┌────────────────────────────────────────────────────────────────┐
│ [← 돌아가기]  비디오 편집 - Daily English Mecca     [내보내기] │
├───────────────┬────────────────────────────────────────────────┤
│               │                                                │
│  📹 미리보기   │           📝 문장 리스트 (스크롤 가능)          │
│               │                                                │
│  ┌─────────┐  │  ┌──────────────────────────────────────────┐  │
│  │         │  │  │ 🎬 Intro (3초)                          │  │
│  │ 9:16    │  │  │ [썸네일] Daily English Mecca           │  │
│  │         │  │  │ 00:00 ~ 3초                            │  │
│  │1080×1920│  │  └──────────────────────────────────────────┘  │
│  │         │  │                                                │
│  └─────────┘  │  ┌──────────────────────────────────────────┐  │
│               │  │ 1 [🔊 Alloy ▼] ☰                        │  │
│  [▶] [⏸]     │  │ The weather is nice today. ✏️          │  │
│  00:00 / 00:27│  │ [썸네일 이미지]                          │  │
│  [1x]         │  │ 📄 오늘 날씨 정말 좋네요                │  │
│               │  │ 00:03 ~ 10초                            │  │
│               │  │ [편집] [✨ AI 이미지 생성]              │  │
│               │  └──────────────────────────────────────────┘  │
│               │                                                │
│               │  ┌──────────────────────────────────────────┐  │
│               │  │ 2 [🔊 Nova ▼] ☰                         │  │
│               │  │ I love studying English. ✏️            │  │
│               │  │ [썸네일 이미지]                          │  │
│               │  │ 📄 영어 공부가 너무 좋아요               │  │
│               │  │ 00:10 ~ 17초                            │  │
│               │  │ [편집] [✨ AI 이미지 생성]              │  │
│               │  └──────────────────────────────────────────┘  │
│               │                                                │
│               │  ... (더 많은 문장)                            │
│               │                                                │
│               │  ┌──────────────────────────────────────────┐  │
│               │  │ 🎭 Outro (2초)                          │  │
│               │  │ [썸네일] 좋아요 & 구독                  │  │
│               │  │ 00:25 ~ 27초                            │  │
│               │  └──────────────────────────────────────────┘  │
├───────────────┴────────────────────────────────────────────────┤
│ 🎵 배경음악: Pixel Peeker Polka [볼륨: 15%]    [💾 저장]      │
└────────────────────────────────────────────────────────────────┘
```

---

## 📌 결론

1. **VREW는 타임라인 중심이 아니라 "문장 리스트 중심"**
2. **짧은 영상(Shorts) 편집에는 문장 리스트가 더 효율적**
3. **Daily English Mecca는 VREW 방식 채택 권장**
4. **개발 시간: 5주 (기존 9.5주 대비 47% 단축)**
5. **초보자 친화적 + 빠른 워크플로우**

**다음 단계:**
- 켈리 승인
- Phase 1 시작 (문장 리스트 UI)
- 기존 타임라인 코드 제거
- 새 문장 카드 컴포넌트 구현

---

**마지막 업데이트**: 2025-10-11
