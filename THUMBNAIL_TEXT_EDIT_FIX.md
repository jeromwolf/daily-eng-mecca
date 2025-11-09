# 텍스트 수정 버그 수정 (2025-11-09)

## 🐛 문제점

**사용자 피드백**:
"텍스트수정하기 선택해서 메인텍스트를 바꾸었는데 메인텍스트는 필수라고 나오네"

### 증상
1. [✏️ 텍스트 수정] 클릭
2. 모달에서 메인 텍스트 입력 (예: "새로운 제목")
3. [적용하기] 클릭
4. 에러 메시지: "메인 텍스트는 필수입니다." ❌

### 원인 분석

**백엔드** (`web/routes/thumbnail_routes.py:208`):
```python
# FormData 파싱
main_text = request.form.get('main_text', '').strip()

# 필수 필드 검증
if not main_text:
    return jsonify({
        'success': False,
        'error': '메인 텍스트는 필수입니다.'
    }), 400
```
→ 백엔드는 **FormData**를 기대함 (`request.form`)

**프론트엔드** (이전 코드, `web/static/js/thumbnail_studio.js:756-766`):
```javascript
// JSON으로 전송 (잘못된 방식!)
const requestData = {
    ...currentThumbnailData,
    main_text: mainText,
    subtitle_text: subtitleText
};

const response = await fetch('/thumbnail-studio/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)  // ❌ JSON 전송
});
```
→ 프론트엔드는 **JSON**으로 전송

**불일치**:
- 백엔드: `request.form` (FormData)
- 프론트엔드: `JSON.stringify()` (JSON)
- 결과: `request.form.get('main_text')` → `None` → 에러!

---

## ✅ 해결 방법

### FormData로 전송 방식 변경

**파일**: `web/static/js/thumbnail_studio.js:755-797`

#### 변경 전 (JSON)
```javascript
// 현재 썸네일 데이터에서 텍스트만 변경
const requestData = {
    ...currentThumbnailData,
    main_text: mainText,
    subtitle_text: subtitleText
};

const response = await fetch('/thumbnail-studio/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },  // ❌ JSON
    body: JSON.stringify(requestData)
});
```

#### 변경 후 (FormData)
```javascript
// FormData 생성 (백엔드가 FormData를 기대함)
const formData = new FormData();
formData.append('main_text', mainText);
formData.append('subtitle_text', subtitleText);
formData.append('style', currentThumbnailData.style || 'fire_english');
formData.append('text_position', currentThumbnailData.text_position || 'center');

// YouTube URL 및 채널 URL
if (currentThumbnailData.youtube_url) {
    formData.append('youtube_url', currentThumbnailData.youtube_url);
}
if (currentThumbnailData.channel_url) {
    formData.append('channel_url', currentThumbnailData.channel_url);
}

// 배지 옵션
if (currentThumbnailData.sentence_count) {
    formData.append('sentence_count', currentThumbnailData.sentence_count);
}
if (currentThumbnailData.video_duration) {
    formData.append('video_duration', currentThumbnailData.video_duration);
}

// 브랜드 색상
if (currentThumbnailData.brand_color_primary) {
    formData.append('brand_color_primary', currentThumbnailData.brand_color_primary);
}
if (currentThumbnailData.brand_color_secondary) {
    formData.append('brand_color_secondary', currentThumbnailData.brand_color_secondary);
}
if (currentThumbnailData.brand_color_accent) {
    formData.append('brand_color_accent', currentThumbnailData.brand_color_accent);
}

// Kelly 캐릭터
if (currentThumbnailData.use_kelly !== undefined) {
    formData.append('use_kelly', currentThumbnailData.use_kelly);
}

const response = await fetch('/thumbnail-studio/api/generate', {
    method: 'POST',
    body: formData  // ✅ FormData로 전송 (헤더 자동 설정)
});
```

---

## 🔍 변경 세부사항

### 1. FormData 객체 생성
```javascript
const formData = new FormData();
```
- `FormData`는 `multipart/form-data` 형식으로 자동 인코딩
- 파일 업로드 및 폼 데이터 전송에 적합

### 2. 필수 필드 추가
```javascript
formData.append('main_text', mainText);
formData.append('subtitle_text', subtitleText);
formData.append('style', currentThumbnailData.style || 'fire_english');
formData.append('text_position', currentThumbnailData.text_position || 'center');
```

### 3. 선택적 필드 (조건부 추가)
```javascript
if (currentThumbnailData.youtube_url) {
    formData.append('youtube_url', currentThumbnailData.youtube_url);
}
```
- `undefined` 또는 `null` 값은 전송하지 않음
- 백엔드에서 `request.form.get()` 시 기본값 반환

### 4. Headers 제거
```javascript
// 변경 전
headers: { 'Content-Type': 'application/json' },

// 변경 후
// (헤더 생략 - FormData가 자동으로 설정)
```
- `FormData` 사용 시 브라우저가 자동으로 `Content-Type: multipart/form-data; boundary=...` 설정
- 수동으로 설정하면 오히려 오류 발생 가능

---

## 📊 데이터 전송 비교

### JSON 방식 (이전, ❌ 실패)
```
POST /thumbnail-studio/api/generate
Content-Type: application/json

{
  "main_text": "새로운 제목",
  "subtitle_text": "서브 텍스트",
  "style": "fire_english",
  ...
}
```

**백엔드 수신**:
```python
request.form.get('main_text')  # None (JSON은 request.json으로 받아야 함)
```

### FormData 방식 (개선, ✅ 성공)
```
POST /thumbnail-studio/api/generate
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="main_text"

새로운 제목
------WebKitFormBoundary...
Content-Disposition: form-data; name="subtitle_text"

서브 텍스트
------WebKitFormBoundary...
```

**백엔드 수신**:
```python
request.form.get('main_text')  # "새로운 제목" ✅
```

---

## 🎯 수정 전후 비교

### 이전 워크플로우 (❌ 실패)
```
1. [✏️ 텍스트 수정] 클릭
   ↓
2. 모달에서 메인 텍스트 입력: "새로운 제목"
   ↓
3. [적용하기] 클릭
   ↓
4. JavaScript: JSON으로 전송
   {
     "main_text": "새로운 제목",
     ...
   }
   ↓
5. 백엔드: request.form.get('main_text') → None
   ↓
6. 에러: "메인 텍스트는 필수입니다." ❌
```

### 개선된 워크플로우 (✅ 성공)
```
1. [✏️ 텍스트 수정] 클릭
   ↓
2. 모달에서 메인 텍스트 입력: "새로운 제목"
   ↓
3. [적용하기] 클릭
   ↓
4. JavaScript: FormData로 전송
   formData.append('main_text', '새로운 제목')
   ↓
5. 백엔드: request.form.get('main_text') → "새로운 제목" ✅
   ↓
6. 썸네일 재생성 시작 (10-15초)
   ↓
7. 성공 메시지: "텍스트가 수정되었습니다!" ✅
```

---

## 📁 수정된 파일

**`web/static/js/thumbnail_studio.js`** (Lines 755-797)
- `JSON.stringify()` → `FormData` 변경
- 모든 필드를 `formData.append()`로 추가
- `Content-Type` 헤더 제거 (자동 설정)

---

## 🧪 테스트 체크리스트

- [x] 썸네일 생성 후 [✏️ 텍스트 수정] 클릭
- [x] 모달에서 메인 텍스트 변경 (예: "테스트 제목")
- [x] [적용하기] 클릭
- [x] 로딩 표시 (10-15초)
- [x] 에러 없이 새 썸네일 생성 확인
- [x] "텍스트가 수정되었습니다!" 성공 메시지 확인
- [x] 미리보기에 새 텍스트 표시 확인
- [x] 히스토리에 새 버전 추가 확인

---

## 💡 교훈

### 1. API 계약 준수
- 백엔드가 `request.form` 사용 → 프론트엔드는 FormData 전송
- 백엔드가 `request.json` 사용 → 프론트엔드는 JSON 전송
- **API 문서화 중요**: 요청/응답 형식 명시

### 2. 타입 불일치 디버깅
```python
# 백엔드 디버깅 팁
print(f"Content-Type: {request.content_type}")
print(f"Form data: {request.form}")
print(f"JSON data: {request.json}")
```

```javascript
// 프론트엔드 디버깅 팁
console.log('Request body type:', formData.constructor.name);
console.log('Headers:', headers);
```

### 3. FormData 사용 시 주의사항
- `Content-Type` 헤더를 **수동으로 설정하지 말 것**
- 브라우저가 `boundary` 자동 생성
- 파일 업로드 시 필수

---

## 🔄 관련 이슈

이 버그는 초기 구현 시 발생했던 타입 불일치 문제입니다:
- `generateThumbnail()` 함수는 FormData 사용 (정상 작동)
- `applyTextEdit()` 함수는 JSON 사용 (버그 발생)

→ 모든 API 호출을 FormData로 통일하여 일관성 확보

---

**작성자**: Kelly & Claude Code
**날짜**: 2025-11-09
**상태**: 수정 완료
**우선순위**: 🔴 Critical (사용자 차단 버그)
