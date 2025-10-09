"""
UI 효과음 (클릭, 알림, 호버 등)
"""
import numpy as np
from .base_effect import BaseEffect


class ClickSound(BaseEffect):
    """클릭 효과음 (짧고 경쾌한)"""

    def generate(self) -> np.ndarray:
        """
        클릭 효과음 생성

        특징:
        - 매우 짧음 (0.05초)
        - 높은 주파수 (경쾌함)
        - 빠른 attack/release

        Returns:
            오디오 샘플 배열
        """
        duration = 0.05

        # 높은 톤 (C6)
        audio = self.generate_tone(1046.50, duration, volume=0.3)

        # 매우 빠른 ADSR
        audio = self.apply_adsr(audio, attack=0.001, decay=0.01, sustain=0.3, release=0.02)

        return audio


class HoverSound(BaseEffect):
    """호버 효과음 (부드러운)"""

    def generate(self) -> np.ndarray:
        """
        호버 효과음 생성

        특징:
        - 짧고 부드러움 (0.08초)
        - 중간 주파수
        - 부드러운 attack

        Returns:
            오디오 샘플 배열
        """
        duration = 0.08

        # 중간 톤 (A5)
        audio = self.generate_tone(880.00, duration, volume=0.2)

        # 부드러운 ADSR
        audio = self.apply_adsr(audio, attack=0.01, decay=0.02, sustain=0.5, release=0.03)

        return audio


class NotificationSound(BaseEffect):
    """알림 효과음 (주의 환기)"""

    def generate(self) -> np.ndarray:
        """
        알림 효과음 생성

        특징:
        - 두 번 반복 (띵-똥)
        - 명확하고 주의를 끄는 느낌
        - 0.5초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.5

        # 첫 번째 톤 (E5)
        tone1 = self.generate_tone(659.25, 0.15, volume=0.4)
        tone1 = self.apply_adsr(tone1, attack=0.01, decay=0.03, sustain=0.6, release=0.05)

        # 두 번째 톤 (C5)
        tone2 = self.generate_tone(523.25, 0.15, volume=0.4)
        tone2 = self.apply_adsr(tone2, attack=0.01, decay=0.03, sustain=0.6, release=0.05)

        # 두 톤 연결
        audio = np.zeros(int(duration * self.sample_rate))
        audio[:len(tone1)] += tone1
        audio[len(tone1)+int(0.05*self.sample_rate):len(tone1)+int(0.05*self.sample_rate)+len(tone2)] += tone2

        return audio


class ErrorSound(BaseEffect):
    """에러 효과음 (명확한 부정)"""

    def generate(self) -> np.ndarray:
        """
        에러 효과음 생성

        특징:
        - 낮은 주파수 하강
        - 명확하게 부정적
        - 0.3초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.3

        # 주파수 하강 (A4 → E4)
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq_start = 440.00  # A4
        freq_end = 329.63    # E4

        freq = np.linspace(freq_start, freq_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate

        audio = 0.5 * np.sin(phase)

        # 빠른 ADSR
        audio = self.apply_adsr(audio, attack=0.01, decay=0.05, sustain=0.4, release=0.1)

        return audio


class SuccessSound(BaseEffect):
    """성공 효과음 (밝고 긍정적)"""

    def generate(self) -> np.ndarray:
        """
        성공 효과음 생성

        특징:
        - 상승하는 코드 (G-B-D)
        - 밝고 긍정적
        - 0.4초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.4

        # G 메이저 코드 (G-B-D)
        g_note = self.generate_tone(392.00, duration, volume=0.4)  # G4
        b_note = self.generate_tone(493.88, duration, volume=0.3)  # B4
        d_note = self.generate_tone(587.33, duration, volume=0.2)  # D5

        audio = g_note + b_note + d_note

        # ADSR
        audio = self.apply_adsr(audio, attack=0.01, decay=0.05, sustain=0.6, release=0.15)

        return audio


class ToggleSound(BaseEffect):
    """토글 효과음 (ON/OFF)"""

    def generate(self) -> np.ndarray:
        """
        토글 효과음 생성

        특징:
        - 짧은 펄스 (0.06초)
        - 중립적인 톤

        Returns:
            오디오 샘플 배열
        """
        duration = 0.06

        # 중간 톤 (C5)
        audio = self.generate_square_wave(523.25, duration, volume=0.3)

        # ADSR
        audio = self.apply_adsr(audio, attack=0.005, decay=0.01, sustain=0.5, release=0.02)

        return audio
