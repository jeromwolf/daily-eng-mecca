"""
OpenAI GPT를 사용한 문장 자동 생성 모듈
"""
import os
from openai import OpenAI


class SentenceGenerator:
    def __init__(self, api_key: str = None):
        """
        SentenceGenerator 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate_theme_sentences(self, theme: str, theme_detail: str = "") -> list[str]:
        """
        주제별 3~6문장 자동 생성 (내용에 따라 가변)

        Args:
            theme: 주제 (travel, business, daily, restaurant, shopping, health, hobby, study)
            theme_detail: 추가 설명 (선택사항)

        Returns:
            생성된 3~6개의 영어 문장 리스트
        """
        # 주제별 설명
        theme_descriptions = {
            "travel": "Travel and tourism",
            "business": "Business and work situations",
            "daily": "Daily life and routines",
            "restaurant": "Restaurant and dining",
            "shopping": "Shopping and purchases",
            "health": "Health and fitness",
            "hobby": "Hobbies and interests",
            "study": "Studying and education"
        }

        theme_desc = theme_descriptions.get(theme, theme)

        # 추가 설명이 있으면 포함
        context = f"{theme_desc}"
        if theme_detail:
            context += f" - specifically about: {theme_detail}"

        prompt = f"""Generate 3 to 6 simple English sentences for daily English learning.

Theme: {context}

Requirements:
- Generate between 3 to 6 sentences depending on how much the topic needs to be covered
- Each sentence should be 5-12 words long
- Use simple, practical vocabulary suitable for Korean learners
- The sentences can be related or form a short conversation
- Focus on commonly used expressions in real-life situations
- Make them natural and conversational
- Choose the number of sentences that best fits the topic (minimum 3, maximum 6)

Output format: Return ONLY the sentences (3-6 sentences), one per line, without numbering or any other text.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert English teacher for Korean learners. Generate practical, simple sentences for daily learning. Decide the optimal number of sentences (3-6) based on the topic."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            # 3~6문장 범위로 제한
            if len(sentences) < 3:
                raise ValueError(f"Too few sentences generated: {len(sentences)}")
            if len(sentences) > 6:
                sentences = sentences[:6]

            # 빈 문장이 있으면 에러
            if any(not s for s in sentences):
                raise ValueError("Empty sentence detected")

            print(f"✅ 테마별 문장 생성 완료: {theme} ({len(sentences)}문장)")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 문장 생성 실패: {e}")
            raise

    def generate_story_series(self, story_theme: str, day: int = 1, previous_context: str = "") -> list[str]:
        """
        스토리 시리즈 문장 생성 (Day 1-7 연결, 3~6문장 가변)

        Args:
            story_theme: 스토리 주제 (예: "해외 여행 첫날")
            day: Day 번호 (1-7)
            previous_context: 이전 Day의 내용 (Day 2 이상일 때)

        Returns:
            생성된 3~6개의 영어 문장 리스트
        """
        day_context = f"This is Day {day} of a 7-day story series."

        if day == 1:
            day_instruction = "This is the beginning of the story. Set up the scene and introduce the situation."
        elif day == 7:
            day_instruction = "This is the final day. Conclude the story with a resolution or reflection."
        else:
            day_instruction = f"Continue the story from Day {day-1}. Progress the narrative naturally."

        prompt = f"""Generate 3 to 6 simple English sentences for a story-based English learning series.

Story Theme: {story_theme}
{day_context}
{day_instruction}

{f"Previous context: {previous_context}" if previous_context else ""}

Requirements:
- Generate between 3 to 6 sentences depending on how much story development is needed
- Each sentence should be 5-12 words long
- Use simple, practical vocabulary
- The sentences should form a coherent part of the ongoing story
- Make it engaging and natural
- Focus on everyday conversation and situations
- Choose the number of sentences that best fits the story progression (minimum 3, maximum 6)

Output format: Return ONLY the sentences (3-6 sentences), one per line, without numbering or any other text.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative English teacher who creates engaging story-based lessons for Korean learners. Decide the optimal number of sentences (3-6) based on the story needs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=300
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            # 3~6문장 범위로 제한
            if len(sentences) < 3:
                raise ValueError(f"Too few sentences generated: {len(sentences)}")
            if len(sentences) > 6:
                sentences = sentences[:6]

            if any(not s for s in sentences):
                raise ValueError("Empty sentence detected")

            print(f"✅ 스토리 시리즈 문장 생성 완료: Day {day} ({len(sentences)}문장)")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 스토리 문장 생성 실패: {e}")
            raise

    def generate_movie_quotes(self) -> list[str]:
        """
        유명 영화 명대사 3개 생성

        Returns:
            생성된 3개의 영화 명대사 리스트
        """
        prompt = """Generate exactly 3 famous, simple movie quotes in English.

Requirements:
- Choose well-known, iconic movie quotes
- Each quote should be 5-12 words long
- Select quotes that are easy to understand for Korean learners
- Include quotes from different movies
- Make sure they are family-friendly

Output format: Return ONLY the 3 quotes, one per line, without movie names or any other text.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a film expert and English teacher. Select iconic, simple movie quotes for learning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            if len(sentences) != 3:
                sentences = sentences[:3]

            if len(sentences) < 3:
                raise ValueError("Failed to generate 3 valid movie quotes")

            print(f"✅ 영화 명대사 생성 완료")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 영화 명대사 생성 실패: {e}")
            raise

    def generate_pronunciation_sentences(self) -> list[str]:
        """
        발음 집중 훈련용 문장 3개 생성

        Returns:
            발음하기 어려운 단어가 포함된 3개의 문장 리스트
        """
        prompt = """Generate exactly 3 simple English sentences that are good for pronunciation practice.

Requirements:
- Each sentence should contain words with challenging pronunciation for Korean learners
- Include common difficult sounds: th, r/l, f/p, v/b, etc.
- Keep sentences simple (5-12 words) but naturally flowing
- Make them practical and useful for daily conversation
- Focus on one or two difficult sounds per sentence

Output format: Return ONLY the 3 sentences, one per line, without any other text.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a pronunciation expert teaching English to Korean speakers. Create sentences that help practice difficult sounds."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            if len(sentences) != 3:
                sentences = sentences[:3]

            if len(sentences) < 3:
                raise ValueError("Failed to generate 3 valid pronunciation sentences")

            print(f"✅ 발음 집중 문장 생성 완료")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 발음 집중 문장 생성 실패: {e}")
            raise

    def generate_news_sentences(self) -> list[str]:
        """
        오늘의 뉴스 스타일 문장 3개 생성

        Returns:
            뉴스 스타일의 3개 문장 리스트
        """
        prompt = """Generate exactly 3 simple news-style English sentences for learning.

Requirements:
- Use news/current events style language
- Keep sentences simple (5-12 words) and factual
- Topics can be: technology, environment, health, society, etc.
- Make them informative but easy to understand
- Use present simple or present perfect tense

Output format: Return ONLY the 3 sentences, one per line, without any other text.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a news writer creating simple English news sentences for Korean learners."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            if len(sentences) != 3:
                sentences = sentences[:3]

            if len(sentences) < 3:
                raise ValueError("Failed to generate 3 valid news sentences")

            print(f"✅ 뉴스 스타일 문장 생성 완료")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 뉴스 문장 생성 실패: {e}")
            raise
