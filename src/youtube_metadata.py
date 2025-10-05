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
                    {"role": "system", "content": "You are a YouTube content optimization expert. Generate engaging metadata for English learning videos."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
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

        prompt = f"""Given these English sentences for a daily learning video:

{sentences_text}

Generate YouTube metadata in JSON format with the following structure:
{{
    "title": "Catchy title in Korean (maximum 100 characters, should include '영어회화', '일상영어' etc)",
    "description": "Engaging description in Korean (should include the 3 English sentences with Korean translations, and encourage learning)",
    "tags": ["list", "of", "relevant", "tags", "in", "Korean", "and", "English"],
    "category": "Education"
}}

The title should be catchy and encourage viewers to learn.
The description should include:
1. Brief intro about daily English learning
2. The 3 English sentences with Korean translations
3. Encouragement to subscribe and like
Tags should include relevant keywords like: 영어회화, 영어공부, 일상영어, English, daily English, etc.
"""
        return prompt

    def _create_default_metadata(self, sentences: list[str]) -> dict:
        """
        기본 메타정보 생성 (GPT 실패 시)

        Args:
            sentences: 영어 문장 리스트

        Returns:
            기본 메타정보
        """
        return {
            "title": "매일 3문장 영어회화 | Daily English Mecca",
            "description": f"""🌟 하루 3문장으로 영어 마스터하기!

📝 오늘의 문장:
{chr(10).join([f'{i+1}. {s}' for i, s in enumerate(sentences)])}

매일 3문장씩 외우면서 자연스러운 영어 표현을 익혀보세요!

👍 좋아요와 구독 부탁드립니다!
🔔 알림 설정하고 매일 새로운 표현을 받아보세요!

#영어회화 #영어공부 #일상영어 #EnglishLearning""",
            "tags": [
                "영어회화", "영어공부", "일상영어", "영어표현",
                "English", "Daily English", "Learn English",
                "영어쇼츠", "영어숏츠", "영어배우기"
            ],
            "category": "Education"
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
