"""
유튜브 메타정보 자동 생성 모듈
"""
import os
import json
from openai import OpenAI
from pathlib import Path


class YouTubeMetadataGenerator:
    def __init__(self, api_key: str = None):
        """
        YouTubeMetadataGenerator 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate_metadata(self, sentences: list[str]) -> dict:
        """
        영어 문장들로부터 유튜브 메타정보 생성

        Args:
            sentences: 영어 문장 리스트

        Returns:
            유튜브 메타정보 딕셔너리
            {
                'title': str,
                'description': str,
                'tags': list[str],
                'category': str
            }
        """
        try:
            print("유튜브 메타정보 생성 중...")

            # GPT를 사용하여 메타정보 생성
            prompt = self._create_metadata_prompt(sentences)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a top-performing YouTube Shorts creator specializing in English education content for Korean learners.
You understand:
- YouTube algorithm optimization (CTR, watch time, engagement)
- Korean learning culture and trending topics
- SEO best practices for educational content
- How to write compelling, clickable titles that drive views
- Effective use of hashtags and tags for discoverability

Your metadata consistently generates high CTR (>10%) and strong engagement."""},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8  # 더 창의적인 제목과 설명
            )

            metadata = json.loads(response.choices[0].message.content)

            print("✓ 유튜브 메타정보 생성 완료")
            return metadata

        except Exception as e:
            print(f"✗ 메타정보 생성 실패: {e}")
            # 기본 메타정보 반환
            return self._create_default_metadata(sentences)

    def _create_metadata_prompt(self, sentences: list[str]) -> str:
        """
        메타정보 생성을 위한 프롬프트 생성

        Args:
            sentences: 영어 문장 리스트

        Returns:
            GPT 프롬프트
        """
        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        num_sentences = len(sentences)

        prompt = f"""Given these {num_sentences} English sentences for a YouTube Shorts daily learning video:

{sentences_text}

Generate YouTube metadata in JSON format optimized for maximum views and engagement:

{{
    "title": "Highly engaging title in Korean (80-100 characters)",
    "description": "Comprehensive description in Korean with hashtags and timestamps",
    "tags": ["30+ relevant tags in Korean and English for SEO"],
    "category": "Education",
    "hashtags": ["list of 15-20 relevant hashtags without # symbol"]
}}

📌 TITLE REQUIREMENTS (80-100 characters):
- Use proven clickbait formulas: "이거 모르면 손해", "원어민처럼 말하는 비법", "99% 틀리는 표현"
- Include numbers and specificity: "하루 3분", "3문장으로", "30초 만에"
- Use emotional words: "꿀팁", "필수", "진짜", "레전드"
- Include target keywords: 영어회화, 일상영어, 영어표현, 원어민
- Examples: "진짜 원어민은 이렇게 말해요 🔥 일상영어 3문장 | Daily English"

📝 DESCRIPTION REQUIREMENTS:
1. Hook line (1-2 sentences) - Why this video matters
2. Sentence breakdown with Korean translations:
   0:00 Intro
   0:03 Sentence 1: [English] - [Korean translation]
   0:08 Sentence 2: [English] - [Korean translation]
   0:13 Sentence 3: [English] - [Korean translation]
3. Learning tips (2-3 sentences about usage)
4. Call to action (subscribe + like + notification)
5. Social media links (if applicable)
6. 15-20 hashtags at the end (with # symbol)

🏷️ TAGS REQUIREMENTS (30+ tags):
- Mix Korean and English tags
- Include:
  * Main keywords: 영어회화, 영어공부, 일상영어, 영어표현, 영어듣기
  * Long-tail keywords: 원어민영어표현, 미국영어회화, 영어쇼츠
  * English keywords: English conversation, daily English, learn English, English speaking
  * Trending: 쇼츠, shorts, 영어공부법, 영어독학
- Use both singular and variations

💡 HASHTAGS REQUIREMENTS (15-20 hashtags, without # symbol):
- Most popular: 영어회화, 영어공부, 일상영어, 영어쇼츠, 영어표현
- Trending: 영어듣기, 원어민영어, 영어회화공부, 영어독학, 영어회화표현
- English: LearnEnglish, EnglishConversation, DailyEnglish, EnglishLearning
- Niche: 쉬운영어, 기초영어, 여행영어 (if applicable)

Make the metadata feel authentic, valuable, and optimized for YouTube algorithm."""
        return prompt

    def _create_default_metadata(self, sentences: list[str]) -> dict:
        """
        기본 메타정보 생성 (GPT 실패 시)

        Args:
            sentences: 영어 문장 리스트

        Returns:
            기본 메타정보
        """
        num_sentences = len(sentences)

        return {
            "title": f"진짜 원어민은 이렇게 말해요 🔥 일상영어 {num_sentences}문장 | Daily English Mecca",
            "description": f"""🎯 원어민처럼 말하고 싶다면 이 {num_sentences}문장은 필수!

⏰ 타임스탬프:
0:00 인트로
{chr(10).join([f'0:{(i+1)*3:02d} {s}' for i, s in enumerate(sentences)])}

📚 오늘의 핵심 표현:
{chr(10).join([f'{i+1}. {s}' for i, s in enumerate(sentences)])}

💡 이런 상황에서 써보세요:
이 표현들은 일상생활에서 정말 자주 쓰이는 필수 영어입니다.
원어민 친구들과 대화할 때, 해외여행 갈 때 바로 써먹을 수 있어요!

✅ 학습 팁:
1. 소리내서 3번씩 따라 읽기
2. 상황을 상상하며 연습하기
3. 오늘 배운 표현 하나라도 실제로 사용해보기

👍 이 영상이 도움되셨다면 좋아요 & 구독 부탁드려요!
🔔 알림 설정하고 매일 새로운 영어 표현 받아보세요!
💬 댓글로 오늘 배운 문장 써보기 챌린지!

📱 Daily English Mecca와 함께 영어 정복하세요!

#영어회화 #영어공부 #일상영어 #영어쇼츠 #영어표현 #영어듣기 #원어민영어 #영어회화공부 #영어독학 #영어공부법 #쉬운영어 #기초영어 #영어발음 #영어스피킹 #LearnEnglish #EnglishConversation #DailyEnglish #EnglishLearning #SpeakEnglish""",
            "tags": [
                # 한글 주요 키워드
                "영어회화", "영어공부", "일상영어", "영어표현", "영어듣기",
                "원어민영어", "영어회화공부", "영어독학", "영어쇼츠", "영어숏츠",
                "영어공부법", "쉬운영어", "기초영어", "영어발음", "영어스피킹",
                "미국영어", "영어회화표현", "영어학습", "영어배우기", "영어마스터",
                # 영어 키워드
                "English conversation", "Daily English", "Learn English", "English speaking",
                "English learning", "Speak English", "English phrases", "English practice",
                "American English", "ESL", "English tutorial", "English lesson",
                # 쇼츠/숏폼 관련
                "쇼츠", "shorts", "영어shorts", "English shorts",
                # 롱테일 키워드
                "원어민처럼말하기", "영어자연스럽게", "영어꿀팁"
            ],
            "category": "Education",
            "hashtags": [
                "영어회화", "영어공부", "일상영어", "영어쇼츠", "영어표현",
                "영어듣기", "원어민영어", "영어회화공부", "영어독학", "영어회화표현",
                "영어공부법", "쉬운영어", "기초영어", "영어발음", "영어스피킹",
                "LearnEnglish", "EnglishConversation", "DailyEnglish", "EnglishLearning", "SpeakEnglish"
            ]
        }

    def save_metadata(self, metadata: dict, output_path: str) -> str:
        """
        메타정보를 JSON 파일로 저장

        Args:
            metadata: 메타정보 딕셔너리
            output_path: 저장 경로

        Returns:
            저장된 파일 경로
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✓ 메타정보 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ 메타정보 저장 실패: {e}")
            raise

    def print_metadata(self, metadata: dict):
        """
        메타정보를 보기 좋게 출력

        Args:
            metadata: 메타정보 딕셔너리
        """
        print("\n" + "="*60)
        print("📺 유튜브 메타정보")
        print("="*60)
        print(f"\n📌 제목:\n{metadata.get('title', 'N/A')}")
        print(f"\n📝 설명:\n{metadata.get('description', 'N/A')}")
        print(f"\n🏷️  태그:\n{', '.join(metadata.get('tags', []))}")
        print(f"\n📂 카테고리: {metadata.get('category', 'N/A')}")
        print("="*60 + "\n")
