"""
썸네일 제목 최적화 모듈

YouTube CTR 최적화를 위한 바이럴 제목 생성기.
GPT-4o-mini로 평범한 제목을 클릭 유도 제목으로 변환.

Author: Kelly & Claude Code
Date: 2025-11-09
"""
from openai import OpenAI
from typing import Optional


class ThumbnailTitleOptimizer:
    """
    YouTube 썸네일 제목 최적화기

    평범한 제목을 YouTube 알고리즘 친화적이고
    CTR이 높은 바이럴 제목으로 변환합니다.
    """

    def __init__(self, api_key: str):
        """
        Args:
            api_key: OpenAI API 키
        """
        self.client = OpenAI(api_key=api_key)

    def optimize_title(
        self,
        original_title: str,
        context: Optional[str] = None,
        target_audience: str = "영어 학습자"
    ) -> str:
        """
        평범한 제목을 바이럴 썸네일 제목으로 최적화

        Args:
            original_title: 원본 제목 (예: "여행영어 마스터")
            context: 추가 컨텍스트 (예: "랜드마크 영어 학습")
            target_audience: 타겟 시청자

        Returns:
            최적화된 썸네일 제목 (30자 이내)

        Example:
            >>> optimizer = ThumbnailTitleOptimizer(api_key)
            >>> title = optimizer.optimize_title("여행영어 마스터")
            >>> # "99% 틀리는 여행영어"
        """
        try:
            system_prompt = f"""
You are a YouTube thumbnail title optimization expert.
Your goal: Create click-worthy titles that maximize CTR (Click-Through Rate).

Target audience: {target_audience}
Platform: YouTube Shorts & 롱폼
Language: Korean (natural, conversational)

Title optimization principles:
1. Use numbers/stats: "99%", "3가지", "단 10초만에"
2. Create curiosity gap: "이것만 알면", "절대 모를", "사실은"
3. Use emotional triggers: "충격", "대박", "놀라운"
4. Promise value: "마스터", "완벽", "비밀"
5. Keep it short: 15-30 characters (Korean)
6. Avoid clickbait: Must deliver on promise

YouTube algorithm favors:
- Specific numbers
- Questions
- "How to" format
- Contrast/comparison
- Unexpected facts

Bad examples (avoid):
- "여행영어 마스터" (too generic)
- "영어 공부 잘하는 법" (boring)

Good examples (use as inspiration):
- "99% 틀리는 여행영어"
- "원어민도 놀란 표현 3가지"
- "이것만 알면 여행영어 끝"
- "10초만에 외우는 비법"
"""

            user_prompt = f"""
Original title: "{original_title}"
{f"Context: {context}" if context else ""}

Generate 1 optimized thumbnail title:
- Korean language
- 15-30 characters
- High CTR potential
- Curiosity-inducing
- Natural and conversational

Output ONLY the optimized title (no explanation).
"""

            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                max_tokens=50,
                temperature=0.9  # 창의적인 제목 생성
            )

            optimized_title = response.choices[0].message.content.strip()

            # 따옴표 제거 (GPT가 때때로 추가)
            optimized_title = optimized_title.strip('"\'')

            # 30자 제한
            if len(optimized_title) > 30:
                optimized_title = optimized_title[:30]

            print(f"✅ 제목 최적화: '{original_title}' → '{optimized_title}'")
            return optimized_title

        except Exception as e:
            print(f"⚠️ 제목 최적화 실패 (원본 사용): {e}")
            return original_title[:30]  # 실패 시 원본 제목 사용 (30자 제한)

    def generate_multiple_options(
        self,
        original_title: str,
        count: int = 3,
        context: Optional[str] = None
    ) -> list[str]:
        """
        여러 개의 최적화된 제목 옵션 생성

        Args:
            original_title: 원본 제목
            count: 생성할 옵션 개수 (기본 3개)
            context: 추가 컨텍스트

        Returns:
            최적화된 제목 리스트

        Example:
            >>> optimizer = ThumbnailTitleOptimizer(api_key)
            >>> options = optimizer.generate_multiple_options("여행영어 마스터", count=5)
            >>> # ["99% 틀리는 여행영어", "10초만에 외우는 비법", ...]
        """
        try:
            system_prompt = """
You are a YouTube thumbnail title optimization expert.
Generate multiple click-worthy title options for A/B testing.

Each title should:
- Use different psychological triggers
- Target different viewer motivations
- Maintain high CTR potential
- Be unique and creative

Output format: One title per line, no numbering.
"""

            user_prompt = f"""
Original title: "{original_title}"
{f"Context: {context}" if context else ""}
Target audience: 영어 학습자

Generate {count} different optimized thumbnail titles:
- Korean language
- 15-30 characters each
- Diverse approaches (numbers, questions, promises, contrast)
- High CTR potential

Output ONLY the titles (one per line, no explanation).
"""

            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                max_tokens=200,
                temperature=0.95  # 매우 창의적
            )

            content = response.choices[0].message.content.strip()
            titles = [line.strip().strip('"\'') for line in content.split('\n') if line.strip()]

            # 30자 제한 적용
            titles = [title[:30] for title in titles]

            # 요청한 개수만큼만 반환
            titles = titles[:count]

            print(f"✅ {len(titles)}개 제목 옵션 생성")
            return titles

        except Exception as e:
            print(f"⚠️ 다중 제목 생성 실패: {e}")
            return [original_title[:30]]


# 테스트 코드
if __name__ == '__main__':
    import os
    from pathlib import Path

    # API 키 로드
    project_root = Path(__file__).parent.parent.parent
    api_key_file = project_root / 'api_key.txt'

    if not api_key_file.exists():
        print("❌ api_key.txt 파일이 없습니다.")
        exit(1)

    api_key = api_key_file.read_text().strip()

    print("=" * 60)
    print("썸네일 제목 최적화 테스트")
    print("=" * 60)

    optimizer = ThumbnailTitleOptimizer(api_key=api_key)

    # 테스트 케이스
    test_cases = [
        ("여행영어 마스터", "랜드마크 영어 학습"),
        ("영어 회화 공부", "일상 영어"),
        ("발음 연습", "원어민 발음"),
        ("문법 정리", "영어 문법"),
    ]

    print("\n📝 단일 제목 최적화:")
    print("-" * 60)
    for original, context in test_cases:
        optimized = optimizer.optimize_title(original, context)
        print(f"원본: {original}")
        print(f"최적화: {optimized}")
        print()

    print("\n📝 다중 옵션 생성 (A/B 테스트용):")
    print("-" * 60)
    options = optimizer.generate_multiple_options(
        "여행영어 마스터",
        count=5,
        context="에펠탑 관광 영어"
    )
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    print("\n" + "=" * 60)
