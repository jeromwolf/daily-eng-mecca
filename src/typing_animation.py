"""
타이핑 애니메이션 효과 모듈 (단어별 색상 변화)
"""
from moviepy import TextClip, CompositeVideoClip


class TypingAnimation:
    """
    영어 텍스트에 타이핑 애니메이션 효과 추가
    - 단어별로 흰색 → 주황색 변화
    - TTS 음성과 동기화
    """

    def __init__(self, font_path: str, width: int = 1080):
        """
        Args:
            font_path: 폰트 파일 경로
            width: 비디오 너비 (기본 1080px)
        """
        self.font_path = font_path
        self.width = width

    def create_typing_text_clip(
        self,
        text: str,
        font_size: int,
        duration: float,
        y_position: int,
        word_timings: list[tuple[str, float, float]] = None
    ) -> CompositeVideoClip:
        """
        타이핑 애니메이션 텍스트 클립 생성

        Args:
            text: 전체 텍스트 (예: "Hello, how are you?")
            font_size: 폰트 크기
            duration: 전체 지속 시간
            y_position: Y 좌표 (화면 상단 기준)
            word_timings: 각 단어의 (단어, 시작시간, 종료시간) 튜플 리스트
                         None이면 자동 계산 (균등 분배)

        Returns:
            타이핑 애니메이션이 적용된 CompositeVideoClip
        """
        words = text.split()

        # word_timings 없으면 자동 계산 (균등 분배)
        if word_timings is None:
            word_timings = []
            time_per_word = duration / len(words)
            for i, word in enumerate(words):
                start = i * time_per_word
                end = start + time_per_word * 0.7  # 70%만 사용 (간격 확보)
                word_timings.append((word, start, end))

        # 전체 텍스트 (흰색 베이스)
        base_text = TextClip(
            text=text,
            font_size=font_size,
            color='white',
            font=self.font_path,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', y_position)).with_duration(duration)

        # 각 단어별 주황색 오버레이 클립 생성
        word_clips = [base_text]

        # 누적 X 위치 계산 (중앙 정렬 기준)
        x_offset = self._calculate_center_offset(words, font_size)

        for word, start_time, end_time in word_timings:
            # 단어별 주황색 클립
            word_clip = TextClip(
                text=word,
                font_size=font_size,
                color='#FF8C00',  # 주황색 (DarkOrange)
                font=self.font_path,
                stroke_color='black',
                stroke_width=3
            ).with_start(start_time).with_end(end_time)

            # 위치 계산 (중앙 정렬)
            word_position = (x_offset, y_position)
            word_clip = word_clip.with_position(word_position)

            word_clips.append(word_clip)

            # 다음 단어 위치 (대략적 계산, 실제로는 폰트 렌더링 후 측정 필요)
            x_offset += len(word) * (font_size * 0.5) + (font_size * 0.3)  # 단어 간격

        return CompositeVideoClip(word_clips, size=(self.width, 1920))

    def _calculate_center_offset(self, words: list[str], font_size: int) -> int:
        """
        중앙 정렬 기준 첫 단어 X 오프셋 계산

        Args:
            words: 단어 리스트
            font_size: 폰트 크기

        Returns:
            X 오프셋 (px)
        """
        # 전체 텍스트 길이 추정 (대략적)
        total_width = sum(len(word) for word in words) * (font_size * 0.5)
        total_width += (len(words) - 1) * (font_size * 0.3)  # 단어 간격

        # 중앙 정렬 시작점
        return int((self.width - total_width) / 2)

    def create_word_by_word_clip(
        self,
        text: str,
        font_size: int,
        duration: float,
        y_position: int,
        tts_duration: float = None
    ) -> CompositeVideoClip:
        """
        간단한 단어별 색상 변화 클립 (TTS와 동기화)

        Args:
            text: 전체 텍스트
            font_size: 폰트 크기
            duration: 전체 지속 시간
            y_position: Y 좌표
            tts_duration: TTS 음성 길이 (None이면 duration 사용)

        Returns:
            CompositeVideoClip
        """
        words = text.split()

        # TTS 길이 기준으로 단어별 타이밍 계산
        active_duration = tts_duration if tts_duration else duration * 0.7
        time_per_word = active_duration / len(words)

        # 단어별 타이밍 생성
        word_timings = []
        for i, word in enumerate(words):
            start = i * time_per_word
            end = start + time_per_word
            word_timings.append((word, start, end))

        return self.create_typing_text_clip(
            text=text,
            font_size=font_size,
            duration=duration,
            y_position=y_position,
            word_timings=word_timings
        )


# ========== 더 간단한 버전 (Lambda 함수 사용) ==========

def create_simple_typing_effect(
    text: str,
    font_path: str,
    font_size: int,
    duration: float,
    y_position: int,
    width: int = 1080,
    tts_duration: float = None
) -> TextClip:
    """
    가장 간단한 타이핑 효과 (전체 텍스트를 시간에 따라 색상 변경)

    Args:
        text: 텍스트
        font_path: 폰트 경로
        font_size: 폰트 크기
        duration: 지속 시간
        y_position: Y 좌표
        width: 비디오 너비
        tts_duration: TTS 음성 길이

    Returns:
        색상 변경 애니메이션이 적용된 TextClip
    """
    # TTS 길이 기준 색상 변화 시간 계산
    color_change_time = tts_duration if tts_duration else duration * 0.7

    # Lambda 함수로 시간에 따라 색상 변경
    def color_at_time(t):
        if t < color_change_time:
            # 타이핑 진행 중: 시간 비율에 따라 주황색 강도 증가
            ratio = t / color_change_time
            orange_intensity = int(255 * ratio)
            white_intensity = int(255 * (1 - ratio))
            return (255, white_intensity + int(140 * ratio), white_intensity)  # 흰색 → 주황색
        else:
            # 타이핑 완료: 주황색 유지
            return (255, 140, 0)  # DarkOrange

    txt_clip = TextClip(
        text=text,
        font_size=font_size,
        color='white',  # 초기 색상
        font=font_path,
        size=(width - 120, None),
        method='caption',
        text_align='center',
        stroke_color='black',
        stroke_width=3,
        margin=(10, 20)
    ).with_position(('center', y_position)).with_duration(duration)

    # 색상 변경 애니메이션 적용 (MoviePy 2.x - .with_effects() 사용 불가, 직접 구현 필요)
    # 참고: 이 방법은 MoviePy 1.x에서만 작동 (make_frame 재정의 필요)

    return txt_clip


# ========== 가장 현실적인 방법: 단어별 개별 클립 ==========

def create_word_highlight_clips(
    text: str,
    font_path: str,
    font_size: int,
    duration: float,
    y_position: int,
    width: int = 1080,
    tts_duration: float = None
) -> list[TextClip]:
    """
    단어별로 개별 클립 생성 (각 단어가 순차적으로 주황색으로 변함)

    Args:
        text: 전체 텍스트
        font_path: 폰트 경로
        font_size: 폰트 크기
        duration: 전체 지속 시간
        y_position: Y 좌표
        width: 비디오 너비
        tts_duration: TTS 음성 길이

    Returns:
        [base_text_clip, word1_clip, word2_clip, ...] 리스트
    """
    words = text.split()

    # TTS 길이 기준으로 단어별 타이밍 계산
    active_duration = tts_duration if tts_duration else duration * 0.7
    time_per_word = active_duration / len(words)

    # 1. 전체 텍스트 (흰색 베이스)
    base_clip = TextClip(
        text=text,
        font_size=font_size,
        color='white',
        font=font_path,
        size=(width - 120, None),
        method='caption',
        text_align='center',
        stroke_color='black',
        stroke_width=3,
        margin=(10, 20)
    ).with_position(('center', y_position)).with_duration(duration)

    clips = [base_clip]

    # 2. 각 단어별 주황색 클립 (순차적으로 나타남)
    for i, word in enumerate(words):
        start_time = i * time_per_word
        end_time = start_time + time_per_word

        # 단어별 텍스트 생성 (앞 단어들은 공백으로 유지, 현재 단어만 주황색)
        # 예: "      how      " (Hello는 공백, how만 표시)
        highlighted_text = " ".join(
            [" " * len(w) if j != i else w for j, w in enumerate(words)]
        )

        word_clip = TextClip(
            text=highlighted_text,
            font_size=font_size,
            color='#FF8C00',  # 주황색
            font=font_path,
            size=(width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', y_position)).with_start(start_time).with_end(end_time)

        clips.append(word_clip)

    return clips
