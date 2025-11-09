# 텍스트 수정 기능 테스트 가이드 (2025-11-09)

## 🎯 테스트 목적

"썸네일 URL을 받지 못했습니다" 에러 수정 확인

---

## ✅ 수정 내용 요약

### 1. YouTube URL 제외 (텍스트 수정 시)
- **위치**: `web/static/js/thumbnail_studio.js:762-764`
- **목적**: 텍스트 수정 시 YouTube 비디오 프레임 재추출 방지 → 1개 썸네일만 생성
- **코드**:
  ```javascript
  // YouTube URL은 텍스트 수정 시 제외 (새로 프레임 추출 방지, 1개만 생성)
  console.log('📝 텍스트 수정 모드: YouTube URL 제외 (1개 썸네일만 생성)');
  ```

### 2. 유연한 응답 처리 (1개 또는 3개 썸네일 대응)
- **위치**: `web/static/js/thumbnail_studio.js:813-856`
- **목적**: 백엔드 응답 형식에 따라 자동 대응
- **3가지 경우**:
  1. **3개 썸네일 생성** (`data.count > 1` + `data.thumbnail_urls` 배열)
     - → `displayThumbnailSelection()` 호출 (선택 UI 표시)
  2. **1개 썸네일 생성** (`data.thumbnail_url` 또는 `data.thumbnail_urls[0]`)
     - → `displayThumbnail()` 호출 (미리보기 표시)
  3. **에러 발생** (URL 없음)
     - → 자세한 에러 메시지 표시

### 3. 디버깅 로깅 추가
- **위치**: `web/static/js/thumbnail_studio.js:802, 816, 826, 845`
- **목적**: 브라우저 콘솔에서 백엔드 응답 확인
- **로그 메시지**:
  - `✅ 백엔드 응답:` (전체 응답 데이터)
  - `📸 3개 썸네일 생성됨:` (3개 생성 시)
  - `📸 1개 썸네일 생성됨:` (1개 생성 시)
  - `❌ 응답 데이터:` (에러 시)

---

## 🧪 테스트 시나리오

### **시나리오 1: YouTube URL로 썸네일 생성 → 텍스트 수정**

#### 1단계: 초기 생성
1. 썸네일 스튜디오 페이지 열기: `http://localhost:5001/thumbnail-studio/`
2. YouTube URL 입력: `https://www.youtube.com/watch?v=dQw4w9WgxcQ`
3. 메인 텍스트: "Original Title"
4. 서브 텍스트: "Original Subtitle"
5. [생성하기] 클릭
6. **예상 결과**: 3개 썸네일 표시 (비디오 프레임 3개)

#### 2단계: 1개 선택
1. 마음에 드는 썸네일 1개 선택
2. **예상 결과**: 큰 미리보기 + 3개 버튼 표시
   - [📥 다운로드]
   - [✏️ 텍스트 수정]
   - [🔄 새로 생성]

#### 3단계: 텍스트 수정
1. [✏️ 텍스트 수정] 클릭
2. 모달 팝업 표시 확인
3. 메인 텍스트 변경: "Updated Title"
4. 서브 텍스트 변경: "Updated Subtitle"
5. [적용하기] 클릭
6. **F12 키** 눌러 개발자 도구 열기 → **Console 탭** 확인

#### 4단계: 콘솔 로그 확인
**예상 로그**:
```
📝 텍스트 수정 모드: YouTube URL 제외 (1개 썸네일만 생성)
✅ 백엔드 응답: {
    success: true,
    session_id: "abc123...",
    versions: [2],
    thumbnail_urls: ["/thumbnail-studio/api/download/abc123.../v2"],
    count: 1
}
📸 1개 썸네일 생성됨: /thumbnail-studio/api/download/abc123.../v2
```

#### 5단계: 결과 확인
**성공 시**:
- ✅ 미리보기에 **새 텍스트**가 표시된 썸네일 로드
- ✅ 성공 메시지: "텍스트가 수정되었습니다!"
- ✅ 히스토리에 v1, v2 모두 표시 (좌측 사이드바)
- ✅ [📥 다운로드] 버튼 활성화

**실패 시**:
- ❌ 빈 화면 또는 에러 메시지
- 콘솔 로그를 **스크린샷**으로 캡처하여 공유 필요

---

### **시나리오 2: 직접 입력 (YouTube URL 없이) → 텍스트 수정**

#### 1단계: 초기 생성
1. 썸네일 스튜디오 페이지 열기
2. **YouTube URL 비워두기** (입력 안 함)
3. 메인 텍스트: "Test Title"
4. 서브 텍스트: "Test Subtitle"
5. 스타일: Fire English
6. [생성하기] 클릭
7. **예상 결과**: 1개 썸네일만 생성 (배경 없음, Fire English 스타일)

#### 2단계: 텍스트 수정
1. [✏️ 텍스트 수정] 클릭
2. 메인 텍스트 변경: "Modified Text"
3. [적용하기] 클릭
4. **F12 → Console 확인**

#### 3단계: 콘솔 로그 확인
**예상 로그**:
```
📝 텍스트 수정 모드: YouTube URL 제외 (1개 썸네일만 생성)
✅ 백엔드 응답: {
    success: true,
    session_id: "xyz789...",
    versions: [2],
    thumbnail_urls: ["/thumbnail-studio/api/download/xyz789.../v2"],
    count: 1
}
📸 1개 썸네일 생성됨: /thumbnail-studio/api/download/xyz789.../v2
```

#### 4단계: 결과 확인
- ✅ 새 텍스트 표시
- ✅ 성공 메시지
- ✅ 히스토리 업데이트

---

## 🐛 에러 발생 시 대처 방법

### **에러 1: "썸네일 URL을 받지 못했습니다"**

#### 확인 사항:
1. **F12 → Console 탭** 열기
2. `❌ 응답 데이터:` 로그 찾기
3. 실제 백엔드 응답 구조 확인

#### 예상 응답 (정상):
```javascript
{
    success: true,
    session_id: "...",
    versions: [2],
    thumbnail_urls: ["/thumbnail-studio/api/download/.../v2"],
    count: 1
}
```

#### 비정상 응답 예시:
```javascript
// Case A: thumbnail_urls가 배열이 아님
{
    success: true,
    thumbnail_url: "/..." // 단일 문자열 (현재 코드로 처리 가능)
}

// Case B: success가 false
{
    success: false,
    error: "..."
}

// Case C: 응답 구조가 완전히 다름
{
    data: { ... }  // 예상 외 구조
}
```

#### 해결 방법:
- 콘솔 로그 **스크린샷** 캡처
- 백엔드 서버 로그 확인 (터미널에서 Flask 출력 확인)
- GitHub Issue에 스크린샷 + 서버 로그 공유

---

### **에러 2: "메인 텍스트는 필수입니다"**

#### 원인:
- FormData 전송이 안 되고 JSON으로 전송되는 경우
- 현재 코드는 수정되어 있으므로 발생하지 않아야 함

#### 확인 방법:
1. **F12 → Network 탭** 열기
2. [적용하기] 클릭
3. `generate` 요청 찾기
4. **Payload** 섹션 확인:
   ```
   main_text: "Updated Title"
   subtitle_text: "Updated Subtitle"
   style: fire_english
   ...
   ```
   (FormData 형식이어야 함)

---

### **에러 3: 빈 화면 (이미지 표시 안 됨)**

#### 원인:
- `thumbnail_url`이 undefined인 경우
- 이미지 경로가 잘못된 경우

#### 확인 방법:
1. **F12 → Network 탭** 열기
2. `/thumbnail-studio/api/download/...` 요청 확인
3. **Status Code** 확인:
   - 200: 정상 (이미지 로드 성공)
   - 404: 파일 없음 (서버에 이미지 파일 미생성)
   - 500: 서버 에러

#### 해결 방법:
- Status 200인데 안 보이면: 브라우저 캐시 문제 → `Ctrl+Shift+R` (강제 새로고침)
- Status 404: 백엔드 썸네일 생성 실패 → 서버 로그 확인
- Status 500: 서버 에러 → 서버 로그 확인

---

## 📸 스크린샷 가이드

### 성공 시 캡처할 것:
1. **미리보기 화면** (새 텍스트가 표시된 썸네일)
2. **성공 메시지** (초록색 토스트)
3. **히스토리 사이드바** (v1, v2 모두 표시)
4. **콘솔 로그** (F12 → Console)

### 실패 시 캡처할 것:
1. **에러 메시지** (빨간색 토스트)
2. **콘솔 로그** (F12 → Console) - 전체 스크롤하여 모든 로그 포함
3. **Network 탭** (F12 → Network → `generate` 요청 클릭 → Response)
4. **서버 터미널** (Flask 실행 중인 터미널 출력)

---

## 🔍 디버깅 체크리스트

### 백엔드 확인:
- [ ] Flask 서버 실행 중 (`python web/app.py`)
- [ ] 터미널에서 `✅ 썸네일 생성 완료` 메시지 확인
- [ ] `output/thumbnails/<session_id>/` 폴더에 PNG 파일 생성 확인

### 프론트엔드 확인:
- [ ] F12 → Console 탭에서 `📝 텍스트 수정 모드:` 로그 확인
- [ ] F12 → Console 탭에서 `✅ 백엔드 응답:` 로그 확인
- [ ] F12 → Network 탭에서 `generate` 요청 Status 200 확인
- [ ] F12 → Network 탭에서 `download` 요청 Status 200 확인

### 코드 확인:
- [ ] `web/static/js/thumbnail_studio.js:762-764` - YouTube URL 제외 로직
- [ ] `web/static/js/thumbnail_studio.js:813-856` - 응답 처리 로직
- [ ] `web/routes/thumbnail_routes.py:438-444` - 백엔드 응답 구조

---

## 💡 예상 시나리오별 결과

| 시나리오 | YouTube URL | 초기 썸네일 개수 | 텍스트 수정 후 | 예상 응답 |
|---------|-------------|-----------------|--------------|----------|
| 1 | ✅ 있음 | 3개 (프레임 추출) | 1개 (새 텍스트) | `count: 1, thumbnail_urls: [...]` |
| 2 | ❌ 없음 | 1개 (기본 배경) | 1개 (새 텍스트) | `count: 1, thumbnail_urls: [...]` |

---

## 📋 테스트 완료 보고 양식

테스트 완료 후 아래 내용을 작성하여 공유:

```
### 테스트 결과 보고

**날짜**: 2025-11-09
**테스트 시나리오**: [1 또는 2]

**결과**: [성공 / 실패]

**콘솔 로그**:
```
(여기에 콘솔 로그 복사)
```

**스크린샷**:
- 미리보기: [첨부]
- 콘솔: [첨부]
- (실패 시) 에러 메시지: [첨부]

**추가 메모**:
- (기타 특이사항)
```

---

**작성자**: Claude Code
**날짜**: 2025-11-09
**버전**: v1.0
