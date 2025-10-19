"""
Base clip class with common functionality
"""
from abc import ABC, abstractmethod
from moviepy import VideoClip, ColorClip, TextClip, CompositeVideoClip
from src.config import VideoSettings


class BaseClip(ABC):
    """모든 클립의 베이스 클래스"""

    def __init__(self, width: int = None, height: int = None):
        """
        Args:
            width: 비디오 너비 (기본값: VideoSettings.WIDTH)
            height: 비디오 높이 (기본값: VideoSettings.HEIGHT)
        """
        self.width = width or VideoSettings.WIDTH
        self.height = height or VideoSettings.HEIGHT
        self.settings = VideoSettings

    @abstractmethod
    def create(self, **kwargs) -> VideoClip:
        """
        클립 생성 (서브클래스에서 구현 필수)

        Returns:
            VideoClip: 생성된 비디오 클립
        """
        pass

    def create_background(self, color: tuple, duration: float) -> ColorClip:
        """
        단색 배경 생성

        Args:
            color: RGB 색상 튜플
            duration: 지속 시간

        Returns:
            ColorClip: 배경 클립
        """
        return ColorClip(
            size=(self.width, self.height),
            color=color,
            duration=duration
        )

    def create_text(
        self,
        text: str,
        font_size: int,
        color: str,
        position: tuple,
        duration: float,
        size: tuple = None,
        method: str = None,
        text_align: str = 'center',
        stroke_color: str = None,
        stroke_width: int = None,
        margin: tuple = None
    ) -> TextClip:
        """
        텍스트 클립 생성 (공통 파라미터 처리)

        Args:
            text: 표시할 텍스트
            font_size: 폰트 크기
            color: 텍스트 색상
            position: (x, y) 위치
            duration: 지속 시간
            size: (width, height) 크기 (None이면 자동)
            method: 'caption' 등
            text_align: 텍스트 정렬
            stroke_color: 외곽선 색상
            stroke_width: 외곽선 두께
            margin: (horizontal, vertical) 여백

        Returns:
            TextClip: 텍스트 클립
        """
        # 기본값 설정
        if stroke_color is None:
            stroke_color = self.settings.Text.STROKE_COLOR
        if stroke_width is None:
            stroke_width = self.settings.Text.STROKE_WIDTH
        if margin is None:
            margin = self.settings.Text.MARGIN

        params = {
            'text': text,
            'font_size': font_size,
            'color': color,
            'font': self.settings.KOREAN_FONT,
            'stroke_color': stroke_color,
            'stroke_width': stroke_width,
            'margin': margin
        }

        if size:
            params['size'] = size
        if method:
            params['method'] = method
            params['text_align'] = text_align

        txt_clip = TextClip(**params)
        return txt_clip.with_position(position).with_duration(duration)

    def compose(self, clips: list) -> CompositeVideoClip:
        """
        여러 클립을 합성

        Args:
            clips: VideoClip 리스트

        Returns:
            CompositeVideoClip: 합성된 클립
        """
        return CompositeVideoClip(clips, size=(self.width, self.height))
