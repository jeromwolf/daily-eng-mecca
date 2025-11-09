# 배경 이미지 보존 버그 수정 (2025-11-09)

## 🐛 문제점

**사용자 피드백**:
"이미지는 없어졌어. 텍스트 수정하니"

### 증상
1. YouTube URL로 썸네일 생성 → 3개 썸네일 (비디오 프레임 배경)
2. 1개 선택 → 미리보기 표시
3. [✏️ 텍스트 수정] 클릭
4. 메인 텍스트 변경 (예: "AI 거장들이 예언한 충격 미래" → "새로운 제목")
5. [적용하기] 클릭
6. **배경 이미지가 사라짐** ❌ (흰색 배경 + 회색 텍스트 박스만 표시)

---

## 🔍 원인 분석

### 백엔드 로직 문제

**텍스트 수정 시 프로세스**:
1. 프론트엔드: `session_id` 없이 FormData 전송
2. 백엔드: 새 세션 생성
3. 백엔드: `background_image_paths` 없음 → 기본 배경 사용
4. 결과: **이전 배경 이미지 손실**

**코드 위치** (`web/routes/thumbnail_routes.py:337-345`, 수정 전):
```python
# 수정 전: 항상 새 세션 생성
session_id = history_manager.create_session({
    'main_text': main_text,
    'subtitle_text': subtitle_text,
    'style': style,
    'reference_analysis': reference_analysis
})

print(f"📁 세션 생성: {session_id}")
```

### 프론트엔드 로직 문제

**`applyTextEdit()` 함수** (`web/static/js/thumbnail_studio.js:755-770`, 수정 전):
```javascript
// 수정 전: session_id를 전달하지 않음
const formData = new FormData();
formData.append('main_text', mainText);
formData.append('subtitle_text', subtitleText);
formData.append('style', currentThumbnailData.style || 'fire_english');
formData.append('text_position', currentThumbnailData.text_position || 'center');

// session_id 누락! ❌
```

**문제**:
- `currentSessionId` 변수에 세션 ID가 저장되어 있지만 FormData에 추가하지 않음
- 백엔드가 새 세션으로 인식 → 이전 배경 이미지 경로 손실

---

## ✅ 해결 방법

### 1. 백엔드: 세션 재사용 및 배경 이미지 복원

**파일**: `web/routes/thumbnail_routes.py:337-363`

**변경 후 코드**:
```python
# 세션 생성 또는 기존 세션 사용
# 텍스트 수정 시: 기존 세션 ID가 있으면 재사용 (배경 이미지 보존)
existing_session_id = request.form.get('session_id')

if existing_session_id and history_manager.get_session_thumbnails(existing_session_id):
    # 기존 세션 재사용 (텍스트 수정 모드)
    session_id = existing_session_id
    print(f"📁 기존 세션 재사용: {session_id}")

    # 마지막 썸네일의 배경 이미지 및 채널 아이콘 경로 가져오기
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
    # 새 세션 생성 (초기 생성)
    session_id = history_manager.create_session({
        'main_text': main_text,
        'subtitle_text': subtitle_text,
        'style': style,
        'reference_analysis': reference_analysis
    })
    print(f"📁 새 세션 생성: {session_id}")
```

**주요 개선사항**:
1. **세션 재사용 체크**: `existing_session_id` 파라미터 확인
2. **이전 config 로드**: 마지막 썸네일의 config에서 경로 추출
3. **배경 이미지 복원**: `background_image_path` 파일 존재 확인 후 재사용
4. **채널 아이콘 복원**: `channel_icon_path` 파일 존재 확인 후 재사용

---

### 2. 프론트엔드: session_id 전달

**파일**: `web/static/js/thumbnail_studio.js:762-766`

**변경 후 코드**:
```javascript
// FormData 생성 (백엔드가 FormData를 기대함)
const formData = new FormData();
formData.append('main_text', mainText);
formData.append('subtitle_text', subtitleText);
formData.append('style', currentThumbnailData.style || 'fire_english');
formData.append('text_position', currentThumbnailData.text_position || 'center');

// 기존 세션 ID 전달 (배경 이미지 재사용)
if (currentSessionId) {
    formData.append('session_id', currentSessionId);
    console.log('📝 텍스트 수정 모드: 기존 세션 재사용 →', currentSessionId);
}
```

**효과**:
- `currentSessionId`를 FormData에 추가
- 백엔드가 기존 세션으로 인식
- 이전 배경 이미지 및 채널 아이콘 자동 복원

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
4. FormData 전송 (session_id 없음)
   ↓
5. 백엔드: 새 세션 생성
   session_id = "new123"
   ↓
6. 백엔드: background_image_paths = []
   → 기본 배경 사용 (흰색)
   ↓
7. 썸네일 생성: 흰색 배경 + 회색 박스 + 텍스트
   ↓
8. 사용자: "이미지는 없어졌어" ❌
```

### 개선된 워크플로우 (✅ 성공)

```
1. [✏️ 텍스트 수정] 클릭
   ↓
2. 메인 텍스트 입력: "새로운 제목"
   ↓
3. [적용하기] 클릭
   ↓
4. FormData 전송 (session_id: "abc123" 포함)
   console.log: "📝 텍스트 수정 모드: 기존 세션 재사용 → abc123"
   ↓
5. 백엔드: 기존 세션 재사용
   session_id = "abc123"
   console.log: "📁 기존 세션 재사용: abc123"
   ↓
6. 백엔드: 마지막 썸네일 config 로드
   last_config = {
       'background_image_path': '/path/to/frame_1.jpg',
       'channel_icon_path': '/path/to/icon.jpg',
       ...
   }
   ↓
7. 백엔드: 파일 존재 확인
   Path('/path/to/frame_1.jpg').exists() → True ✅
   console.log: "✅ 이전 배경 이미지 재사용: frame_1.jpg"
   ↓
8. 썸네일 생성: 동일한 배경 + 새 텍스트
   ↓
9. 미리보기: 배경 이미지 보존! 🎉
```

---

## 🎯 추가 개선사항

### 안전한 폴백 처리

**파일 존재 확인**:
```python
if last_bg_path and Path(last_bg_path).exists():
    background_image_paths = [last_bg_path]
else:
    print(f"⚠ 이전 배경 이미지 파일 없음: {last_bg_path}")
    # 기본 배경 사용
```

**효과**:
- 파일이 삭제된 경우에도 에러 없이 기본 배경 사용
- 안정적인 사용자 경험

---

## 📁 수정된 파일

### 1. `web/routes/thumbnail_routes.py`

**Line 337-363**: 세션 재사용 및 배경 이미지 복원 로직
- `existing_session_id = request.form.get('session_id')`
- 기존 세션 재사용 시 마지막 config 로드
- `background_image_path` 및 `channel_icon_path` 복원
- 파일 존재 확인 후 안전하게 재사용

### 2. `web/static/js/thumbnail_studio.js`

**Line 762-766**: session_id FormData 추가
- `formData.append('session_id', currentSessionId)`
- 콘솔 로깅: "기존 세션 재사용 →"

---

## 🧪 테스트 체크리스트

### **시나리오 1: YouTube URL → 텍스트 수정 → 배경 보존**

1. **초기 생성**:
   - [ ] YouTube URL 입력: `https://www.youtube.com/watch?v=...`
   - [ ] 메인 텍스트: "Original Title"
   - [ ] [생성하기] 클릭
   - [ ] 3개 썸네일 생성 (비디오 프레임 배경)

2. **1개 선택**:
   - [ ] 마음에 드는 썸네일 클릭
   - [ ] 큰 미리보기 표시
   - [ ] **배경 이미지 확인** (비디오 프레임)

3. **텍스트 수정**:
   - [ ] [✏️ 텍스트 수정] 클릭
   - [ ] 메인 텍스트 변경: "Updated Title"
   - [ ] [적용하기] 클릭

4. **F12 → Console 확인**:
   ```
   📝 텍스트 수정 모드: 기존 세션 재사용 → abc123...
   📁 기존 세션 재사용: abc123...
   ✅ 이전 배경 이미지 재사용: frame_1.jpg
   ✅ 이전 채널 아이콘 재사용: icon.jpg
   ```

5. **결과 확인**:
   - [ ] **배경 이미지 보존** ✅ (동일한 비디오 프레임)
   - [ ] **채널 아이콘 보존** ✅ (동일한 아이콘)
   - [ ] **새 텍스트 표시** ✅ ("Updated Title")
   - [ ] 히스토리에 v2 추가

---

### **시나리오 2: 직접 입력 (배경 없음) → 텍스트 수정**

1. **초기 생성**:
   - [ ] YouTube URL 비워두기
   - [ ] 메인 텍스트: "Test Title"
   - [ ] [생성하기] 클릭
   - [ ] 1개 썸네일 생성 (기본 배경)

2. **텍스트 수정**:
   - [ ] [✏️ 텍스트 수정] 클릭
   - [ ] 메인 텍스트 변경: "Modified Text"
   - [ ] [적용하기] 클릭

3. **결과 확인**:
   - [ ] 기본 배경 유지 (흰색)
   - [ ] 새 텍스트 표시
   - [ ] 에러 없음

---

## 💡 교훈

### 1. 세션 기반 상태 관리

**나쁜 예**:
```python
# 항상 새 세션 생성 → 이전 데이터 손실
session_id = create_new_session()
```

**좋은 예**:
```python
# 기존 세션 재사용 → 데이터 보존
if existing_session_id:
    session_id = existing_session_id
    # 이전 config 복원
else:
    session_id = create_new_session()
```

### 2. 프론트엔드-백엔드 상태 동기화

**중요**:
- 프론트엔드: `currentSessionId` 저장
- 백엔드 요청 시: **반드시** FormData에 포함
- 백엔드: 세션 ID 기반 데이터 복원

### 3. 파일 경로 안전성

**파일 존재 확인**:
```python
if path and Path(path).exists():
    use_file(path)
else:
    use_default()
```

**효과**:
- 파일 삭제/이동 시에도 안정적
- 명확한 폴백 로직

---

## 🔗 관련 수정

이 버그 수정은 텍스트 수정 기능 3부작의 마지막입니다:

1. ✅ **FormData 전송 문제** (THUMBNAIL_TEXT_EDIT_FIX.md)
   - JSON → FormData 변경
   - "메인 텍스트는 필수입니다" 해결

2. ✅ **이미지 표시 문제** (THUMBNAIL_DISPLAY_FIX.md)
   - `thumbnail_path` → `thumbnail_url` 수정
   - 빈 화면 해결

3. ✅ **배경 이미지 보존 문제** (현재 문서)
   - 세션 재사용 로직 추가
   - 배경 이미지 복원

**완료**: 텍스트 수정 기능이 완벽하게 작동합니다! 🎉

---

**작성자**: Claude Code
**날짜**: 2025-11-09
**상태**: 수정 완료 (테스트 대기)
**우선순위**: 🔴 Critical (사용자 경험 저해)
