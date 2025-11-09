"""
썸네일 재생성 엔진

마음에 안 드는 썸네일을 3가지 방식으로 재생성합니다:
1. 색상만 바꾸기 (빠름, 5초)
2. 레이아웃만 바꾸기 (보통, 8초)
3. 완전히 새로 만들기 (느림, 15초)

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import random
import colorsys
from typing import Dict, Any, List, Tuple
import copy


class VariationEngine:
    """
    썸네일 변형 생성 엔진

    기존 썸네일 설정을 기반으로 다양한 변형을 생성합니다.
    기존 코드와 완전히 독립적.
    """

    def __init__(self):
        """초기화"""
        pass

    def regenerate_color_variation(self, original_config: dict) -> dict:
        """
        색상만 변경 (레이아웃은 유지)

        가장 빠른 재생성 방법. 기존 레이아웃, 텍스트 위치는 그대로 유지하고
        색상 팔레트만 변경합니다.

        Args:
            original_config: 원본 썸네일 설정

        Returns:
            색상 변형된 새 설정

        Example:
            >>> engine = VariationEngine()
            >>> new_config = engine.regenerate_color_variation(original_config)
            >>> # 빨간색 → 파란색, 노란색 → 보라색 등
        """
        new_config = copy.deepcopy(original_config)

        # 원본 색상 추출
        original_colors = self._extract_colors_from_config(original_config)

        # 보색 또는 유사색 생성
        variation_type = random.choice(['complementary', 'analogous', 'triadic'])

        if variation_type == 'complementary':
            # 보색 (Color Wheel 반대편)
            new_colors = self._generate_complementary_colors(original_colors)
        elif variation_type == 'analogous':
            # 유사색 (Color Wheel 인접)
            new_colors = self._generate_analogous_colors(original_colors)
        else:
            # 삼색 조화 (120도 간격)
            new_colors = self._generate_triadic_colors(original_colors)

        # 새 색상 적용
        new_config = self._apply_colors_to_config(new_config, new_colors)
        new_config['variation_type'] = f'color_{variation_type}'

        print(f"✅ 색상 변형 생성: {variation_type}")
        return new_config

    def regenerate_layout_variation(self, original_config: dict) -> dict:
        """
        레이아웃만 변경 (색상은 유지)

        텍스트 위치, 캐릭터 배치 등을 변경하지만 색상은 그대로 유지합니다.

        Args:
            original_config: 원본 썸네일 설정

        Returns:
            레이아웃 변형된 새 설정

        Example:
            >>> engine = VariationEngine()
            >>> new_config = engine.regenerate_layout_variation(original_config)
            >>> # 상단 헤더 → 하단 헤더, 우측 캐릭터 → 좌측 캐릭터 등
        """
        new_config = copy.deepcopy(original_config)

        # 레이아웃 패턴 목록
        layout_patterns = [
            'header_top_text_bottom',      # 헤더 상단 + 텍스트 하단
            'header_bottom_text_top',      # 헤더 하단 + 텍스트 상단
            'centered_composition',        # 중앙 집중 배치
            'split_screen',                # 좌우 분할
            'diagonal_composition'         # 대각선 배치
        ]

        # 원본과 다른 레이아웃 선택
        current_layout = original_config.get('layout_pattern', 'header_top_text_bottom')
        available_layouts = [l for l in layout_patterns if l != current_layout]
        new_layout = random.choice(available_layouts)

        # 레이아웃 적용
        if new_layout == 'header_bottom_text_top':
            # 헤더를 하단으로
            if 'layout' in new_config and 'header_enabled' in new_config['layout']:
                new_config['text']['main']['position'] = 'top'
                new_config['text']['main']['y_offset'] = 50

        elif new_layout == 'centered_composition':
            # 모든 요소 중앙 집중
            new_config['layout']['character_position'] = 'center'
            new_config['text']['main']['position'] = 'center'
            new_config['text']['main']['y_offset'] = 200

        elif new_layout == 'split_screen':
            # 좌우 분할
            new_config['layout']['character_position'] = 'left'
            new_config['text']['main']['position'] = 'right'

        else:
            # 랜덤 조정
            positions = ['left', 'center', 'right']
            new_config['layout']['character_position'] = random.choice(positions)

        new_config['layout_pattern'] = new_layout
        new_config['variation_type'] = f'layout_{new_layout}'

        print(f"✅ 레이아웃 변형 생성: {new_layout}")
        return new_config

    def regenerate_complete_new(self, original_config: dict) -> dict:
        """
        완전히 새로운 디자인 생성

        원본을 참고하되 완전히 다른 스타일의 썸네일을 생성합니다.
        색상, 레이아웃, 스타일 모두 변경됩니다.

        Args:
            original_config: 원본 썸네일 설정

        Returns:
            완전히 새로운 설정

        Example:
            >>> engine = VariationEngine()
            >>> new_config = engine.regenerate_complete_new(original_config)
            >>> # Fire English → Minimalist로 완전 변경
        """
        new_config = copy.deepcopy(original_config)

        # 스타일 목록 (원본과 다른 것)
        from .styles import THUMBNAIL_STYLES

        available_styles = list(THUMBNAIL_STYLES.keys())
        if 'custom' in available_styles:
            available_styles.remove('custom')

        # 원본 스타일 제외
        original_style = original_config.get('style', 'fire_english')
        if original_style in available_styles:
            available_styles.remove(original_style)

        # 새 스타일 선택
        new_style_name = random.choice(available_styles)
        new_style = THUMBNAIL_STYLES[new_style_name]

        # 새 스타일 적용 (텍스트 내용은 유지)
        original_text = new_config.get('text_content', {})

        new_config = copy.deepcopy(new_style)
        new_config['text_content'] = original_text
        new_config['style'] = new_style_name
        new_config['variation_type'] = f'complete_{new_style_name}'

        print(f"✅ 완전 새 디자인: {original_style} → {new_style_name}")
        return new_config

    # ================================================================
    # 색상 조화 알고리즘 (Color Theory)
    # ================================================================

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """HEX → RGB 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """RGB → HEX 변환"""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'.upper()

    def _rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """RGB → HSV 변환"""
        r, g, b = [x / 255.0 for x in rgb]
        return colorsys.rgb_to_hsv(r, g, b)

    def _hsv_to_rgb(self, hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """HSV → RGB 변환"""
        r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
        return (int(r * 255), int(g * 255), int(b * 255))

    def _generate_complementary_colors(self, original_colors: List[str]) -> List[str]:
        """보색 생성 (180도 회전)"""
        new_colors = []

        for hex_color in original_colors:
            rgb = self._hex_to_rgb(hex_color)
            h, s, v = self._rgb_to_hsv(rgb)

            # Hue를 180도 회전
            new_h = (h + 0.5) % 1.0

            new_rgb = self._hsv_to_rgb((new_h, s, v))
            new_colors.append(self._rgb_to_hex(new_rgb))

        return new_colors

    def _generate_analogous_colors(self, original_colors: List[str]) -> List[str]:
        """유사색 생성 (30도 이동)"""
        new_colors = []

        # 랜덤하게 +30도 또는 -30도
        shift = random.choice([30, -30]) / 360.0

        for hex_color in original_colors:
            rgb = self._hex_to_rgb(hex_color)
            h, s, v = self._rgb_to_hsv(rgb)

            # Hue 이동
            new_h = (h + shift) % 1.0

            new_rgb = self._hsv_to_rgb((new_h, s, v))
            new_colors.append(self._rgb_to_hex(new_rgb))

        return new_colors

    def _generate_triadic_colors(self, original_colors: List[str]) -> List[str]:
        """삼색 조화 (120도 간격)"""
        new_colors = []

        for hex_color in original_colors:
            rgb = self._hex_to_rgb(hex_color)
            h, s, v = self._rgb_to_hsv(rgb)

            # Hue를 120도 또는 240도 회전
            shift = random.choice([120, 240]) / 360.0
            new_h = (h + shift) % 1.0

            new_rgb = self._hsv_to_rgb((new_h, s, v))
            new_colors.append(self._rgb_to_hex(new_rgb))

        return new_colors

    def _extract_colors_from_config(self, config: dict) -> List[str]:
        """설정에서 색상 추출"""
        colors = []

        # 레이아웃 색상
        if 'layout' in config:
            if 'header_color' in config['layout']:
                colors.append(config['layout']['header_color'])
            if 'background_color' in config['layout']:
                colors.append(config['layout']['background_color'])

        # 텍스트 색상
        if 'text' in config:
            for text_type in ['main', 'subtitle']:
                if text_type in config['text']:
                    if 'color' in config['text'][text_type]:
                        colors.append(config['text'][text_type]['color'])
                    if 'box_color' in config['text'][text_type]:
                        colors.append(config['text'][text_type]['box_color'])

        # 배지 색상
        if 'badges' in config:
            for badge_type in config['badges'].values():
                if isinstance(badge_type, dict) and 'bg_color' in badge_type:
                    colors.append(badge_type['bg_color'])

        # 중복 제거
        colors = list(dict.fromkeys(colors))

        # 최소 3개 보장
        while len(colors) < 3:
            colors.append('#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]))

        return colors[:5]  # 최대 5개

    def _apply_colors_to_config(self, config: dict, new_colors: List[str]) -> dict:
        """새 색상을 설정에 적용"""
        color_index = 0

        # 레이아웃 색상 교체
        if 'layout' in config:
            if 'header_color' in config['layout'] and color_index < len(new_colors):
                config['layout']['header_color'] = new_colors[color_index]
                color_index += 1

            if 'background_color' in config['layout'] and color_index < len(new_colors):
                config['layout']['background_color'] = new_colors[color_index]
                color_index += 1

        # 텍스트 색상 교체
        if 'text' in config and 'subtitle' in config['text']:
            if 'box_color' in config['text']['subtitle'] and color_index < len(new_colors):
                config['text']['subtitle']['box_color'] = new_colors[color_index]
                color_index += 1

        # 배지 색상 교체
        if 'badges' in config and 'sentence_count' in config['badges']:
            if 'bg_color' in config['badges']['sentence_count'] and color_index < len(new_colors):
                config['badges']['sentence_count']['bg_color'] = new_colors[color_index]
                color_index += 1

        return config


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("썸네일 재생성 엔진 테스트")
    print("=" * 60)

    from .styles import get_style

    engine = VariationEngine()

    # 원본 설정 (Fire English 스타일)
    original = get_style('fire_english')
    original['text_content'] = {
        'main': '여행영어 마스터',
        'subtitle': '필수 10문장'
    }

    print("\n📌 원본 스타일: Fire English")
    print(f"  헤더 색상: {original['layout']['header_color']}")

    # 1. 색상 변형
    print("\n1️⃣ 색상만 변경:")
    color_variation = engine.regenerate_color_variation(original)
    print(f"  새 헤더 색상: {color_variation['layout']['header_color']}")
    print(f"  변형 타입: {color_variation.get('variation_type', 'N/A')}")

    # 2. 레이아웃 변형
    print("\n2️⃣ 레이아웃만 변경:")
    layout_variation = engine.regenerate_layout_variation(original)
    print(f"  새 레이아웃: {layout_variation.get('layout_pattern', 'N/A')}")
    print(f"  캐릭터 위치: {layout_variation['layout']['character_position']}")

    # 3. 완전히 새로 만들기
    print("\n3️⃣ 완전히 새 디자인:")
    complete_new = engine.regenerate_complete_new(original)
    print(f"  새 스타일: {complete_new.get('style', 'N/A')}")
    print(f"  변형 타입: {complete_new.get('variation_type', 'N/A')}")

    print("\n" + "=" * 60)
