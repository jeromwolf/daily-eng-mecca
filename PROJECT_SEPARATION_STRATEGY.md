# 프로젝트 분리 전략
## Daily English Mecca + English News Digest

**작성일**: 2025-10-09
**목표**: 두 프로젝트 완전 분리 + 공통 모듈 재사용

---

## 📋 프로젝트 개요

### **1. Daily English Mecca** (기존)
- **포맷**: 9:16 세로 (Shorts)
- **길이**: 30초~1분
- **콘텐츠**: 영어 학습 문장 3개
- **타겟**: 짬내기 영어 학습자
- **채널**: Daily English Mecca

### **2. Tech News Digest** (신규)
- **포맷**: 16:9 가로 (일반 영상)
- **길이**: 3~5분
- **콘텐츠**: IT/Tech 뉴스 5개 (IT 60-80%, 경제 20-40%)
- **타겟**: IT 종사자, 개발자, 스타트업 관심층
- **채널**: Tech News Digest (신규)

---

## 🏗️ 분리 전략

### **옵션 1: 공통 패키지 방식** ⭐ (추천)

```
프로젝트 구조:

english-content-toolkit/        # 🔧 공통 라이브러리 (PyPI 패키지)
├── setup.py
├── english_toolkit/
│   ├── __init__.py
│   ├── ai/
│   │   ├── openai_client.py       # OpenAI 통합
│   │   ├── image_generator.py     # DALL-E 3
│   │   ├── tts_generator.py       # TTS
│   │   └── content_analyzer.py    # GPT 분석
│   │
│   ├── video/
│   │   ├── base_video_creator.py  # 추상 클래스
│   │   ├── shorts_creator.py      # 9:16 Shorts
│   │   └── standard_creator.py    # 16:9 일반
│   │
│   └── utils/
│       ├── resource_manager.py
│       ├── cache_manager.py
│       └── youtube_uploader.py
│
└── README.md


daily-english-mecca/            # 📚 영어 학습 (Shorts)
├── pyproject.toml
│   dependencies:
│     - english-content-toolkit>=1.0.0
│
├── src/
│   ├── sentence_generator.py      # 학습 문장 생성
│   ├── shorts_video_creator.py    # Shorts 전용 (9:16)
│   └── editor/                    # 에디터
│
└── web/
    └── app.py


tech-news-digest/               # 📰 IT/Tech 뉴스 (일반 영상)
├── pyproject.toml
│   dependencies:
│     - english-content-toolkit>=1.0.0
│
├── src/
│   ├── news/
│   │   ├── crawler.py             # 뉴스 크롤링
│   │   ├── summarizer.py          # 뉴스 요약
│   │   └── script_generator.py    # 앵커 스크립트
│   │
│   └── video/
│       └── news_video_creator.py  # 뉴스 영상 (16:9)
│
└── web/
    └── app.py
```

**장점:**
- ✅ 코드 중복 제로
- ✅ 버전 관리 용이 (toolkit v1.0.0, v1.1.0...)
- ✅ 각 프로젝트 독립적 개발
- ✅ 다른 프로젝트에도 재사용 가능

**단점:**
- ⚠️ 초기 설정 복잡

---

### **옵션 2: Git Submodule 방식**

```
shared-modules/                 # Git Submodule
├── image_generator.py
├── tts_generator.py
└── ...

daily-english-mecca/
├── shared-modules/  → submodule

tech-news-digest/
├── shared-modules/  → submodule
```

**장점:**
- ✅ Git으로 관리
- ✅ 동기화 쉬움

**단점:**
- ⚠️ Submodule 복잡함
- ⚠️ 충돌 가능성

---

### **옵션 3: 심볼릭 링크**

```
daily-english-mecca/
├── src/common/ → ../../common/

tech-news-digest/
├── src/common/ → ../../common/

common/  (별도 폴더)
```

**장점:**
- ✅ 간단

**단점:**
- ❌ OS 의존적
- ❌ 버전 관리 어려움

---

## 🎯 추천: 공통 패키지 방식

### **단계별 실행 계획**

#### **Phase 1: 공통 패키지 생성 (1일)**

```bash
# 1. 패키지 프로젝트 생성
mkdir english-content-toolkit
cd english-content-toolkit

# 2. 구조 생성
mkdir -p english_toolkit/{ai,video,utils}
touch english_toolkit/__init__.py

# 3. setup.py 작성
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="english-content-toolkit",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "moviepy>=2.0.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
    ],
    author="Kelly",
    description="Common toolkit for English learning video generation",
    python_requires=">=3.11",
)
EOF

# 4. 로컬 설치
pip install -e .
```

#### **Phase 2: 기존 코드 마이그레이션 (1일)**

```bash
# daily-english-mecca에서 공통 모듈 추출
cp src/image_generator.py ../english-content-toolkit/english_toolkit/ai/
cp src/tts_generator.py ../english-content-toolkit/english_toolkit/ai/
cp src/content_analyzer.py ../english-content-toolkit/english_toolkit/ai/
cp src/resource_manager.py ../english-content-toolkit/english_toolkit/utils/

# daily-english-mecca에서 패키지 사용
# src/video_creator.py
from english_toolkit.ai import ImageGenerator, TTSGenerator
from english_toolkit.utils import ResourceManager
```

#### **Phase 3: 뉴스 프로젝트 생성 (1일)**

```bash
# 1. 새 프로젝트 생성
mkdir tech-news-digest
cd tech-news-digest

# 2. 구조 생성
mkdir -p src/{news,video}
mkdir -p web/{templates,static}

# 3. pyproject.toml 작성
cat > pyproject.toml << 'EOF'
[project]
name = "tech-news-digest"
version = "1.0.0"
dependencies = [
    "english-content-toolkit>=1.0.0",
    "fastapi>=0.104.0",
    "feedparser>=6.0.0",  # RSS 파싱
    "beautifulsoup4>=4.12.0",  # HTML 파싱
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
]
EOF

# 4. 공통 패키지 설치
pip install -e ../english-content-toolkit
pip install -e .
```

---

## 📦 공통 패키지 API 설계

### **1. AI 모듈**

```python
# english_toolkit/ai/image_generator.py

from abc import ABC, abstractmethod

class BaseImageGenerator(ABC):
    """이미지 생성 추상 클래스"""

    @abstractmethod
    def generate_image(self, prompt: str, size: str) -> str:
        """이미지 생성"""
        pass


class DALLEImageGenerator(BaseImageGenerator):
    """DALL-E 3 구현"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt: str, size: str = "1024x1792") -> str:
        """
        DALL-E 3로 이미지 생성

        Args:
            prompt: 이미지 프롬프트
            size: "1024x1792" (세로) 또는 "1792x1024" (가로)

        Returns:
            이미지 파일 경로
        """
        # 구현...
```

### **2. 비디오 모듈**

```python
# english_toolkit/video/base_video_creator.py

class BaseVideoCreator(ABC):
    """비디오 생성 추상 클래스"""

    def __init__(self, format: str):
        self.format = format  # "shorts" or "standard"
        self.width, self.height = self._get_dimensions()

    def _get_dimensions(self) -> tuple[int, int]:
        if self.format == "shorts":
            return (1080, 1920)  # 9:16
        elif self.format == "standard":
            return (1920, 1080)  # 16:9
        else:
            raise ValueError(f"Unknown format: {self.format}")

    @abstractmethod
    def create_video(self, clips: list, output_path: str) -> str:
        """비디오 생성"""
        pass


# english_toolkit/video/shorts_creator.py

class ShortsVideoCreator(BaseVideoCreator):
    """Shorts 전용 (9:16)"""

    def __init__(self):
        super().__init__(format="shorts")

    def create_video(self, clips: list, output_path: str) -> str:
        # Shorts 특화 로직
        pass


# english_toolkit/video/standard_creator.py

class StandardVideoCreator(BaseVideoCreator):
    """일반 영상 (16:9)"""

    def __init__(self):
        super().__init__(format="standard")

    def create_video(self, clips: list, output_path: str) -> str:
        # 일반 영상 로직
        pass
```

---

## 🔄 사용 예시

### **Daily English Mecca에서 사용**

```python
# daily-english-mecca/src/video_creator.py

from english_toolkit.ai import DALLEImageGenerator, OpenAITTS
from english_toolkit.video import ShortsVideoCreator
from english_toolkit.utils import ResourceManager

class DailyEnglishVideoCreator:
    """Daily English Mecca 전용 비디오 생성"""

    def __init__(self):
        # 공통 모듈 사용
        self.image_gen = DALLEImageGenerator(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = OpenAITTS(api_key=os.getenv("OPENAI_API_KEY"))
        self.video_creator = ShortsVideoCreator()  # 9:16 Shorts
        self.resource_mgr = ResourceManager(base_dir="output")

    def create_learning_video(self, sentences: list[str]) -> str:
        # 이미지 생성 (세로)
        images = [self.image_gen.generate_image(s, size="1024x1792") for s in sentences]

        # TTS 생성
        audio = [self.tts.generate_speech(s) for s in sentences]

        # Shorts 영상 합성 (9:16)
        return self.video_creator.create_video(
            clips=self._prepare_clips(images, audio),
            output_path="output/videos/daily_english.mp4"
        )
```

### **Tech News Digest에서 사용**

```python
# tech-news-digest/src/video/news_video_creator.py

from english_toolkit.ai import DALLEImageGenerator, OpenAITTS
from english_toolkit.video import StandardVideoCreator  # 16:9
from english_toolkit.utils import ResourceManager

class NewsVideoCreator:
    """뉴스 다이제스트 전용 비디오 생성"""

    def __init__(self):
        # 같은 공통 모듈 사용
        self.image_gen = DALLEImageGenerator(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = OpenAITTS(api_key=os.getenv("OPENAI_API_KEY"))
        self.video_creator = StandardVideoCreator()  # 16:9 일반 영상
        self.resource_mgr = ResourceManager(base_dir="output")

    def create_news_video(self, news_list: list[dict]) -> str:
        # 이미지 생성 (가로)
        images = [self.image_gen.generate_image(n['headline'], size="1792x1024") for n in news_list]

        # 앵커 TTS 생성
        audio = [self.tts.generate_speech(n['script']) for n in news_list]

        # 일반 영상 합성 (16:9)
        return self.video_creator.create_news_video(
            news_clips=self._prepare_news_clips(news_list, images, audio),
            output_path="output/videos/news_digest.mp4"
        )
```

---

## 📊 버전 관리 전략

### **Semantic Versioning**

```
english-content-toolkit
├── v1.0.0 - 초기 릴리스 (이미지, TTS, 기본 비디오)
├── v1.1.0 - 뉴스 기능 추가 (앵커 스크립트, 레이아웃)
├── v1.2.0 - 멀티 음성 지원
└── v2.0.0 - 메이저 업데이트 (API 변경)
```

### **의존성 관리**

```toml
# daily-english-mecca/pyproject.toml
[project]
dependencies = [
    "english-content-toolkit>=1.0.0,<2.0.0",  # 1.x 버전만
]

# tech-news-digest/pyproject.toml
[project]
dependencies = [
    "english-content-toolkit>=1.1.0,<2.0.0",  # 뉴스 기능 필요
]
```

---

## 🚀 실행 순서

### **Week 1: 공통 패키지 구축**
1. [x] 설계 문서 완성
2. [ ] `english-content-toolkit` 프로젝트 생성
3. [ ] 기존 코드에서 공통 모듈 추출
4. [ ] 로컬 패키지 설치 및 테스트

### **Week 2: Daily English Mecca 리팩토링**
1. [ ] 공통 패키지 의존성 추가
2. [ ] Import 경로 변경
3. [ ] 테스트 및 검증

### **Week 3: Tech News Digest 구축**
1. [ ] 새 프로젝트 생성
2. [ ] 뉴스 크롤러 구현
3. [ ] 16:9 영상 생성 시스템 구현

### **Week 4: 통합 테스트**
1. [ ] 두 프로젝트 동시 실행
2. [ ] 버그 수정
3. [ ] 문서 업데이트

---

## 💡 핵심 원칙

### **1. 독립성**
- 각 프로젝트는 독립적으로 실행 가능
- 공통 패키지에만 의존

### **2. 확장성**
- 새 프로젝트 추가 시 공통 패키지 재사용
- 예: Japanese News Digest, Chinese Learning Shorts

### **3. 버전 안정성**
- 공통 패키지 변경 시 하위 호환성 유지
- 메이저 버전 업데이트는 신중하게

### **4. 테스트**
- 공통 패키지에 유닛 테스트 필수
- 각 프로젝트는 통합 테스트

---

**이 전략으로 진행하시겠습니까?** 🎯

다음 단계:
1. 공통 패키지 프로젝트 생성
2. 기존 코드 마이그레이션
3. 뉴스 프로젝트 구축

바로 시작할까요?
