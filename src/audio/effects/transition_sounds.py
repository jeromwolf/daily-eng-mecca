"""
전환 효과음 (씬 전환, 슬라이드 등)
"""
import numpy as np
from .base_effect import BaseEffect


class WhooshSound(BaseEffect):
    """휙 지나가는 소리 (씬 전환)"""

    def generate(self) -> np.ndarray:
        """
        Whoosh 효과음 생성

        특징:
        - 화이트 노이즈 기반
        - 주파수 변조
        - 빠른 페이드 인/아웃
        - 0.5초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.5

        # 화이트 노이즈 생성
        audio = self.generate_white_noise(duration, volume=0.4)

        # 주파수 필터 (고주파 통과 → 저주파 통과)
        t = np.linspace(0, duration, len(audio))

        # 간단한 볼륨 엔벨로프 (빠른 페이드)
        envelope = np.exp(-10 * (t - 0.25) ** 2)  # 가우시안 엔벨로프
        audio = audio * envelope

        # 페이드 적용
        audio = self.apply_fade(audio, fade_in=0.05, fade_out=0.1)

        return audio


class SwipeSound(BaseEffect):
    """스와이프 효과음 (부드러운 전환)"""

    def generate(self) -> np.ndarray:
        """
        스와이프 효과음 생성

        특징:
        - 주파수 상승
        - 부드러운 느낌
        - 0.3초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.3

        # 주파수 상승 (C4 → C5)
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq_start = 261.63  # C4
        freq_end = 523.25    # C5

        freq = np.linspace(freq_start, freq_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate

        audio = 0.3 * np.sin(phase)

        # 부드러운 ADSR
        audio = self.apply_adsr(audio, attack=0.02, decay=0.05, sustain=0.6, release=0.1)

        return audio


class PopSound(BaseEffect):
    """팝 효과음 (나타남)"""

    def generate(self) -> np.ndarray:
        """
        팝 효과음 생성

        특징:
        - 짧은 펄스
        - 높은 주파수
        - 0.1초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.1

        # 높은 톤 (C6)
        audio = self.generate_tone(1046.50, duration, volume=0.4)

        # 매우 빠른 attack
        audio = self.apply_adsr(audio, attack=0.001, decay=0.02, sustain=0.3, release=0.05)

        return audio


class SlideSound(BaseEffect):
    """슬라이드 효과음 (부드러운 이동)"""

    def generate(self) -> np.ndarray:
        """
        슬라이드 효과음 생성

        특징:
        - 주파수 선형 이동
        - 부드러운 사인파
        - 0.4초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.4

        # 주파수 이동 (E4 → A4)
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq_start = 329.63  # E4
        freq_end = 440.00    # A4

        freq = np.linspace(freq_start, freq_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate

        audio = 0.3 * np.sin(phase)

        # ADSR
        audio = self.apply_adsr(audio, attack=0.02, decay=0.05, sustain=0.7, release=0.1)

        return audio


class FadeTransitionSound(BaseEffect):
    """페이드 전환 효과음 (점진적)"""

    def generate(self) -> np.ndarray:
        """
        페이드 전환 효과음 생성

        특징:
        - 부드러운 톤
        - 긴 페이드 아웃
        - 0.8초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.8

        # 중간 톤 (G4)
        audio = self.generate_tone(392.00, duration, volume=0.3)

        # 긴 페이드 아웃
        audio = self.apply_fade(audio, fade_in=0.1, fade_out=0.4)

        return audio


class PageTurnSound(BaseEffect):
    """페이지 넘김 효과음"""

    def generate(self) -> np.ndarray:
        """
        페이지 넘김 효과음 생성

        특징:
        - 화이트 노이즈 기반
        - 짧은 burst
        - 0.2초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.2

        # 화이트 노이즈
        audio = self.generate_white_noise(duration, volume=0.2)

        # 빠른 envelope
        t = np.linspace(0, duration, len(audio))
        envelope = np.exp(-15 * t)  # 빠른 감소
        audio = audio * envelope

        return audio
