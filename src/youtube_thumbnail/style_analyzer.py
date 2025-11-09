"""
GPT-4 Vision 참고 이미지 분석 모듈

참고 썸네일 이미지를 업로드하면 GPT-4 Vision이 자동으로
색상, 레이아웃, 타이포그래피를 분석하여 스타일을 추출합니다.

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import base64
import json
from pathlib import Path
from typing import Optional
import os


class StyleAnalyzer:
    """
    참고 이미지 스타일 분석 (GPT-4 Vision)

    기존 코드와 완전히 독립적.
    """

    def __init__(self, api_key: str):
        """
        Args:
            api_key: OpenAI API 키
        """
        self.api_key = api_key

        # OpenAI 클라이언트 초기화
        try:
            import openai
            self.openai = openai
            self.client = openai.OpenAI(api_key=api_key)
            self.available = True
            print("✅ GPT-4 Vision 사용 가능")
        except ImportError:
            print("⚠️ OpenAI 라이브러리 없음 (pip install openai)")
            self.client = None
            self.available = False
        except Exception as e:
            print(f"⚠️ OpenAI 클라이언트 초기화 실패: {e}")
            self.client = None
            self.available = False

    def analyze_reference_image(self, image_path: str) -> Optional[dict]:
        """
        참고 썸네일 이미지 분석

        Args:
            image_path: 분석할 이미지 파일 경로

        Returns:
            {
                'color_palette': ['#HEX1', '#HEX2', ...],  # 주요 색상 5개
                'layout': {
                    'header': {'height': 100, 'color': '#HEX'},
                    'text_boxes': [...],
                    'character_position': 'right'|'center'|'left'
                },
                'typography': {
                    'main_font_size': 80,
                    'subtitle_font_size': 50,
                    'style': 'bold'|'regular'
                },
                'background': {
                    'type': 'gradient'|'solid'|'image',
                    'colors': ['#HEX1', '#HEX2']
                },
                'badges': ['sentence_count', 'duration']
            }
            또는 None (실패 시)

        Example:
            >>> analyzer = StyleAnalyzer(api_key='sk-...')
            >>> result = analyzer.analyze_reference_image('reference.png')
            >>> print(result['color_palette'])
            ['#D32F2F', '#FFFFFF', '#FF5722']
        """
        if not self.available:
            print("⚠️ GPT-4 Vision 사용 불가 (OpenAI 라이브러리 없음)")
            return None

        if not os.path.exists(image_path):
            print(f"❌ 이미지 파일 없음: {image_path}")
            return None

        try:
            # 이미지 Base64 인코딩
            print(f"📸 이미지 분석 중: {image_path}")
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 이미지 형식 감지
            image_ext = Path(image_path).suffix.lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }.get(image_ext, 'image/png')

            # GPT-4 Vision 호출
            response = self.client.chat.completions.create(
                model='gpt-4o',  # Vision 지원 모델
                messages=[{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': self._get_analysis_prompt()
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:{mime_type};base64,{image_base64}',
                                'detail': 'high'  # 고해상도 분석
                            }
                        }
                    ]
                }],
                max_tokens=1500,
                temperature=0.3  # 일관된 분석을 위해 낮은 temperature
            )

            # JSON 파싱
            result_text = response.choices[0].message.content

            # JSON 추출 (마크다운 코드 블록 제거)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]

            result = json.loads(result_text.strip())

            print("✅ 이미지 분석 완료")
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            print(f"   응답: {result_text[:200]}...")
            return None

        except Exception as e:
            print(f"❌ 이미지 분석 실패: {e}")
            return None

    def _get_analysis_prompt(self) -> str:
        """GPT-4 Vision 분석 프롬프트"""
        return """
Analyze this YouTube thumbnail image in detail and extract design elements.

**Instructions:**
1. Identify the TOP 5 dominant colors (hex codes)
2. Measure the layout structure (header height, text positions, character placement)
3. Estimate typography sizes (main text, subtitle)
4. Identify background style (gradient/solid/image)
5. Detect badges or special elements (number badges, duration labels)

**IMPORTANT:**
- Return ONLY valid JSON format (no markdown, no explanations)
- Use hex color codes with # prefix (e.g., "#D32F2F")
- Estimate pixel sizes based on standard 1280x720 thumbnail
- For character_position: use "left", "center", or "right"

**JSON Schema:**
```json
{
  "color_palette": ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"],
  "layout": {
    "header": {
      "height": 100,
      "color": "#HEX"
    },
    "text_boxes": [
      {
        "position": "top|middle|bottom",
        "color": "#HEX",
        "width": 800,
        "height": 100
      }
    ],
    "character_position": "right",
    "background_type": "solid|gradient|image"
  },
  "typography": {
    "main_font_size": 100,
    "subtitle_font_size": 60,
    "style": "bold|regular",
    "alignment": "left|center|right"
  },
  "background": {
    "type": "gradient",
    "colors": ["#HEX1", "#HEX2"]
  },
  "badges": {
    "has_number_badge": true,
    "has_duration_badge": true,
    "badge_positions": ["top-left", "bottom-right"]
  },
  "overall_style": "fire_english|minimalist|bold_bright|professional"
}
```

**Examples of good color extraction:**
- Fire English style: ["#D32F2F", "#FFFFFF", "#FF5722", "#FFC107", "#000000"]
- Minimalist style: ["#F5F5F5", "#212121", "#757575", "#FFFFFF", "#424242"]

Return ONLY the JSON object, nothing else.
"""

    def suggest_improvements(self, analysis: dict, current_config: dict) -> list[str]:
        """
        분석 결과 기반으로 개선 제안

        Args:
            analysis: analyze_reference_image() 결과
            current_config: 현재 썸네일 설정

        Returns:
            개선 제안 리스트

        Example:
            >>> suggestions = analyzer.suggest_improvements(analysis, config)
            >>> for suggestion in suggestions:
                    print(f"- {suggestion}")
        """
        suggestions = []

        # 색상 대비 검사
        if 'color_palette' in analysis:
            colors = analysis['color_palette']
            if len(colors) < 3:
                suggestions.append("💡 색상이 단조롭습니다. 3가지 이상 사용을 권장합니다.")

        # 헤더 검사
        if 'layout' in analysis and 'header' in analysis['layout']:
            header_height = analysis['layout']['header'].get('height', 0)
            if header_height < 80:
                suggestions.append("💡 헤더가 작습니다. 최소 100px 권장합니다.")
            elif header_height > 200:
                suggestions.append("💡 헤더가 너무 큽니다. 컨텐츠 영역이 부족할 수 있습니다.")

        # 폰트 크기 검사
        if 'typography' in analysis:
            main_size = analysis['typography'].get('main_font_size', 0)
            if main_size < 80:
                suggestions.append("💡 메인 텍스트가 작습니다. 모바일에서 읽기 어려울 수 있습니다.")

        # 배지 검사
        if 'badges' in analysis:
            if not analysis['badges'].get('has_number_badge'):
                suggestions.append("💡 숫자 배지를 추가하면 클릭률이 높아집니다. (예: 문장 개수)")
            if not analysis['badges'].get('has_duration_badge'):
                suggestions.append("💡 영상 길이 배지를 추가하면 시청자가 시간을 예상할 수 있습니다.")

        # 캐릭터 위치 검사
        if 'layout' in analysis:
            char_pos = analysis['layout'].get('character_position', '')
            if char_pos == 'left':
                suggestions.append("💡 캐릭터를 중앙 또는 우측으로 이동하면 텍스트와 균형이 좋습니다.")

        return suggestions


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("GPT-4 Vision 스타일 분석기 테스트")
    print("=" * 60)

    # API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   테스트를 실행하려면 .env 파일에 API 키를 추가하세요.")
        exit(1)

    analyzer = StyleAnalyzer(api_key=api_key)

    if not analyzer.available:
        print("❌ GPT-4 Vision 사용 불가")
        exit(1)

    # 테스트 이미지 경로 (존재하는 썸네일 이미지 필요)
    test_image = 'output/resources/images/kelly_casual_hoodie.png'

    if os.path.exists(test_image):
        print(f"\n🔍 테스트 이미지: {test_image}\n")

        result = analyzer.analyze_reference_image(test_image)

        if result:
            print("✅ 분석 성공!\n")
            print("📊 색상 팔레트:")
            for color in result.get('color_palette', []):
                print(f"  - {color}")

            print("\n📐 레이아웃:")
            layout = result.get('layout', {})
            print(f"  헤더 높이: {layout.get('header', {}).get('height', 'N/A')}px")
            print(f"  캐릭터 위치: {layout.get('character_position', 'N/A')}")

            print("\n✏️ 타이포그래피:")
            typo = result.get('typography', {})
            print(f"  메인 폰트: {typo.get('main_font_size', 'N/A')}px")
            print(f"  서브 폰트: {typo.get('subtitle_font_size', 'N/A')}px")

            # 개선 제안
            print("\n💡 개선 제안:")
            suggestions = analyzer.suggest_improvements(result, {})
            if suggestions:
                for suggestion in suggestions:
                    print(f"  {suggestion}")
            else:
                print("  완벽합니다! 개선 사항이 없습니다.")
        else:
            print("❌ 분석 실패")
    else:
        print(f"⚠️ 테스트 이미지 없음: {test_image}")
        print("   실제 썸네일 이미지로 테스트하세요.")

    print("\n" + "=" * 60)
