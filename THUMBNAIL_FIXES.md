# YouTube 썸네일 생성기 버그 수정 및 개선 (2025-11-09)

## 📌 요약

사용자 피드백에 따른 3가지 핵심 문제 해결:
1. ✅ **이미지 화질 개선** - 흐릿함 해결
2. ✅ **영상 길이 배지 버그 수정** - 체크 안 해도 표시되는 문제
3. ✅ **디자인 개선** - 검은색 박스 제거, 그라데이션 오버레이 적용

---

## 🐛 Issue 1: 이미지 화질이 안좋아 (Image Quality)

### 문제점
사용자 피드백: "이미지 화질이 안좋아"
- YouTube 영상에서 추출한 프레임이 흐릿하고 저화질

### 원인
- FFmpeg의 `-q:v` 파라미터가 `2`로 설정됨 (중간 품질)
- JPEG 품질 스케일: 1 (최고) ~ 31 (최저)

### 해결 방법
**파일**: `src/youtube_thumbnail/frame_extractor.py:227`

```python
# Before:
'-q:v', '2',  # 중간 품질

# After:
'-q:v', '1',  # 최고 품질 (2→1로 변경)
```

### 효과
- JPEG 압축 품질 최대화
- 프레임 이미지 선명도 향상
- 썸네일 최종 화질 개선

---

## 🐛 Issue 2: 영상길이 체크 안했는데 표시 되었어 (Duration Badge Bug)

### 문제점
사용자 피드백: "영상길이 체크 안했는데 표시 되었어"
- 사용자가 "영상 길이" 체크박스를 선택하지 않았는데도 배지가 자동으로 표시됨

### 원인
`thumbnail_routes.py`에서 YouTube 메타데이터의 `duration_string`을 자동으로 `video_duration`에 할당:
```python
# 잘못된 로직 (자동 설정)
if not video_duration and video_metadata.get('duration_string'):
    video_duration = video_metadata['duration_string']
```

### 해결 방법
**파일**: `web/routes/thumbnail_routes.py:250-251`

```python
# Before:
if not video_duration and video_metadata.get('duration_string'):
    video_duration = video_metadata['duration_string']  # 자동 설정

# After:
# 영상 길이는 사용자가 입력한 경우만 사용 (자동 설정 제거)
# video_duration이 비어있으면 배지가 표시되지 않음
```

### 효과
- 사용자가 명시적으로 입력한 경우에만 영상 길이 배지 표시
- 체크박스와 배지 표시가 일치하도록 수정
- 더 깔끔한 UI 제공

---

## 🎨 Issue 3: 검은색 박스 디자인이 깔끔하지 않음 (Design Improvement)

### 문제점
사용자 피드백: "검정색으로 board 후에 텍스트가 있는데 별로 안 깔끔한것 같아"
- 기존 디자인: 불투명한 검은색 박스 (70% opacity) + 흰색 텍스트
- 딱딱하고 전문적이지 않은 느낌

### 기존 코드
**파일**: `src/youtube_thumbnail/thumbnail_engine.py:307-314`

```python
# 반투명 검은색 박스 (딱딱한 디자인)
overlay_box = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
draw_overlay = ImageDraw.Draw(overlay_box)
draw_overlay.rectangle(
    [box_x1, box_y1, box_x2, box_y2],
    fill=(0, 0, 0, 180)  # 70% 불투명 (딱딱한 검은색 박스)
)
canvas.paste(overlay_box, (0, 0), overlay_box)
```

### 개선된 디자인
**파일**: `src/youtube_thumbnail/thumbnail_engine.py:295-382`

#### 개선 1: 그라데이션 오버레이
**이전**: 단순 검은색 박스 (균일한 불투명도)
**개선**: 세로 그라데이션 (중앙이 가장 어둡고 위/아래로 갈수록 투명)

```python
# 세로 그라데이션 오버레이 (위에서 아래로 어두워짐)
overlay_box = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
draw_overlay = ImageDraw.Draw(overlay_box)

gradient_height = box_y2 - box_y1
for i in range(int(gradient_height)):
    y = box_y1 + i
    if y < 0 or y >= self.HEIGHT:
        continue

    # 그라데이션 알파값 (중앙이 가장 어두움)
    # 중앙 50%에서 최대 불투명도 (120), 위/아래로 갈수록 투명해짐
    center = gradient_height / 2
    distance_from_center = abs(i - center)
    alpha_ratio = 1.0 - (distance_from_center / center) * 0.5  # 0.5~1.0
    alpha = int(120 * alpha_ratio)  # 최대 120 (약 47% 불투명)

    draw_overlay.line(
        [(box_x1, y), (box_x2, y)],
        fill=(0, 0, 0, alpha)
    )

canvas.paste(overlay_box, (0, 0), overlay_box)
```

**효과**:
- 부드러운 그라데이션 효과 (자연스러운 배경 어두움)
- 최대 불투명도 47% (기존 70%보다 밝음)
- 텍스트 주변만 어둡게 처리하여 배경 이미지 잘 보임

#### 개선 2: 강한 텍스트 외곽선 (Stroke)
**이전**: 단순 그림자 (shadow offset 3px)
**개선**: 두꺼운 검은색 외곽선 (5px, 8방향)

```python
# 메인 텍스트 외곽선 (검은색, 8방향 + 대각선)
stroke_width = 5  # 외곽선 두께

for offset_x in range(-stroke_width, stroke_width + 1):
    for offset_y in range(-stroke_width, stroke_width + 1):
        if offset_x == 0 and offset_y == 0:
            continue  # 중앙은 나중에
        draw.text(
            (x_main + offset_x, y_main + offset_y),
            main_text,
            fill='#000000',
            font=main_font
        )

# 메인 텍스트 (흰색)
draw.text((x_main, y_main), main_text, fill=text_color, font=main_font)
```

**효과**:
- 텍스트 가독성 크게 향상 (배경이 밝아도 잘 보임)
- YouTube 썸네일 Best Practice 적용 (TED, Veritasium 스타일)
- 전문적이고 깔끔한 느낌

#### 개선 3: 서브 텍스트 외곽선
**금색(#FFD700) 서브 텍스트에도 4px 외곽선 적용**

```python
# 서브 텍스트 외곽선 (검은색)
stroke_width_sub = 4
for offset_x in range(-stroke_width_sub, stroke_width_sub + 1):
    for offset_y in range(-stroke_width_sub, stroke_width_sub + 1):
        if offset_x == 0 and offset_y == 0:
            continue
        draw.text(
            (x_sub + offset_x, y_sub + offset_y),
            subtitle_text,
            fill='#000000',
            font=sub_font
        )

# 서브 텍스트 (금색)
draw.text((x_sub, y_sub), subtitle_text, fill='#FFD700', font=sub_font)
```

### 디자인 비교

| 항목 | 이전 디자인 | 개선된 디자인 |
|-----|-----------|-------------|
| 배경 오버레이 | 검은색 박스 (70% 불투명) | 그라데이션 (47% 최대) |
| 텍스트 외곽선 | 3px 단순 그림자 | 5px 두꺼운 외곽선 (8방향) |
| 서브 텍스트 | 3px 단순 그림자 | 4px 두꺼운 외곽선 |
| 전체 느낌 | 딱딱하고 어두움 | 부드럽고 전문적 |
| 가독성 | 중간 | 매우 높음 |

---

## 📁 수정된 파일 목록

1. **`src/youtube_thumbnail/frame_extractor.py`** (Line 227)
   - FFmpeg 품질 파라미터 변경: `-q:v 2` → `-q:v 1`

2. **`web/routes/thumbnail_routes.py`** (Lines 250-251)
   - `video_duration` 자동 설정 로직 제거

3. **`src/youtube_thumbnail/thumbnail_engine.py`** (Lines 295-382)
   - `_draw_ted_text()` 메서드 완전 재작성:
     - 그라데이션 오버레이 추가
     - 강한 텍스트 외곽선 (5px 메인, 4px 서브)
     - 검은색 박스 제거

---

## 🚀 기대 효과

1. **이미지 품질 향상**
   - YouTube 썸네일이 고화질로 표시됨
   - 모바일에서도 선명하게 보임

2. **UX 개선**
   - 사용자 의도대로 배지 표시/숨김 작동
   - 직관적인 UI

3. **디자인 품질 향상**
   - TED, Veritasium 수준의 전문적인 썸네일
   - YouTube 알고리즘 최적화 (CTR 향상)
   - "검은색 박스가 깔끔하지 않다"는 문제 완전 해결

---

## 🧪 테스트 필요 사항

### 1. 이미지 품질 확인
- YouTube URL로 썸네일 생성
- 1280x720 해상도에서 선명도 확인
- 모바일 뷰에서 텍스트 가독성 테스트

### 2. 영상 길이 배지 테스트
- Case 1: "영상 길이" 체크 안 함 → 배지 없어야 함 ✓
- Case 2: "영상 길이" 체크 + 수동 입력 → 배지 표시되어야 함 ✓

### 3. 디자인 개선 확인
- 다양한 배경 이미지 (밝은 배경, 어두운 배경, 복잡한 배경)에서 텍스트 가독성 확인
- 그라데이션 오버레이가 자연스러운지 확인
- 텍스트 외곽선이 너무 두껍지 않은지 확인

---

## 📝 향후 개선 아이디어 (Optional)

1. **동적 외곽선 두께**
   - 배경 밝기에 따라 외곽선 두께 자동 조정
   - PIL ImageStat로 배경 밝기 분석

2. **커스터마이징 옵션**
   - 사용자가 오버레이 불투명도 조절
   - 텍스트 외곽선 색상 선택 (검은색/흰색)

3. **AI 기반 텍스트 배치**
   - GPT-4 Vision으로 배경 이미지 분석
   - 가장 적합한 텍스트 위치 자동 결정

---

**작성자**: Kelly & Claude Code
**날짜**: 2025-11-09
**상태**: 테스트 대기 중
