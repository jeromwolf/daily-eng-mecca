# 텍스트 수정 후 썸네일 표시 안되는 버그 수정 (2025-11-09)

## 🐛 문제점

**사용자 피드백**:
텍스트를 바꾼 후 미리보기가 비어있고 "생성된 썸네일" 텍스트만 보임 (이미지가 로드되지 않음)

### 증상
1. [✏️ 텍스트 수정] 클릭
2. 메인 텍스트 변경 (예: "새로운 제목")
3. [적용하기] 클릭
4. 로딩... (10-15초)
5. 성공 메시지: "텍스트가 수정되었습니다!"
6. **미리보기가 비어있음** ❌ (이미지가 표시되지 않음)

### 원인 분석

**백엔드 응답** (`web/routes/thumbnail_routes.py:544`):
```python
return jsonify({
    'success': True,
    'session_id': session_id,
    'version': version,
    'thumbnail_url': thumbnail_url  # ← 'thumbnail_url' 키 사용
}), 200
```

**프론트엔드 코드** (이전, `web/static/js/thumbnail_studio.js:811`):
```javascript
// 미리보기 업데이트
displayThumbnail(data.thumbnail_path);  // ❌ 'thumbnail_path'는 존재하지 않음
```

**불일치**:
- 백엔드: `thumbnail_url`
- 프론트엔드: `thumbnail_path` (undefined)
- 결과: 이미지 src가 `undefined` → 빈 화면

---

## ✅ 해결 방법

### 1. 올바른 키 사용 및 폴백 추가

**파일**: `web/static/js/thumbnail_studio.js:818-832`

#### 변경 전
```javascript
const data = await response.json();

// 현재 썸네일 데이터 업데이트
currentThumbnailData.main_text = mainText;
currentThumbnailData.subtitle_text = subtitleText;

// 미리보기 업데이트
displayThumbnail(data.thumbnail_path);  // ❌ undefined

// 히스토리 업데이트
currentVersion++;
addToHistory(data.thumbnail_path, currentVersion);  // ❌ undefined
```

#### 변경 후
```javascript
const data = await response.json();

// 현재 썸네일 데이터 업데이트
currentThumbnailData.main_text = mainText;
currentThumbnailData.subtitle_text = subtitleText;

// 세션 ID 및 버전 업데이트
if (data.session_id) {
    currentSessionId = data.session_id;
}
if (data.version) {
    currentVersion = data.version;
}

// 미리보기 업데이트 (thumbnail_url 사용, 폴백 포함)
const thumbnailUrl = data.thumbnail_url || data.thumbnail_path;
if (thumbnailUrl) {
    displayThumbnail(thumbnailUrl);  // ✅ 정상 표시

    // 히스토리 새로고침 (세션이 있으면)
    if (currentSessionId) {
        loadHistory(currentSessionId);
    }

    // 재생성 옵션 표시
    document.getElementById('regeneration-options').classList.remove('hidden');
} else {
    throw new Error('썸네일 URL을 받지 못했습니다');
}
```

---

## 🔍 변경 세부사항

### 1. 올바른 키 사용
```javascript
// 변경 전
displayThumbnail(data.thumbnail_path);  // ❌ undefined

// 변경 후
const thumbnailUrl = data.thumbnail_url || data.thumbnail_path;  // ✅ 폴백 포함
displayThumbnail(thumbnailUrl);
```

**폴백 이유**:
- 현재 백엔드: `thumbnail_url`
- 미래 호환성: `thumbnail_path`도 지원
- 둘 다 없으면 에러 발생

### 2. 세션 ID 및 버전 업데이트
```javascript
if (data.session_id) {
    currentSessionId = data.session_id;
}
if (data.version) {
    currentVersion = data.version;
}
```

**이유**:
- 텍스트 수정 시 새로운 세션 생성 가능
- 버전 번호를 백엔드에서 받아 동기화
- 히스토리 로딩에 필요

### 3. 히스토리 로딩 변경
```javascript
// 변경 전
currentVersion++;  // 수동 증가 (잘못된 버전 번호 가능)
addToHistory(data.thumbnail_path, currentVersion);  // 히스토리 1개만 추가

// 변경 후
if (currentSessionId) {
    loadHistory(currentSessionId);  // 전체 히스토리 새로고침
}
```

**이유**:
- `loadHistory()`: 서버에서 전체 히스토리를 가져와 표시
- `addToHistory()`: 클라이언트에서 수동 추가 (동기화 문제 가능)
- 세션 기반 히스토리 관리가 더 안정적

### 4. 재생성 옵션 표시
```javascript
document.getElementById('regeneration-options').classList.remove('hidden');
```

**이유**:
- 텍스트 수정 후에도 재생성 버튼들 표시
- [📥 다운로드], [✏️ 텍스트 수정], [🔄 새로 생성] 사용 가능

### 5. 에러 처리
```javascript
if (thumbnailUrl) {
    displayThumbnail(thumbnailUrl);
    // ...
} else {
    throw new Error('썸네일 URL을 받지 못했습니다');
}
```

**이유**:
- `thumbnailUrl`이 `undefined`이면 명확한 에러 메시지
- 디버깅 용이

---

## 📊 수정 전후 비교

### 이전 워크플로우 (❌ 실패)
```
1. [✏️ 텍스트 수정] 클릭
   ↓
2. 메인 텍스트 입력: "새로운 제목"
   ↓
3. [적용하기] 클릭
   ↓
4. FormData 전송 (정상)
   ↓
5. 백엔드 응답:
   {
     "success": true,
     "session_id": "abc123",
     "version": 2,
     "thumbnail_url": "/thumbnail-studio/api/download/abc123/v2"
   }
   ↓
6. displayThumbnail(data.thumbnail_path)
   → data.thumbnail_path = undefined ❌
   → <img src="undefined"> ❌
   ↓
7. 빈 화면 (이미지 없음)
```

### 개선된 워크플로우 (✅ 성공)
```
1. [✏️ 텍스트 수정] 클릭
   ↓
2. 메인 텍스트 입력: "새로운 제목"
   ↓
3. [적용하기] 클릭
   ↓
4. FormData 전송 (정상)
   ↓
5. 백엔드 응답:
   {
     "success": true,
     "session_id": "abc123",
     "version": 2,
     "thumbnail_url": "/thumbnail-studio/api/download/abc123/v2"
   }
   ↓
6. const thumbnailUrl = data.thumbnail_url || data.thumbnail_path
   → thumbnailUrl = "/thumbnail-studio/api/download/abc123/v2" ✅
   ↓
7. displayThumbnail(thumbnailUrl)
   → <img src="/thumbnail-studio/api/download/abc123/v2"> ✅
   ↓
8. 이미지 표시 성공! 🎉
   ↓
9. loadHistory(currentSessionId)
   → 히스토리에 v1, v2 모두 표시
   ↓
10. 재생성 옵션 표시
    → [📥 다운로드] [✏️ 텍스트 수정] [🔄 새로 생성]
```

---

## 🔧 추가 개선사항

### 1. 세션 ID 동기화
```javascript
if (data.session_id) {
    currentSessionId = data.session_id;
}
```
- 텍스트 수정 시 새 세션 생성 가능
- 현재 세션 ID를 최신 상태로 유지

### 2. 버전 번호 동기화
```javascript
if (data.version) {
    currentVersion = data.version;
}
```
- 백엔드에서 정확한 버전 번호 받음
- 수동 증가(`currentVersion++`)보다 안정적

### 3. 히스토리 완전 새로고침
```javascript
if (currentSessionId) {
    loadHistory(currentSessionId);
}
```
- 서버에서 전체 히스토리 가져옴
- 클라이언트-서버 동기화 보장

---

## 📁 수정된 파일

**`web/static/js/thumbnail_studio.js`** (Lines 818-832)
- `data.thumbnail_path` → `data.thumbnail_url` 변경
- 폴백 로직 추가 (`data.thumbnail_url || data.thumbnail_path`)
- 세션 ID 및 버전 동기화 추가
- 히스토리 로딩 변경 (`addToHistory` → `loadHistory`)
- 재생성 옵션 표시 추가
- 에러 처리 추가

---

## 🧪 테스트 체크리스트

- [x] 썸네일 생성 후 [✏️ 텍스트 수정] 클릭
- [x] 메인 텍스트 변경 (예: "새로운 제목")
- [x] [적용하기] 클릭
- [x] 로딩 표시 확인 (10-15초)
- [x] **이미지가 미리보기에 표시되는지 확인** ✅
- [x] 성공 메시지: "텍스트가 수정되었습니다!" 확인
- [x] 히스토리에 v1, v2 모두 표시되는지 확인
- [x] 재생성 옵션 버튼들 표시 확인
- [x] [📥 다운로드] 버튼 클릭 → 새 텍스트 썸네일 다운로드 확인

---

## 💡 교훈

### 1. API 응답 키 일관성
```javascript
// 나쁜 예 (하드코딩)
displayThumbnail(data.thumbnail_path);  // 키 이름 변경 시 오류

// 좋은 예 (폴백 포함)
const thumbnailUrl = data.thumbnail_url || data.thumbnail_path;
if (thumbnailUrl) {
    displayThumbnail(thumbnailUrl);
} else {
    throw new Error('썸네일 URL을 받지 못했습니다');
}
```

### 2. 서버-클라이언트 동기화
```javascript
// 나쁜 예 (클라이언트에서 수동 관리)
currentVersion++;
addToHistory(thumbnailUrl, currentVersion);

// 좋은 예 (서버에서 최신 상태 받기)
if (data.version) {
    currentVersion = data.version;
}
if (currentSessionId) {
    loadHistory(currentSessionId);  // 서버에서 전체 히스토리 가져오기
}
```

### 3. 디버깅 팁
```javascript
// 응답 데이터 로깅
console.log('✅ API 응답:', data);
console.log('  - thumbnail_url:', data.thumbnail_url);
console.log('  - session_id:', data.session_id);
console.log('  - version:', data.version);
```

---

## 🔗 관련 버그

이 버그는 이전 "메인 텍스트는 필수입니다" 버그와 연쇄적으로 발생:
1. FormData 전송 문제 → 해결 ✅
2. **이미지 표시 문제** → 해결 ✅

두 버그를 모두 수정하여 텍스트 수정 기능이 완전히 작동합니다!

---

**작성자**: Kelly & Claude Code
**날짜**: 2025-11-09
**상태**: 수정 완료
**우선순위**: 🔴 Critical (사용자 경험 저해)
