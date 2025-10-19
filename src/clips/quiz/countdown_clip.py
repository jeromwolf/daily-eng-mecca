"""
Quiz countdown clip (3-2-1 카운트다운 클립)
"""
from moviepy import VideoClip, TextClip, vfx
from src.clips.base_clip import BaseClip


class CountdownClip(BaseClip):
    """퀴즈 카운트다운 클립 (3-2-1 애니메이션)"""

    def create(self, question: str, option_a: str, option_b: str, duration: float = 3.0) -> VideoClip:
        """
        카운트다운 클립 생성

        Args:
            question: 퀴즈 문제 (상단 표시용)
            option_a: 선택지 A (상단 표시용)
            option_b: 선택지 B (상단 표시용)
            duration: 지속 시간 (기본 3초)

        Returns:
            VideoClip: 카운트다운 클립
        """
        # 배경
        bg = self.create_background(
            color=self.settings.Colors.QUIZ_QUESTION_BG,
            duration=duration
        )

        # 문제 텍스트 (작게, 상단)
        question_txt = self.create_text(
            text=question,
            font_size=self.settings.Quiz.Countdown.QUESTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', self.settings.Quiz.Countdown.QUESTION_Y),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        # 선택지 A (작게, 상단)
        option_a_txt = self.create_text(
            text=f"A. {option_a}",
            font_size=self.settings.Quiz.Countdown.OPTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=(self.settings.Quiz.Countdown.OPTION_X, self.settings.Quiz.Countdown.OPTION_A_Y),
            duration=duration,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_width=self.settings.Text.STROKE_WIDTH_SMALL
        )

        # 선택지 B (작게, 상단)
        option_b_txt = self.create_text(
            text=f"B. {option_b}",
            font_size=self.settings.Quiz.Countdown.OPTION_FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=(self.settings.Quiz.Countdown.OPTION_X, self.settings.Quiz.Countdown.OPTION_B_Y),
            duration=duration,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_width=self.settings.Text.STROKE_WIDTH_SMALL
        )

        # 카운트다운 숫자 생성 (3, 2, 1)
        countdown_clips = []
        for i, number in enumerate(['3', '2', '1'], start=0):
            countdown_txt = TextClip(
                text=number,
                font_size=self.settings.Quiz.Countdown.COUNTDOWN_FONT_SIZE,
                color=self.settings.Colors.GOLD,
                font=self.settings.KOREAN_FONT,
                stroke_color=self.settings.Text.STROKE_COLOR,
                stroke_width=self.settings.Quiz.Countdown.COUNTDOWN_STROKE_WIDTH
            )
            countdown_txt = (
                countdown_txt
                .with_position(('center', self.settings.Quiz.Countdown.COUNTDOWN_Y))
                .with_start(i * 1.0)  # 0초, 1초, 2초에 시작
                .with_duration(1.0)
                .with_effects([vfx.FadeIn(0.1), vfx.FadeOut(0.2)])
            )
            countdown_clips.append(countdown_txt)

        # 모든 요소 합성
        all_clips = [bg, question_txt, option_a_txt, option_b_txt] + countdown_clips
        return self.compose(all_clips)
