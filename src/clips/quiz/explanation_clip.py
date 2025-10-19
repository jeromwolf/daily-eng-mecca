"""
Quiz explanation clip (해설 클립)
"""
from moviepy import VideoClip
from src.clips.base_clip import BaseClip


class ExplanationClip(BaseClip):
    """퀴즈 해설 클립"""

    def create(self, explanation: str, duration: float) -> VideoClip:
        """
        해설 클립 생성

        Args:
            explanation: 해설 텍스트
            duration: 지속 시간

        Returns:
            VideoClip: 해설 클립
        """
        # 배경
        bg = self.create_background(
            color=self.settings.Colors.QUIZ_EXPLANATION_BG,
            duration=duration
        )

        # "해설" 타이틀
        title_txt = self.create_text(
            text="해설",
            font_size=self.settings.Quiz.Explanation.TITLE_FONT_SIZE,
            color=self.settings.Colors.BLACK,
            position=('center', self.settings.Quiz.Explanation.TITLE_Y),
            duration=duration
        )

        # 해설 내용
        content_txt = self.create_text(
            text=explanation,
            font_size=self.settings.Quiz.Explanation.CONTENT_FONT_SIZE,
            color=self.settings.Colors.BLACK,
            position=('center', self.settings.Quiz.Explanation.CONTENT_Y),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        return self.compose([bg, title_txt, content_txt])
