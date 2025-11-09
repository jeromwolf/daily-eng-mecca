"""
YouTube 썸네일 생성 엔진

PIL을 사용하여 전문적인 YouTube 썸네일을 생성합니다.
기존 src/thumbnail_generator.py와 완전히 독립적.

Author: Kelly & Claude Code
Date: 2025-11-09
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import Optional, Tuple
import os


class YouTubeThumbnailEngine:
    """
    YouTube 전용 썸네일 생성 엔진

    기존 ThumbnailGenerator와 완전히 다른 클래스.
    메서드명도 다르게 하여 충돌 방지.
    """

    # YouTube 썸네일 표준 크기
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, output_dir: str = 'output/youtube_thumbnails'):
        """
        Args:
            output_dir: 썸네일 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 폰트 설정
        self.font_path = self._find_font()

    def _find_font(self) -> Optional[str]:
        """
        시스템 폰트 찾기 (AppleGothic 우선)

        Returns:
            폰트 파일 경로 또는 None
        """
        font_candidates = [
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',  # macOS
            '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',  # Ubuntu
            'C:\\Windows\\Fonts\\malgun.ttf',  # Windows (맑은고딕)
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'  # Linux fallback
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                print(f"✅ 폰트 로드: {font_path}")
                return font_path

        print("⚠️ 시스템 폰트 없음, 기본 폰트 사용")
        return None

    def create_thumbnail(
        self,
        main_text: str,
        subtitle_text: str = '',
        style: str = 'ted_style',
        sentence_count: int = 0,
        video_duration: str = '',
        background_image_path: Optional[str] = None,
        channel_icon_path: Optional[str] = None,
        text_position: str = 'center',
        brand_colors: Optional[dict] = None
    ) -> str:
        """
        TED 스타일 썸네일 생성 (유튜브 영상 스크린샷 기반)

        Args:
            main_text: 메인 텍스트 (필수, GPT로 최적화된 제목)
            subtitle_text: 서브 텍스트
            style: 스타일 템플릿 ('ted_style', 'fire_english', 등)
            sentence_count: 문장 개수 (숫자 배지용, 선택)
            video_duration: 영상 길이 ("3:42" 형식)
            background_image_path: YouTube 영상 스크린샷 경로 (NEW)
            channel_icon_path: 채널 아이콘 경로 (NEW, 원형으로 표시)
            text_position: 텍스트 위치 ('left', 'center', 'right')
            brand_colors: 브랜드 색상 dict

        Returns:
            생성된 썸네일 파일 경로

        Example (TED Style):
            >>> engine = YouTubeThumbnailEngine()
            >>> path = engine.create_thumbnail(
                    main_text='99% 틀리는 여행영어',
                    background_image_path='/path/to/youtube_screenshot.jpg',
                    channel_icon_path='/path/to/channel_icon.jpg',
                    video_duration='3:42',
                    text_position='center'
                )
        """
        # 1. 배경 이미지 로드 (YouTube 스크린샷 또는 생성)
        if background_image_path and os.path.exists(background_image_path):
            # TED 스타일: 실제 YouTube 영상 스크린샷 사용
            canvas = Image.open(background_image_path)
            canvas = canvas.resize((self.WIDTH, self.HEIGHT), Image.Resampling.LANCZOS)

            # 이미지 샤프닝 (선명도 향상) - 흐림 문제 해결
            canvas = canvas.filter(ImageFilter.SHARPEN)
            canvas = canvas.filter(ImageFilter.SHARPEN)  # 2회 적용으로 더 선명하게

            print(f"  ✅ 배경 이미지 로드 + 샤프닝 적용: {background_image_path}")
        else:
            # 폴백: 빈 캔버스 생성 (배경 그리기)
            canvas = Image.new('RGB', (self.WIDTH, self.HEIGHT), 'white')
            self._draw_background(canvas, style, brand_colors)

        # 2. 반투명 오버레이 (텍스트 가독성 향상, 선택사항)
        if background_image_path:
            self._add_darkening_overlay(canvas, opacity=0.3)

        # 3. 텍스트 추가 (TED 스타일: 중앙 또는 커스텀 위치)
        self._draw_ted_text(canvas, main_text, subtitle_text, text_position, brand_colors)

        # 4. 채널 아이콘 추가 (좌하단, 원형)
        if channel_icon_path and os.path.exists(channel_icon_path):
            self._add_channel_icon(canvas, channel_icon_path)

        # 5. 배지 추가
        if sentence_count is not None and sentence_count > 0:
            self._add_sentence_badge(canvas, sentence_count)

        if video_duration:
            self._add_duration_badge(canvas, video_duration)

        # 저장
        output_path = self.output_dir / f'thumbnail_{hash(main_text)}.png'
        canvas.save(output_path, 'PNG', quality=95)

        print(f"✅ TED 스타일 썸네일 생성: {output_path}")
        return str(output_path)

    def _draw_background(
        self,
        canvas: Image.Image,
        style: str,
        brand_colors: Optional[dict]
    ):
        """배경 그리기 (그라데이션 또는 단색)"""
        draw = ImageDraw.Draw(canvas)

        if style == 'fire_english':
            # 빨간색 헤더 + 흰색 배경
            header_color = brand_colors.get('primary', '#D32F2F') if brand_colors else '#D32F2F'

            # 헤더 (상단 120px)
            draw.rectangle([0, 0, self.WIDTH, 120], fill=header_color)

            # 나머지 흰색
            draw.rectangle([0, 120, self.WIDTH, self.HEIGHT], fill='#FFFFFF')

        elif style == 'minimalist':
            # 밝은 회색 단색
            draw.rectangle([0, 0, self.WIDTH, self.HEIGHT], fill='#F5F5F5')

        elif style == 'bold_bright':
            # 화려한 그라데이션 (PIL은 직접 그라데이션 지원 안 함, 간단히 처리)
            top_color = (233, 30, 99)  # 핑크
            bottom_color = (255, 235, 59)  # 노란색

            for y in range(self.HEIGHT):
                ratio = y / self.HEIGHT
                r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                draw.line([(0, y), (self.WIDTH, y)], fill=(r, g, b))

        else:
            # 기본 배경 (흰색)
            draw.rectangle([0, 0, self.WIDTH, self.HEIGHT], fill='#FFFFFF')

    def _add_darkening_overlay(self, canvas: Image.Image, opacity: float = 0.3):
        """
        반투명 어두운 오버레이 추가 (텍스트 가독성 향상)

        Args:
            canvas: 대상 이미지
            opacity: 불투명도 (0.0 = 투명, 1.0 = 완전 불투명)
        """
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, int(255 * opacity)))
        canvas.paste(overlay, (0, 0), overlay)
        print(f"  ✅ 반투명 오버레이 추가 (opacity={opacity})")

    def _add_channel_icon(self, canvas: Image.Image, icon_path: str):
        """
        채널 아이콘 추가 (좌하단, 원형)

        Args:
            canvas: 대상 이미지
            icon_path: 채널 아이콘 파일 경로
        """
        try:
            icon = Image.open(icon_path)

            # 원형 크기 (TED 로고 스타일)
            icon_size = 100  # 지름 100px

            # 정사각형으로 리사이즈
            icon_resized = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

            # 원형 마스크 생성
            mask = Image.new('L', (icon_size, icon_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse([0, 0, icon_size, icon_size], fill=255)

            # RGBA 변환 (투명도 지원)
            if icon_resized.mode != 'RGBA':
                icon_resized = icon_resized.convert('RGBA')

            # 원형으로 자르기
            icon_circle = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            icon_circle.paste(icon_resized, (0, 0), mask)

            # 위치 (좌하단, 30px 여백)
            x = 30
            y = self.HEIGHT - icon_size - 30

            # 흰색 테두리 (선택사항)
            border_size = 4
            border_circle = Image.new('RGBA', (icon_size + border_size * 2, icon_size + border_size * 2), (255, 255, 255, 255))
            border_mask = Image.new('L', (icon_size + border_size * 2, icon_size + border_size * 2), 0)
            draw_border = ImageDraw.Draw(border_mask)
            draw_border.ellipse([0, 0, icon_size + border_size * 2, icon_size + border_size * 2], fill=255)
            border_circle.putalpha(border_mask)

            # 캔버스에 테두리 먼저 붙이기
            canvas.paste(border_circle, (x - border_size, y - border_size), border_circle)

            # 캔버스에 아이콘 붙이기
            canvas.paste(icon_circle, (x, y), icon_circle)

            print(f"  ✅ 채널 아이콘 추가: {icon_size}px (좌하단)")

        except Exception as e:
            print(f"  ⚠️ 채널 아이콘 추가 실패: {e}")

    def _draw_ted_text(
        self,
        canvas: Image.Image,
        main_text: str,
        subtitle_text: str,
        text_position: str,
        brand_colors: Optional[dict]
    ):
        """
        TED 스타일 텍스트 그리기 (중앙 또는 커스텀 위치)
        개선된 디자인: 그라데이션 오버레이 + 강한 텍스트 외곽선 (검은색 박스 제거)

        Args:
            canvas: 대상 이미지
            main_text: 메인 텍스트 (GPT 최적화된 제목)
            subtitle_text: 서브 텍스트
            text_position: 'left', 'center', 'right'
            brand_colors: 브랜드 색상
        """
        draw = ImageDraw.Draw(canvas)

        # 폰트 크기
        main_font_size = 90
        sub_font_size = 50

        try:
            if self.font_path:
                main_font = ImageFont.truetype(self.font_path, main_font_size)
                sub_font = ImageFont.truetype(self.font_path, sub_font_size)
            else:
                main_font = ImageFont.load_default()
                sub_font = ImageFont.load_default()
        except Exception:
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()

        # 텍스트 색상 (흰색, 가독성 높음)
        text_color = '#FFFFFF'

        # 메인 텍스트 위치 계산
        y_main = self.HEIGHT // 2 - 50  # 중앙보다 약간 위

        # 텍스트 크기 계산
        bbox_main = draw.textbbox((0, 0), main_text, font=main_font)
        main_width = bbox_main[2] - bbox_main[0]
        main_height = bbox_main[3] - bbox_main[1]

        # 위치 결정
        if text_position == 'left':
            x_main = 50  # 좌측 정렬
        elif text_position == 'right':
            x_main = self.WIDTH - main_width - 50  # 우측 정렬
        else:  # center
            x_main = (self.WIDTH - main_width) // 2  # 중앙 정렬

        # 개선된 디자인 1: 그라데이션 오버레이 (검은색 박스 제거)
        # 텍스트 영역에만 부드러운 그라데이션 적용
        box_padding = 40
        box_x1 = max(0, x_main - box_padding)
        box_y1 = max(0, y_main - box_padding)
        box_x2 = min(self.WIDTH, x_main + main_width + box_padding)
        box_y2 = y_main + main_height + box_padding

        # 서브 텍스트가 있으면 박스 확장
        if subtitle_text:
            bbox_sub = draw.textbbox((0, 0), subtitle_text, font=sub_font)
            sub_width = bbox_sub[2] - bbox_sub[0]
            box_y2 += 80  # 서브 텍스트 공간

        # 세로 그라데이션 오버레이 (위에서 아래로 어두워짐)
        overlay_box = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay_box)

        gradient_height = box_y2 - box_y1
        for i in range(int(gradient_height)):
            y = box_y1 + i
            if y < 0 or y >= self.HEIGHT:
                continue

            # 그라데이션 알파값 (중앙이 가장 어두움)
            # 중앙 50%에서 최대 불투명도 (120), 위/아래로 갈수록 투명해짐
            center = gradient_height / 2
            distance_from_center = abs(i - center)
            alpha_ratio = 1.0 - (distance_from_center / center) * 0.5  # 0.5~1.0
            alpha = int(120 * alpha_ratio)  # 최대 120 (약 47% 불투명)

            draw_overlay.line(
                [(box_x1, y), (box_x2, y)],
                fill=(0, 0, 0, alpha)
            )

        canvas.paste(overlay_box, (0, 0), overlay_box)

        # 개선된 디자인 2: 강한 텍스트 외곽선 (stroke)
        # 여러 번 그려서 두꺼운 외곽선 효과
        stroke_width = 5  # 외곽선 두께

        # 메인 텍스트 외곽선 (검은색, 8방향 + 대각선)
        for offset_x in range(-stroke_width, stroke_width + 1):
            for offset_y in range(-stroke_width, stroke_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue  # 중앙은 나중에
                draw.text(
                    (x_main + offset_x, y_main + offset_y),
                    main_text,
                    fill='#000000',
                    font=main_font
                )

        # 메인 텍스트 (흰색)
        draw.text((x_main, y_main), main_text, fill=text_color, font=main_font)

        # 서브 텍스트 그리기
        if subtitle_text:
            y_sub = y_main + main_height + 20

            bbox_sub = draw.textbbox((0, 0), subtitle_text, font=sub_font)
            sub_width = bbox_sub[2] - bbox_sub[0]

            if text_position == 'left':
                x_sub = 50
            elif text_position == 'right':
                x_sub = self.WIDTH - sub_width - 50
            else:
                x_sub = (self.WIDTH - sub_width) // 2

            # 서브 텍스트 외곽선 (검은색)
            stroke_width_sub = 4
            for offset_x in range(-stroke_width_sub, stroke_width_sub + 1):
                for offset_y in range(-stroke_width_sub, stroke_width_sub + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text(
                        (x_sub + offset_x, y_sub + offset_y),
                        subtitle_text,
                        fill='#000000',
                        font=sub_font
                    )

            # 서브 텍스트 (금색)
            draw.text((x_sub, y_sub), subtitle_text, fill='#FFD700', font=sub_font)

        print(f"  ✅ TED 텍스트 추가 (개선된 디자인): {text_position} 정렬, 그라데이션 오버레이 + 강한 외곽선")

    def _draw_main_text(
        self,
        canvas: Image.Image,
        text: str,
        style: str,
        brand_colors: Optional[dict]
    ):
        """메인 텍스트 그리기"""
        draw = ImageDraw.Draw(canvas)

        # 폰트 크기 결정
        font_size = 100
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 텍스트 색상
        if style == 'fire_english':
            text_color = '#FFFFFF'  # 헤더에 흰색 텍스트
            y_position = 30  # 헤더 영역
        else:
            text_color = '#000000'
            y_position = 200

        # 텍스트 크기 계산 (PIL 2.x)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 중앙 정렬
        x = (self.WIDTH - text_width) // 2

        # 그림자 효과
        shadow_offset = 4
        draw.text(
            (x + shadow_offset, y_position + shadow_offset),
            text,
            fill='#000000',
            font=font
        )

        # 메인 텍스트
        draw.text((x, y_position), text, fill=text_color, font=font)

    def _draw_subtitle_text(
        self,
        canvas: Image.Image,
        text: str,
        style: str,
        brand_colors: Optional[dict]
    ):
        """서브 텍스트 그리기"""
        draw = ImageDraw.Draw(canvas)

        font_size = 60
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 텍스트 박스 (하단)
        y_position = self.HEIGHT - 150

        # 텍스트 크기
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        x = (self.WIDTH - text_width) // 2

        # 배경 박스 (가독성)
        box_padding = 20
        draw.rectangle(
            [x - box_padding, y_position - box_padding,
             x + text_width + box_padding, y_position + 70],
            fill='#000000',
            outline='#FFD700',
            width=3
        )

        # 텍스트
        draw.text((x, y_position), text, fill='#FFFFFF', font=font)

    def _add_sentence_badge(self, canvas: Image.Image, count: int):
        """문장 개수 배지 (좌상단)"""
        draw = ImageDraw.Draw(canvas)

        # 배지 위치
        badge_x = 30
        badge_y = 150
        badge_size = 80

        # 원형 배지
        draw.ellipse(
            [badge_x, badge_y, badge_x + badge_size, badge_y + badge_size],
            fill='#FF5722',
            outline='#FFFFFF',
            width=4
        )

        # 숫자 텍스트
        font_size = 50
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        text = str(count)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = badge_x + (badge_size - text_width) // 2
        text_y = badge_y + (badge_size - text_height) // 2

        draw.text((text_x, text_y), text, fill='#FFFFFF', font=font)

    def _add_duration_badge(self, canvas: Image.Image, duration: str):
        """영상 길이 배지 (우하단)"""
        draw = ImageDraw.Draw(canvas)

        # 배지 위치
        badge_x = self.WIDTH - 150
        badge_y = self.HEIGHT - 80

        # 배지 크기
        badge_width = 120
        badge_height = 50

        # 둥근 사각형 배지
        draw.rectangle(
            [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
            fill='#000000',
            outline='#FFFFFF',
            width=2
        )

        # 시간 텍스트
        font_size = 30
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), duration, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = badge_x + (badge_width - text_width) // 2
        text_y = badge_y + (badge_height - text_height) // 2

        draw.text((text_x, text_y), duration, fill='#FFFFFF', font=font)


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("YouTube 썸네일 생성 엔진 테스트")
    print("=" * 60)

    engine = YouTubeThumbnailEngine()

    # 테스트 1: Fire English 스타일
    print("\n1️⃣ Fire English 스타일")
    path1 = engine.create_thumbnail(
        main_text='여행영어 마스터',
        subtitle_text='필수 10문장',
        style='fire_english',
        sentence_count=10,
        video_duration='3:42'
    )
    print(f"  저장: {path1}")

    # 테스트 2: 미니멀 스타일
    print("\n2️⃣ 미니멀 스타일")
    path2 = engine.create_thumbnail(
        main_text='Daily English',
        subtitle_text='초보자용',
        style='minimalist',
        sentence_count=5
    )
    print(f"  저장: {path2}")

    print("\n" + "=" * 60)
