"""
OpenAI GPT를 사용한 문장 자동 생성 모듈
"""
import os
import time
from openai import OpenAI


class SentenceGenerator:
    def __init__(self, api_key: str = None):
        """
        SentenceGenerator 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def _call_openai_with_retry(self, model: str, messages: list, temperature: float, max_tokens: int, max_retries: int = 3):
        """
        재시도 로직을 포함한 OpenAI API 호출

        Args:
            model: 모델 이름
            messages: 메시지 리스트
            temperature: Temperature 설정
            max_tokens: 최대 토큰 수
            max_retries: 최대 재시도 횟수 (기본 3회)

        Returns:
            OpenAI API 응답

        Raises:
            Exception: 모든 재시도 실패 시
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response
            except Exception as e:
                last_error = e
                error_msg = str(e)

                # 500 에러인 경우 재시도
                if "500" in error_msg or "server" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2초, 4초, 6초
                        print(f"⚠️ OpenAI 서버 오류 발생. {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue

                # 그 외 에러는 즉시 발생
                raise

        # 모든 재시도 실패
        raise Exception(f"OpenAI API 호출 실패 (최대 재시도 {max_retries}회): {last_error}")

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
            response = self._call_openai_with_retry(
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
            response = self._call_openai_with_retry(
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

    def generate_movie_quotes(self, selected_quote_id: int = None) -> list[str]:
        """
        유명 영화 명대사 3~6개 생성 (리스트 선택 방식)

        Args:
            selected_quote_id: 선택된 명대사 ID (None이면 랜덤 3개 선택)

        Returns:
            생성된 3~6개의 영화 명대사 리스트 (영화 제목 + 캐릭터 포함)
        """
        import json
        from pathlib import Path

        # movie_quotes.json 로드
        quotes_file = Path(__file__).parent / 'movie_quotes.json'

        try:
            with open(quotes_file, 'r', encoding='utf-8') as f:
                quotes_data = json.load(f)
                all_quotes = quotes_data['quotes']
        except Exception as e:
            print(f"⚠️ movie_quotes.json 로드 실패: {e}")
            # 기본 3개 영화 명대사 반환
            return self._generate_movie_quotes_fallback()

        if selected_quote_id:
            # 선택된 명대사 찾기
            selected = next((q for q in all_quotes if q['id'] == selected_quote_id), None)

            if not selected:
                print(f"⚠️ ID {selected_quote_id} 명대사를 찾을 수 없습니다. 랜덤 선택합니다.")
                import random
                selected = random.choice(all_quotes)

            # GPT로 해당 영화의 다른 명대사들 3-6개 생성
            return self._generate_related_movie_quotes(selected)

        else:
            # 랜덤 3개 선택
            import random
            selected_quotes = random.sample(all_quotes, 3)

            sentences = []
            for q in selected_quotes:
                sentence = f"{q['quote']} ({q['movie']} - {q['character']})"
                sentences.append(sentence)

            print(f"✅ 영화 명대사 랜덤 3개 선택 완료")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

    def _generate_related_movie_quotes(self, selected_quote: dict) -> list[str]:
        """
        선택된 명대사와 관련된 영화 명대사들 3~6개 생성

        Args:
            selected_quote: 선택된 명대사 정보 (quote, movie, character, year)

        Returns:
            3~6개의 명대사 리스트
        """
        movie = selected_quote['movie']
        character = selected_quote['character']
        main_quote = selected_quote['quote']

        prompt = f"""Generate 3 to 6 famous quotes from the movie "{movie}" for English learning.

Main quote to include:
"{main_quote}" - {character}

Requirements:
- MUST include the main quote above as the FIRST quote
- Add 2-5 more famous quotes from the same movie "{movie}"
- Each quote should be 5-15 words long
- Choose iconic, memorable quotes from the movie
- Make them suitable for Korean English learners
- Return 3-6 quotes total (including the main quote)

Output format: Return ONLY the quotes, one per line, in this format:
[Quote text] ([Movie name] - [Character name])

Example:
May the Force be with you. (Star Wars - Obi-Wan Kenobi)
I have a bad feeling about this. (Star Wars - Han Solo)
"""

        try:
            response = self._call_openai_with_retry(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a film expert specializing in the movie '{movie}'. Generate memorable quotes from this specific movie only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            sentences_text = response.choices[0].message.content.strip()
            sentences = [s.strip() for s in sentences_text.split('\n') if s.strip()]

            # 3~6개 범위 검증
            if len(sentences) < 3:
                # 최소 3개는 되도록 선택된 명대사라도 추가
                sentences.append(f"{main_quote} ({movie} - {character})")
                sentences = sentences[:3]
            elif len(sentences) > 6:
                sentences = sentences[:6]

            print(f"✅ 영화 명대사 생성 완료: {movie} ({len(sentences)}개)")
            for idx, s in enumerate(sentences, 1):
                print(f"   {idx}. {s}")

            return sentences

        except Exception as e:
            print(f"✗ 영화 명대사 생성 실패: {e}")
            # 실패 시 선택된 명대사만 3번 반복
            fallback = [f"{main_quote} ({movie} - {character})"] * 3
            return fallback

    def _generate_movie_quotes_fallback(self) -> list[str]:
        """
        movie_quotes.json 로드 실패 시 기본 명대사 3개 반환
        """
        fallback_quotes = [
            "May the Force be with you. (Star Wars - Obi-Wan Kenobi)",
            "I'll be back. (The Terminator - The Terminator)",
            "Life is like a box of chocolates. (Forrest Gump - Forrest Gump)"
        ]

        print(f"✅ 기본 영화 명대사 3개 사용")
        for idx, s in enumerate(fallback_quotes, 1):
            print(f"   {idx}. {s}")

        return fallback_quotes

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
            response = self._call_openai_with_retry(
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
            response = self._call_openai_with_retry(
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

    def generate_quiz_content(self, topic: str, difficulty: str = "intermediate") -> dict:
        """
        퀴즈 챌린지 콘텐츠 생성 (A/B 문제 + 해설 + 예문)

        Args:
            topic: 퀴즈 주제 (adjectives, prepositions, articles, verbs, pronouns, countable, comparatives, confusing)
            difficulty: 난이도 (beginner, intermediate, advanced)

        Returns:
            {
                'question': '문제 질문',
                'option_a': '선택지 A',
                'option_b': '선택지 B',
                'correct_answer': 'A' or 'B',
                'explanation': '해설 (한국어)',
                'examples': ['예문1', '예문2', '예문3']
            }
        """
        # 주제별 설명
        topic_descriptions = {
            "adjectives": "-ing vs -ed 형용사 (boring/bored)",
            "prepositions": "전치사 (in/on/at)",
            "articles": "관사 (a/an/the)",
            "verbs": "동사 시제 (과거/현재/미래)",
            "pronouns": "대명사 (I/me, who/whom)",
            "countable": "셀 수 있는/없는 명사",
            "comparatives": "비교급/최상급",
            "confusing": "헷갈리는 단어 (affect/effect)"
        }

        topic_desc = topic_descriptions.get(topic, topic)

        # 난이도별 설정
        difficulty_instructions = {
            "beginner": "Use simple, everyday vocabulary. Focus on basic grammar rules.",
            "intermediate": "Use common vocabulary and typical mistakes Korean learners make.",
            "advanced": "Use nuanced expressions and subtle grammar differences."
        }

        difficulty_instruction = difficulty_instructions.get(difficulty, difficulty_instructions["intermediate"])

        prompt = f"""Create an A/B quiz question for Korean English learners.

Topic: {topic_desc}
Difficulty: {difficulty}
Instruction: {difficulty_instruction}

Generate a quiz in the following format:

1. Question: A clear, simple question asking which sentence is correct (in Korean)
2. Option A: One sentence (5-10 words)
3. Option B: One sentence (5-10 words)
4. Correct Answer: Either 'A' or 'B'
5. Explanation: Brief explanation in Korean (2-3 sentences) explaining why one is correct and the other is wrong
6. Examples: 3 additional example sentences showing correct usage

Requirements:
- Make the question engaging (e.g., "한국인 95% 틀리는 문제!")
- Options should look similar but have one clear error
- Explanation must be in Korean, clear and educational
- Examples should be practical and easy to understand

Output format (JSON):
{{
    "question": "다음 중 올바른 표현은?",
    "option_a": "[Sentence A]",
    "option_b": "[Sentence B]",
    "correct_answer": "A",
    "explanation": "Korean explanation here",
    "examples": [
        "Example sentence 1",
        "Example sentence 2",
        "Example sentence 3"
    ]
}}

Return ONLY valid JSON, no additional text."""

        try:
            response = self._call_openai_with_retry(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are an expert English quiz creator for Korean learners. Create engaging A/B questions that highlight common mistakes. Topic: {topic_desc}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # JSON 파싱
            import json

            # ```json ... ``` 제거
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            quiz_data = json.loads(content.strip())

            # 검증
            required_keys = ['question', 'option_a', 'option_b', 'correct_answer', 'explanation', 'examples']
            for key in required_keys:
                if key not in quiz_data:
                    raise ValueError(f"Missing key: {key}")

            if quiz_data['correct_answer'] not in ['A', 'B']:
                raise ValueError(f"Invalid correct_answer: {quiz_data['correct_answer']}")

            if len(quiz_data['examples']) != 3:
                raise ValueError(f"Must have exactly 3 examples, got {len(quiz_data['examples'])}")

            print(f"✅ 퀴즈 콘텐츠 생성 완료: {topic} ({difficulty})")
            print(f"   질문: {quiz_data['question']}")
            print(f"   A: {quiz_data['option_a']}")
            print(f"   B: {quiz_data['option_b']}")
            print(f"   정답: {quiz_data['correct_answer']}")

            return quiz_data

        except json.JSONDecodeError as e:
            print(f"✗ JSON 파싱 실패: {e}")
            print(f"응답 내용: {content}")
            raise ValueError(f"Failed to parse quiz JSON: {e}")
        except Exception as e:
            print(f"✗ 퀴즈 콘텐츠 생성 실패: {e}")
            raise
