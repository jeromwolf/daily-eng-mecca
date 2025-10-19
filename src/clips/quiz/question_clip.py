"""
Quiz question clip (문제 제시 클립)
"""
from moviepy import VideoClip
from src.clips.base_clip import BaseClip


class QuestionClip(BaseClip):
    """퀴즈 문제 제시 클립 (TTS 재생만, pause 제외)"""

    def create(self, question: str, option_a: str, option_b: str, duration: float) -> VideoClip:
        """
        문제 제시 클립 생성

        Args:
            question: 퀴즈 문제
            option_a: 선택지 A
            option_b: 선택지 B
            duration: 지속 시간 (TTS only, pause 제외)

        Returns:
            VideoClip: 문제 제시 클립
        """
        # 배경
        bg = self.create_background(
            color=self.settings.Colors.QUIZ_QUESTION_BG,
            duration=duration
        )

        # 문제 텍스트
        question_txt = self.create_text(
            text=question,
            font_size=self.settings.Quiz.Question.QUESTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Question.QUESTION_Y),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        # 선택지 A
        option_a_txt = self.create_text(
            text=f"A. {option_a}",
            font_size=self.settings.Quiz.Question.OPTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=(self.settings.Quiz.Question.OPTION_X, self.settings.Quiz.Question.OPTION_A_Y),
            duration=duration,
            size=(self.width - 160, None),
            method='caption',
            text_align='left'
        )

        # 선택지 B
        option_b_txt = self.create_text(
            text=f"B. {option_b}",
            font_size=self.settings.Quiz.Question.OPTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=(self.settings.Quiz.Question.OPTION_X, self.settings.Quiz.Question.OPTION_B_Y),
            duration=duration,
            size=(self.width - 160, None),
            method='caption',
            text_align='left'
        )

        return self.compose([bg, question_txt, option_a_txt, option_b_txt])
