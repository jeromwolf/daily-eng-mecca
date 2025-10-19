"""
문장 분석 및 이미지 개수 결정 모듈
"""
import os
from openai import OpenAI


class ContentAnalyzer:
    def __init__(self, api_key: str = None):
        """
        ContentAnalyzer 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def analyze_sentences(self, sentences: list[str]) -> dict:
        """
        문장들을 분석하여 이미지 개수와 그룹핑 정보, 번역 반환

        Args:
            sentences: 영어 문장 리스트 (3~6개)

        Returns:
            분석 결과
            {
                'num_images': int (문장 개수만큼),
                'image_groups': list[list[int]], # 각 이미지에 포함될 문장 인덱스
                'prompts': list[str], # 각 이미지 생성용 프롬프트
                'translations': list[str] # 각 문장의 한글 번역
            }
        """
        try:
            print("문장 분석 중...")

            # GPT를 사용하여 문장 관련성 분석
            prompt = self._create_analysis_prompt(sentences)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are an expert English-Korean translator and visual content creator specializing in educational materials for Korean learners.

Your translations are:
- Natural and conversational (not literal/stiff)
- Contextually accurate and culturally appropriate
- Easy to understand for Korean learners
- Preserving the nuance and tone of the original English

Your image prompts are:
- Visually appealing and cute/playful for social media
- Clear and easy to understand at a glance
- Culturally appropriate for Korean audiences
- Optimized for vertical 9:16 format (YouTube Shorts)"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7  # 자연스러운 번역을 위해 약간 높은 온도
            )

            analysis_text = response.choices[0].message.content

            # 분석 결과 파싱
            result = self._parse_analysis(analysis_text, sentences)

            print(f"✓ 분석 완료: {result['num_images']}개의 이미지 생성 예정")
            return result

        except Exception as e:
            print(f"✗ 분석 실패: {e}")
            # 기본값: 각 문장마다 1개씩 이미지 생성
            return self._create_default_analysis(sentences)

    def _create_analysis_prompt(self, sentences: list[str]) -> str:
        """
        문장 분석을 위한 프롬프트 생성

        Args:
            sentences: 영어 문장 리스트

        Returns:
            GPT 프롬프트
        """
        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        num_sentences = len(sentences)

        # 번역 형식 동적 생성
        translation_format = "\n".join([f"TRANSLATION_{i+1}: [Korean translation of sentence {i+1}]"
                                       for i in range(num_sentences)])

        prompt = f"""Analyze these {num_sentences} English sentences for a YouTube Shorts English learning video and provide:
1. Natural Korean translations (NOT literal, but conversational and contextually accurate)
2. Visual prompts for each sentence

{sentences_text}

📚 TRANSLATION GUIDELINES:
- Translate naturally as native Koreans would say it
- Consider the context and situation
- Use appropriate levels of formality (반말/존댓말)
- Preserve the emotional tone and nuance
- Make it easy to understand for learners
- Avoid overly literal or awkward translations

Examples of good vs bad translation:
❌ Bad: "I'm going to spend time with family" → "나는 가족과 시간을 보낼 것입니다" (too formal/literal)
✅ Good: "I'm going to spend time with family" → "가족들이랑 시간 보낼 거예요" (natural)

❌ Bad: "What's up?" → "무엇이 올라갔습니까?" (literal nonsense)
✅ Good: "What's up?" → "어떻게 지내?" or "뭐해?" (contextual)

Respond in this EXACT format:
NUMBER_OF_IMAGES: {num_sentences}
{translation_format}
IMAGE_1: 1
PROMPT_1: [detailed image generation prompt for DALL-E, in English]
IMAGE_2: 2
PROMPT_2: [detailed prompt]
{f"IMAGE_{num_sentences}: {num_sentences}" if num_sentences > 2 else ""}
{f"PROMPT_{num_sentences}: [detailed prompt]" if num_sentences > 2 else ""}

🎨 IMAGE PROMPT REQUIREMENTS (DALL-E style):
Create GENERALIZED, REUSABLE illustrations (for better caching):
- Make prompts GENERAL, not sentence-specific (e.g., "love theme" not "I love you scene")
- Focus on THEME/TOPIC rather than exact sentence content
- This allows similar sentences to reuse the same cached images

Style guidelines:
- Style: Simple flat 2D cartoon/comic with bold outlines OR modern infographic
- Art: Kawaii cute characters with big expressive eyes OR clean line art icons
- Colors: Bright cheerful pastels (pink, mint, yellow, sky blue) with high contrast
- Characters: Diverse, friendly, simple cartoon people with happy expressions
- Background: Clean minimal with geometric shapes, gradients, or patterns
- Layout: Vertical 9:16 format optimized for mobile (important!)
- Text: NO text in images (text will be added separately)
- Mood: Fun, positive, educational, approachable
- Composition: Center the main subject, leave breathing room

Example GENERALIZED prompts (good for caching):
- Instead of "person saying I love you" → "cute illustration about love and affection, hearts and warmth theme"
- Instead of "ordering coffee at cafe" → "casual dining and cafe scene, friendly atmosphere"
- Instead of "studying for exam" → "education and learning theme, books and study materials"
"""
        return prompt

    def _parse_analysis(self, analysis_text: str, sentences: list[str]) -> dict:
        """
        GPT 응답을 파싱하여 결과 딕셔너리 생성

        Args:
            analysis_text: GPT 응답 텍스트
            sentences: 원본 문장 리스트

        Returns:
            분석 결과 딕셔너리
        """
        lines = analysis_text.strip().split('\n')
        num_sentences = len(sentences)

        num_images = num_sentences  # 기본값: 문장 개수만큼
        image_groups = [[i] for i in range(num_sentences)]  # 각 문장당 1개 이미지
        prompts = []
        translations = ["" for _ in range(num_sentences)]  # 동적 크기 배열

        current_prompt = ""

        for line in lines:
            line = line.strip()

            if line.startswith("NUMBER_OF_IMAGES:"):
                try:
                    num_images = int(line.split(":")[1].strip())
                except:
                    num_images = num_sentences

            elif line.startswith("TRANSLATION_"):
                # 번역 파싱
                try:
                    translation_num = int(line.split("_")[1].split(":")[0])
                    translation_text = line.split(":", 1)[1].strip()
                    if 1 <= translation_num <= num_sentences:
                        translations[translation_num - 1] = translation_text
                except:
                    pass

            elif line.startswith("IMAGE_"):
                # 이전 프롬프트 저장
                if current_prompt:
                    prompts.append(current_prompt.strip())
                    current_prompt = ""

                # 이미지 인덱스 파싱
                try:
                    idx_part = line.split(":")[1].strip()
                    indices = [int(x.strip()) - 1 for x in idx_part.split(",")]
                    if len(prompts) < len(image_groups):
                        image_groups[len(prompts)] = indices
                except:
                    pass

            elif line.startswith("PROMPT_"):
                current_prompt = line.split(":", 1)[1].strip()

            elif current_prompt:
                # 멀티라인 프롬프트 계속 이어가기
                current_prompt += " " + line

        # 마지막 프롬프트 저장
        if current_prompt:
            prompts.append(current_prompt.strip())

        # 프롬프트가 부족하면 기본 프롬프트 생성
        while len(prompts) < num_images:
            idx = len(prompts)
            if idx < len(image_groups) and image_groups[idx]:
                sentence_idx = image_groups[idx][0]
                if sentence_idx < len(sentences):
                    prompts.append(self._create_default_prompt(sentences[sentence_idx]))

        # image_groups를 num_images에 맞게 조정
        image_groups = image_groups[:num_images]

        # 번역이 없는 경우 기본 번역 생성
        for i in range(num_sentences):
            if not translations[i]:
                translations[i] = f"[번역 필요] {sentences[i]}"

        return {
            'num_images': num_images,
            'image_groups': image_groups,
            'prompts': prompts[:num_images],
            'translations': translations
        }

    def _create_default_analysis(self, sentences: list[str]) -> dict:
        """
        기본 분석 결과 생성 (GPT 실패 시)

        Args:
            sentences: 영어 문장 리스트

        Returns:
            기본 분석 결과
        """
        return {
            'num_images': len(sentences),
            'image_groups': [[i] for i in range(len(sentences))],
            'prompts': [self._create_default_prompt(s) for s in sentences],
            'translations': [f"[번역 필요] {s}" for s in sentences]
        }

    def generate_hook_phrase(self, sentences: list[str]) -> str:
        """
        인트로용 바이럴 훅 문구 생성 (AI 자동 생성)

        Args:
            sentences: 영어 문장 리스트

        Returns:
            훅 문구 (예: "99% 틀리는 표현 🔥", "이거 모르면 손해!")
        """
        try:
            print("훅 문구 생성 중...")

            sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

            prompt = f"""Create ONE viral hook phrase in Korean for these English learning sentences (YouTube Shorts, first 3 seconds).

Sentences:
{sentences_text}

🎯 TARGET AUDIENCE:
- Korean English learners (20-35 years old)
- Busy office workers & students
- Want quick, practical English tips
- TikTok/Shorts consumption habits

🔥 VIRAL HOOK FORMULA (choose ONE strategy):

1. **Exclusivity & Scarcity** (가장 효과적!)
   - "원어민만 쓰는 표현"
   - "교과서에 없는 진짜 영어"
   - "드라마 주인공 되는 법"

2. **Social Proof Failure** (실수 공감)
   - "한국인 99% 틀리는 영어"
   - "이거 쓰면 바로 들킴"
   - "외국인이 웃는 영어 실수"

3. **Urgency & FOMO** (놓치면 손해)
   - "모르면 쪽팔리는 표현"
   - "10초면 끝나는 영어"
   - "이거 하나면 끝!"

4. **Controversial & Shocking** (충격 유발)
   - "학교에서 안 가르쳐주는 영어"
   - "이거 몰랐다고?"
   - "진짜 vs 가짜 영어"

5. **Numbers & Stats** (구체적 수치)
   - "3초 안에 외우기"
   - "꼭 알아야 할 표현 3개"
   - "1분 발음 교정"

✅ REQUIREMENTS:
- Length: 6-12 Korean characters ONLY
- NO emojis, NO punctuation marks (!, ?)
- Natural Korean (not translated)
- Creates curiosity gap
- Makes viewers stop scrolling

❌ AVOID:
- Generic: "영어 표현 배우기" (too boring)
- Too long: "오늘 배울 필수 영어 표현 3가지" (too wordy)
- Emojis: "🔥 핫한 표현" (no emojis!)

📊 VIRAL EXAMPLES (high CTR):
- "원어민만 쓰는 표현"
- "한국인 99% 틀림"
- "이거 모르면 손해"
- "교과서에 없는 영어"
- "3초면 끝"

Respond with ONLY the hook phrase (no quotes, no explanation).
Example: 원어민만 쓰는 표현
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a viral content creator specializing in Korean YouTube Shorts. You create highly engaging, clickable hook phrases."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # 높은 창의성
                max_tokens=50
            )

            hook_phrase = response.choices[0].message.content.strip()

            # 따옴표 제거 (GPT가 추가할 수 있음)
            hook_phrase = hook_phrase.strip('"').strip("'").strip()

            # 이모지 제거 (MoviePy TextClip이 이모지를 렌더링하지 못함)
            import re
            # 이모지 제거 정규식 (한글을 제외한 이모지만 제거)
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # 감정 이모지
                "\U0001F300-\U0001F5FF"  # 기호 & 픽토그램
                "\U0001F680-\U0001F6FF"  # 교통 & 지도
                "\U0001F1E0-\U0001F1FF"  # 국기
                "\U00002600-\U000026FF"  # 기타 기호
                "\U00002700-\U000027BF"  # Dingbats
                "\U0001F900-\U0001F9FF"  # 추가 이모지
                "\U0001FA70-\U0001FAFF"  # 확장 이모지
                "]+", flags=re.UNICODE
            )
            hook_phrase = emoji_pattern.sub('', hook_phrase).strip()

            print(f"✓ 훅 문구 생성 완료: {hook_phrase}")
            return hook_phrase

        except Exception as e:
            print(f"✗ 훅 문구 생성 실패 (기본값 사용): {e}")
            # 기본값: 안전한 훅 문구
            return "오늘의 필수 표현!"

    def _create_default_prompt(self, sentence: str) -> str:
        """
        기본 이미지 프롬프트 생성

        Args:
            sentence: 영어 문장

        Returns:
            DALL-E 프롬프트
        """
        return f"""Create a cute, playful cartoon illustration or infographic style artwork for: "{sentence}"

Style: Simple cartoon/comic style or clean infographic design with bold outlines
Art Style: Flat 2D illustration, kawaii cute characters, or modern line art with minimal shading
Colors: Bright, cheerful pastel colors with high contrast
Characters: If people, draw them as simple, friendly cartoon characters with expressive faces
Background: Clean, simple with geometric shapes or minimal decorative elements
Composition: Centered, balanced, vertical format (9:16 ratio) suitable for mobile
Mood: Fun, lighthearted, educational, and approachable
Elements: Use simple icons, symbols, and playful visual metaphors
"""
