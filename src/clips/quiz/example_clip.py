"""
Quiz example clip (예문 클립)
"""
from moviepy import VideoClip
from src.clips.base_clip import BaseClip


class ExampleClip(BaseClip):
    """퀴즈 예문 클립"""

    def create(self, example: str, index: int, duration: float) -> VideoClip:
        """
        예문 클립 생성

        Args:
            example: 예문 텍스트
            index: 예문 번호 (1, 2, 3)
            duration: 지속 시간

        Returns:
            VideoClip: 예문 클립
        """
        # 배경
        bg = self.create_background(
            color=self.settings.Colors.QUIZ_EXAMPLE_BG,
            duration=duration
        )

        # "예문" 타이틀
        title_txt = self.create_text(
            text=f"예문 {index}",
            font_size=self.settings.Quiz.Example.TITLE_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Example.TITLE_Y),
            duration=duration
        )

        # "따라해 보세요" 안내
        guide_txt = self.create_text(
            text="따라해 보세요",
            font_size=self.settings.Quiz.Example.GUIDE_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Example.GUIDE_Y),
            duration=duration
        )

        # 예문 내용
        content_txt = self.create_text(
            text=example,
            font_size=self.settings.Quiz.Example.CONTENT_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Example.CONTENT_Y),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        return self.compose([bg, title_txt, guide_txt, content_txt])
