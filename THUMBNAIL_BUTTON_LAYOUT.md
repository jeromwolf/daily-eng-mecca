# 썸네일 선택 화면 버튼 레이아웃 개선 (2025-11-09)

## 📌 문제점

사용자 피드백:
1. "메뉴가 세로로 되어 있고" - 버튼들이 세로로 배치되어 공간 낭비
2. "텍스트를 바꿀 수 있는 부분도 있으면 좋겠어" - 텍스트 수정 기능 없음

### 이전 레이아웃 (세로)
```
┌─────────────────────────┐
│  버전 1   버전 2  버전 3 │
│  [선택]  [선택]  [선택] │
├─────────────────────────┤
│  📥 선택한 썸네일 다운로드  │  ← 세로 배치 (공간 낭비)
│  🔄 다시 생성하기         │
└─────────────────────────┘
```

---

## ✅ 해결 방법

### 개선된 레이아웃 (가로)
```
┌─────────────────────────────────────┐
│    버전 1     버전 2     버전 3      │
│   [선택]     [선택]     [선택]      │
├─────────────────────────────────────┤
│ 📥 다운로드  ✏️ 텍스트 수정  🔄 새로 생성 │  ← 가로 배치 (깔끔!)
└─────────────────────────────────────┘
```

### 주요 변경사항
1. **버튼 3개로 확장**: 다운로드 + **텍스트 수정** + 새로 생성
2. **가로 배치 강제**: `flex-direction: row`
3. **텍스트 간소화**: "선택한 썸네일 다운로드" → "다운로드"
4. **반응형 디자인**: 모바일에서도 가로 유지 (아주 작은 화면만 세로)

---

## 🔧 구현 내용

### 1. JavaScript - 버튼 추가 및 간소화
**파일**: `web/static/js/thumbnail_studio.js:519-539`

#### 변경 전
```javascript
actions.innerHTML = `
    <button id="btn-download-selected" class="btn-primary">
        📥 선택한 썸네일 다운로드  // 너무 김
    </button>
    <button id="btn-regenerate-new" class="btn-secondary">
        🔄 다시 생성하기  // 너무 김
    </button>
`;

// 이벤트 리스너
document.getElementById('btn-download-selected').addEventListener('click', downloadSelectedThumbnail);
document.getElementById('btn-regenerate-new').addEventListener('click', () => {
    if (confirm('새로 생성하시겠습니까?')) {
        location.reload();
    }
});
```

#### 변경 후
```javascript
// 액션 버튼들 (가로 배치)
const actions = document.createElement('div');
actions.className = 'selection-actions';
actions.innerHTML = `
    <button id="btn-download-selected" class="btn-primary">
        📥 다운로드  // 간소화
    </button>
    <button id="btn-edit-selected-text" class="btn-primary">
        ✏️ 텍스트 수정  // 신규 추가
    </button>
    <button id="btn-regenerate-new" class="btn-secondary">
        🔄 새로 생성  // 간소화
    </button>
`;
preview.appendChild(actions);

// 이벤트 리스너
document.getElementById('btn-download-selected').addEventListener('click', downloadSelectedThumbnail);
document.getElementById('btn-edit-selected-text').addEventListener('click', openTextEditModal);  // 신규
document.getElementById('btn-regenerate-new').addEventListener('click', () => {
    if (confirm('새로 생성하시겠습니까?')) {
        location.reload();
    }
});
```

**효과**:
- 버튼 텍스트 간소화 (가로 공간 절약)
- 텍스트 수정 버튼 추가 (기존 `openTextEditModal` 함수 재사용)
- 일관된 워크플로우 (3개 버전 선택 → 텍스트 수정 → 다운로드)

---

### 2. CSS - 가로 배치 강제 및 반응형
**파일**: `web/static/css/thumbnail_studio.css:737-888`

#### 변경 전
```css
.selection-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.selection-actions button {
    padding: 15px 30px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
    .selection-actions {
        flex-direction: column;  /* 세로 배치! */
        gap: 10px;
    }

    .selection-actions button {
        width: 100%;
    }
}
```

#### 변경 후
```css
.selection-actions {
    display: flex;
    flex-direction: row;  /* 가로 배치 강제 */
    gap: 12px;
    justify-content: center;
    align-items: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    flex-wrap: wrap;  /* 작은 화면에서 줄바꿈 */
}

.selection-actions button {
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    white-space: nowrap;  /* 텍스트 줄바꿈 방지 */
    min-width: 120px;  /* 최소 너비 */
}

/* 모바일 반응형 (768px 이하) */
@media (max-width: 768px) {
    .selection-actions {
        flex-direction: row;  /* 모바일에서도 가로 유지! */
        gap: 8px;
        padding: 15px 10px;
        flex-wrap: wrap;  /* 필요시 줄바꿈 */
    }

    .selection-actions button {
        flex: 1 1 auto;  /* 균등하게 늘어남 */
        min-width: 100px;
        font-size: 14px;
        padding: 10px 16px;
    }
}

/* 매우 작은 화면 (360px 이하) */
@media (max-width: 360px) {
    .selection-actions {
        flex-direction: column;  /* 아주 작은 화면만 세로 */
    }

    .selection-actions button {
        width: 100%;
    }
}
```

**주요 변경사항**:
1. **`flex-direction: row` 명시** - 가로 배치 강제
2. **`flex-wrap: wrap`** - 필요시 줄바꿈 (3개 버튼이 한 줄에 안 들어가면 2줄)
3. **`white-space: nowrap`** - 버튼 텍스트 줄바꿈 방지
4. **`min-width: 120px`** - 버튼 최소 너비 (균일한 크기)
5. **모바일에서도 가로 유지** - 768px 이하에서도 `flex-direction: row`
6. **초소형 화면 대응** - 360px 이하만 세로 배치

---

## 📊 레이아웃 비교

### 데스크톱 (1024px+)
```
이전:
┌──────────────────────────┐
│ 📥 선택한 썸네일 다운로드  │  ← 세로 (공간 낭비)
│ 🔄 다시 생성하기          │
└──────────────────────────┘

개선:
┌──────────────────────────────────────┐
│ 📥 다운로드  ✏️ 텍스트 수정  🔄 새로 생성 │  ← 가로 (깔끔!)
└──────────────────────────────────────┘
```

### 태블릿 (768px)
```
이전:
┌──────────────────────────┐
│ 📥 선택한 썸네일 다운로드  │  ← 세로
│ 🔄 다시 생성하기          │
└──────────────────────────┘

개선:
┌───────────────────────────────┐
│ 📥 다운로드  ✏️ 텍스트 수정    │  ← 가로 유지
│ 🔄 새로 생성                  │  (필요시 2줄)
└───────────────────────────────┘
```

### 모바일 (375px)
```
이전:
┌──────────────────┐
│ 📥 선택한 썸네일  │  ← 세로
│    다운로드       │
│ 🔄 다시 생성하기 │
└──────────────────┘

개선:
┌────────────────────┐
│ 📥      ✏️     🔄  │  ← 가로 (축약 아이콘)
│ 다운로드 텍스트 새로생성 │
└────────────────────┘
```

### 초소형 (360px 이하)
```
┌──────────────┐
│ 📥 다운로드   │  ← 세로 (필요시만)
│ ✏️ 텍스트 수정 │
│ 🔄 새로 생성  │
└──────────────┘
```

---

## 🎯 사용 시나리오

### 시나리오 1: 3개 버전 선택 → 텍스트 수정 → 다운로드
```
1. YouTube URL 입력 → [생성하기]
   ↓
2. 3개 버전 생성 완료
   버전 1: "여행영어 마스터"
   버전 2: "필수 여행영어"  ← 선택
   버전 3: "여행영어 완전정복"
   ↓
3. [✏️ 텍스트 수정] 클릭
   메인 텍스트: "공항 체크인 영어" (변경)
   ↓
4. 새 텍스트로 재생성 (10-15초)
   ↓
5. [📥 다운로드] 클릭
```

### 시나리오 2: 마음에 안 들면 새로 생성
```
1. 3개 버전 확인
   → "아무것도 마음에 안 들어..."
   ↓
2. [🔄 새로 생성] 클릭
   → 확인 대화상자: "새로 생성하시겠습니까?"
   ↓
3. [확인] 클릭
   → 페이지 새로고침 (새로운 3개 버전 생성)
```

---

## 📁 수정된 파일

1. **`web/static/js/thumbnail_studio.js`** (Lines 519-539)
   - 버튼 3개로 확장 (다운로드 + 텍스트 수정 + 새로 생성)
   - 텍스트 간소화 ("선택한 썸네일 다운로드" → "다운로드")
   - `openTextEditModal` 이벤트 리스너 추가

2. **`web/static/css/thumbnail_studio.css`** (Lines 737-888)
   - `flex-direction: row` 명시 (가로 배치 강제)
   - `flex-wrap: wrap` 추가 (줄바꿈 지원)
   - 모바일 반응형 개선 (768px 이하에서도 가로 유지)
   - 360px 이하 초소형 화면만 세로 배치

---

## 🚀 효과

1. **공간 효율성**
   - 세로 배치 → 가로 배치 (공간 50% 절약)
   - 3개 버튼이 한 줄에 표시

2. **텍스트 수정 기능 접근성**
   - 3개 버전 선택 화면에서도 텍스트 수정 가능
   - 워크플로우 개선: 선택 → 수정 → 다운로드

3. **사용자 경험**
   - 버튼 텍스트 간소화 (가독성 향상)
   - 일관된 레이아웃 (데스크톱/모바일 모두 가로)
   - 직관적인 아이콘 (📥 ✏️ 🔄)

4. **반응형 디자인**
   - 모바일에서도 깔끔한 가로 배치
   - 필요시 자동 줄바꿈 (2줄)
   - 초소형 화면만 세로 배치

---

## 🧪 테스트 체크리스트

- [ ] 데스크톱 (1920px): 버튼 3개 가로 배치 확인
- [ ] 태블릿 (768px): 가로 배치 유지 확인
- [ ] 모바일 (375px): 가로 배치 또는 2줄 확인
- [ ] 초소형 (360px): 세로 배치 확인
- [ ] [✏️ 텍스트 수정] 클릭 → 모달 팝업 확인
- [ ] [📥 다운로드] 클릭 → 선택한 썸네일 다운로드 확인
- [ ] [🔄 새로 생성] 클릭 → 확인 대화상자 → 페이지 새로고침

---

**작성자**: Kelly & Claude Code
**날짜**: 2025-11-09
**상태**: 완료 (테스트 대기)
