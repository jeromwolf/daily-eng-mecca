# Daily English Mecca 🌟

> 하루 3문장 영어 학습 유튜브 쇼츠를 자동으로 생성하는 AI 프로그램

매일 3개의 영어 문장만 입력하면, AI가 자동으로 이미지를 생성하고, 음성을 만들고, 전문적인 유튜브 쇼츠 영상을 제작합니다!

---

## ✨ 주요 기능

- 🎨 **AI 이미지 생성**: OpenAI DALL-E 3로 문장에 맞는 고품질 이미지 자동 생성
- 🗣️ **자연스러운 음성**: OpenAI TTS로 원어민 수준의 발음 제공 (3가지 음성 교체)
- 🎵 **프로 사운드 시스템**: 18종 효과음 + 무료 배경음악 자동 적용
- 🎬 **자동 비디오 편집**: 이미지, 텍스트, 음성을 조합하여 유튜브 쇼츠 생성
- 📊 **유튜브 최적화**: 제목, 설명, 태그 자동 생성으로 구독자 증가 유도
- ⚡ **빠른 제작**: 영상 1개당 3분 이내 자동 생성

---

## 🎯 이런 분들에게 추천합니다

- 영어 학습 콘텐츠 크리에이터
- 유튜브 쇼츠를 시작하려는 분
- 매일 영어 콘텐츠를 만들고 싶지만 시간이 부족한 분
- AI 도구로 콘텐츠 제작을 자동화하고 싶은 분

---

## 📋 요구사항

### 필수
- Python 3.8 이상
- OpenAI API 키 ([발급 방법](#openai-api-키-발급))
- 인터넷 연결

### 선택 (성능 향상)
- FFmpeg (비디오 인코딩 최적화)

---

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd daily-english-mecca
```

### 2. 가상환경 생성 (권장)

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 입력하세요:

```bash
OPENAI_API_KEY=your_api_key_here
```

---

## 📖 사용 방법

### 기본 사용

```bash
python main.py
```

프로그램이 실행되면 3개의 영어 문장을 입력하세요:

```
📝 오늘의 3문장을 입력해주세요:

문장 1: I'm going to spend time with family.
문장 2: I plan to hang out with my loved ones.
문장 3: I prefer to have some alone time.
```

### 실행 과정

프로그램은 다음 단계를 자동으로 수행합니다:

1. ✅ 문장 분석 (관련성 파악 및 이미지 개수 결정)
2. ✅ 이미지 생성 (DALL-E 3)
3. ✅ 음성 생성 (OpenAI TTS)
4. ✅ 비디오 생성 (MoviePy)
5. ✅ 유튜브 메타정보 생성

### 결과물

완료되면 다음 파일들이 생성됩니다:

```
output/
├── videos/
│   └── daily_english_20251005_143022.mp4    # 유튜브 쇼츠 영상
├── metadata/
│   └── metadata_20251005_143022.json        # 유튜브 메타정보
├── images/
│   └── 20251005_143022/
│       ├── image_1.png
│       └── image_2.png
└── audio/
    └── 20251005_143022/
        └── speech.mp3
```

---

## 🎬 비디오 구성

생성되는 유튜브 쇼츠는 다음과 같이 구성됩니다:

1. **인트로 (2초)**: "오늘의 3문장 / Daily English"
2. **메인 콘텐츠 (15-25초)**: 각 문장마다
   - AI 생성 배경 이미지
   - 큰 글씨로 영어 문장 표시
   - 자연스러운 원어민 발음
3. **아웃트로 (2초)**: "구독하고 매일 3문장 배우기!" + 좋아요/구독 아이콘

**총 길이**: 20-30초 (유튜브 쇼츠 최적화)

---

## 📊 유튜브 메타정보

자동으로 생성되는 메타정보 예시:

**제목**:
```
매일 3문장 영어회화 | 가족과 함께하는 시간 표현 🌟
```

**설명**:
```
🌟 하루 3문장으로 영어 마스터하기!

📝 오늘의 문장:
1. I'm going to spend time with family.
   → 나는 가족과 시간을 보낼 거예요.
2. I plan to hang out with my loved ones.
   → 나는 사랑하는 사람들과 어울릴 계획이에요.
3. I prefer to have some alone time.
   → 나는 혼자만의 시간을 갖는 것을 선호해요.

👍 좋아요와 구독 부탁드립니다!
🔔 알림 설정하고 매일 새로운 표현을 받아보세요!

#영어회화 #영어공부 #일상영어 #EnglishLearning
```

**태그**:
```
영어회화, 영어공부, 일상영어, 영어표현, English, Daily English,
Learn English, 영어쇼츠, 영어숏츠, 영어배우기
```

---

## 💰 비용 안내

OpenAI API 사용 비용 (2025년 1월 기준):

| 항목 | 비용 | 영상 1개당 |
|------|------|-----------|
| DALL-E 3 이미지 | $0.04/개 | ~$0.08 (2개) |
| TTS 음성 | $0.015/1K 문자 | ~$0.01 |
| GPT-4o-mini | $0.15/1M tokens | ~$0.01 |
| **합계** | - | **~$0.10** |

**월간 예상 비용**:
- 1일 1개 영상: ~$3/월
- 1일 5개 영상: ~$15/월
- 1일 10개 영상: ~$30/월

---

## 🔑 OpenAI API 키 발급

1. https://platform.openai.com/api-keys 접속
2. 로그인 또는 회원가입
3. "Create new secret key" 클릭
4. 생성된 키 복사 (한 번만 표시됩니다!)
5. `.env` 파일에 키 입력

**⚠️ 중요**: API를 사용하려면 결제 정보 등록 필요
- https://platform.openai.com/settings/organization/billing
- 최소 $5 충전 권장

---

## 🛠 프로젝트 구조

```
daily-english-mecca/
├── src/
│   ├── __init__.py
│   ├── image_generator.py       # DALL-E 이미지 생성
│   ├── tts_generator.py          # TTS 음성 생성
│   ├── content_analyzer.py       # 문장 분석
│   ├── youtube_metadata.py       # 메타정보 생성
│   ├── video_creator.py          # 비디오 생성
│   └── audio/                    # 🆕 사운드 시스템
│       ├── effects/              # 효과음 생성기 (18종)
│       │   ├── base_effect.py    # 추상 클래스
│       │   ├── ui_sounds.py      # UI 효과음 (6종)
│       │   ├── learning_sounds.py # 학습 효과음 (6종)
│       │   └── transition_sounds.py # 전환 효과음 (6종)
│       ├── music/                # 배경음악 관리
│       │   └── music_library.py  # Kevin MacLeod 무료 음악
│       ├── presets/              # 사운드 프리셋
│       │   └── daily_english.py  # 4가지 프리셋
│       └── sound_library.py      # 통합 인터페이스
├── output/                       # 생성된 파일
├── web/                          # Flask 웹 인터페이스
├── test_sound_system.py          # 사운드 시스템 테스트
├── main.py                       # 메인 실행 파일
├── requirements.txt              # 패키지 목록
├── .env.example                  # 환경변수 예시
├── PRD.md                        # 제품 요구사항 명세서
├── TASKS.md                      # 개발 태스크 목록
└── README.md                     # 이 파일
```

---

## 🎨 커스터마이징

### 음성 변경

`src/tts_generator.py`에서 음성을 변경할 수 있습니다:

```python
# 사용 가능한 음성: alloy, echo, fable, onyx, nova, shimmer
voice = "nova"  # 기본값: nova (여성, 부드러운 톤)
```

### 비디오 스타일 변경

`src/video_creator.py`에서 색상, 폰트, 레이아웃 등을 수정할 수 있습니다.

---

## 🎵 사운드 시스템 (NEW!)

### 효과음 (18종) - numpy 기반 생성

**UI 효과음 (6종)**
- `click`, `hover`, `notification`, `error`, `success`, `toggle`

**학습 효과음 (6종)**
- `correct`, `wrong`, `celebration`, `encouragement`, `start`, `finish`

**전환 효과음 (6종)**
- `whoosh`, `swipe`, `pop`, `slide`, `fade`, `page_turn`

### 배경음악 (4 무드) - Kevin MacLeod (CC BY 4.0)

- **energetic**: Happy Alley (110초)
- **calm**: Carefree (205초)
- **upbeat**: Fluffing a Duck (150초)
- **focus**: Deliberate Thought (152초)

### 프리셋 (4종)

1. **daily_english**: 영어 학습 비디오 기본
2. **quiz**: 퀴즈 모드
3. **interactive**: 웹 UI 인터랙션
4. **calm_learning**: 차분한 학습

### 사용 방법

```python
from src.audio.sound_library import SoundLibrary

# 라이브러리 초기화
library = SoundLibrary()

# 효과음 생성
click_sound = library.get_effect('click')
correct_sound = library.get_effect('correct')

# 배경음악 다운로드
music = library.get_background_music(mood='energetic')

# 프리셋 적용 (자주 사용하는 조합)
sounds = library.apply_preset('daily_english')
```

### 사운드 시스템 테스트

```bash
python test_sound_system.py
```

모든 효과음과 배경음악이 정상적으로 생성되는지 확인할 수 있습니다.

---

## ❓ 문제 해결 (Troubleshooting)

### 1. API 키 오류

```
❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결**: `.env` 파일을 생성하고 API 키를 입력하세요.

### 2. MoviePy 오류

```
MoviePy Error: ...
```

**해결**: FFmpeg 설치
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# https://ffmpeg.org/download.html에서 다운로드
```

### 3. 이미지 생성 실패

**원인**: API 크레딧 부족 또는 네트워크 오류

**해결**:
- OpenAI 대시보드에서 크레딧 확인
- 인터넷 연결 확인

---

## 🚀 향후 계획

- [x] **프로 사운드 시스템 (완료!)** - 18종 효과음 + 무료 배경음악
- [x] **웹 UI 개발 (완료!)** - Flask 기반 비디오 편집 인터페이스
- [x] **커스텀 인트로/아웃트로 (완료!)** - 비디오별 배경 이미지 생성 기능
- [ ] 배치 처리 (CSV 파일로 여러 영상 한번에 생성)
- [ ] 유튜브 자동 업로드
- [ ] 다양한 템플릿 지원
- [ ] 한국어 자막 자동 생성
- [ ] 성과 분석 대시보드

---

## 📄 라이선스

MIT License

---

## 🤝 기여하기

이슈와 PR은 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 문의

문제가 있거나 제안사항이 있다면 이슈를 생성해주세요!

---

**Made with ❤️ for English Learners**

*하루 3문장으로 영어 정복하세요!* 🚀
