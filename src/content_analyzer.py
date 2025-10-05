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
            sentences: 영어 문장 리스트 (3개)

        Returns:
            분석 결과
            {
                'num_images': int (1-3),
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
                    {"role": "system", "content": "You are an expert at analyzing sentence relationships and creating visual prompts."},
                    {"role": "user", "content": prompt}
                ]
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

        prompt = f"""Analyze these 3 English sentences and provide:
1. How many images should be generated (1-3)
2. Korean translations for each sentence

{sentences_text}

Guidelines:
- If all 3 sentences are closely related (same topic/context), generate 1 image covering all
- If 2 sentences are related and 1 is different, generate 2 images
- If all 3 sentences are different topics, generate 3 images

Respond in this format:
NUMBER_OF_IMAGES: [1, 2, or 3]
TRANSLATION_1: [Korean translation of sentence 1]
TRANSLATION_2: [Korean translation of sentence 2]
TRANSLATION_3: [Korean translation of sentence 3]
IMAGE_1: [sentence indices, e.g., "1,2,3" or "1" or "1,2"]
PROMPT_1: [detailed image generation prompt for DALL-E, in English]
[If 2 or 3 images]
IMAGE_2: [sentence indices]
PROMPT_2: [detailed prompt]
[If 3 images]
IMAGE_3: [sentence indices]
PROMPT_3: [detailed prompt]

Each prompt should create a cute, playful CARTOON or INFOGRAPHIC style illustration:
- Style: Simple cartoon/comic style with bold outlines OR clean infographic design
- Art: Flat 2D illustration, kawaii cute characters, or modern line art
- Colors: Bright cheerful pastels with high contrast
- Characters: Simple friendly cartoon style with expressive faces
- Background: Clean simple with geometric shapes
- Format: Vertical 9:16 ratio for mobile/YouTube Shorts
- Mood: Fun, lighthearted, educational
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

        num_images = 3  # 기본값
        image_groups = [[0], [1], [2]]
        prompts = []
        translations = ["", "", ""]  # 번역 저장

        current_prompt = ""

        for line in lines:
            line = line.strip()

            if line.startswith("NUMBER_OF_IMAGES:"):
                try:
                    num_images = int(line.split(":")[1].strip())
                except:
                    num_images = 3

            elif line.startswith("TRANSLATION_"):
                # 번역 파싱
                try:
                    translation_num = int(line.split("_")[1].split(":")[0])
                    translation_text = line.split(":", 1)[1].strip()
                    if 1 <= translation_num <= 3:
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
        for i in range(len(sentences)):
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
