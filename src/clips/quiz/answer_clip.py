"""
Quiz answer clip (정답 공개 클립)
"""
from moviepy import VideoClip
from src.clips.base_clip import BaseClip


class AnswerClip(BaseClip):
    """퀴즈 정답 공개 클립"""

    def create(self, answer: str, correct_option: str, duration: float) -> VideoClip:
        """
        정답 공개 클립 생성

        Args:
            answer: 정답 ('A' 또는 'B')
            correct_option: 정답 텍스트
            duration: 지속 시간

        Returns:
            VideoClip: 정답 공개 클립
        """
        # 배경
        bg = self.create_background(
            color=self.settings.Colors.QUIZ_ANSWER_BG,
            duration=duration
        )

        # "정답은" 타이틀
        title_txt = self.create_text(
            text="정답은",
            font_size=self.settings.Quiz.Answer.TITLE_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Answer.TITLE_Y),
            duration=duration
        )

        # 정답 (A 또는 B, 크게)
        answer_txt = self.create_text(
            text=answer,
            font_size=self.settings.Quiz.Answer.ANSWER_FONT_SIZE,
            color=self.settings.Colors.GOLD,
            position=('center', self.settings.Quiz.Answer.ANSWER_Y),
            duration=duration,
            stroke_width=self.settings.Quiz.Answer.ANSWER_STROKE_WIDTH
        )

        # 정답 텍스트 (작게)
        option_txt = self.create_text(
            text=correct_option,
            font_size=self.settings.Quiz.Answer.OPTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Answer.OPTION_Y),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        return self.compose([bg, title_txt, answer_txt, option_txt])
