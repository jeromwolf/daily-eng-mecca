"""
영어 학습용 효과음 (정답, 오답, 칭찬 등)
"""
import numpy as np
from .base_effect import BaseEffect


class CorrectSound(BaseEffect):
    """정답 효과음 (긍정적인, 밝은 코드)"""

    def generate(self) -> np.ndarray:
        """
        정답 효과음 생성

        특징:
        - 밝은 메이저 코드 (C-E-G)
        - 짧고 경쾌함 (0.3초)
        - 긍정적인 느낌

        Returns:
            오디오 샘플 배열
        """
        duration = 0.3

        # C 메이저 코드 (C-E-G)
        c_note = self.generate_tone(523.25, duration, volume=0.4)  # C5
        e_note = self.generate_tone(659.25, duration, volume=0.3)  # E5
        g_note = self.generate_tone(783.99, duration, volume=0.2)  # G5

        # 코드 믹스
        chord = c_note + e_note + g_note

        # ADSR 적용 (빠른 attack, 짧은 release)
        chord = self.apply_adsr(chord, attack=0.01, decay=0.05, sustain=0.6, release=0.1)

        return chord


class WrongSound(BaseEffect):
    """오답 효과음 (부드러운, 중립적인)"""

    def generate(self) -> np.ndarray:
        """
        오답 효과음 생성

        특징:
        - 부드러운 사인파 하강
        - 너무 부정적이지 않음
        - 짧고 명확함 (0.2초)

        Returns:
            오디오 샘플 배열
        """
        duration = 0.2

        # 주파수 하강 (E4 → C4)
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        freq_start = 329.63  # E4
        freq_end = 261.63    # C4

        # 선형 주파수 변화
        freq = np.linspace(freq_start, freq_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate

        audio = 0.4 * np.sin(phase)

        # ADSR 적용
        audio = self.apply_adsr(audio, attack=0.01, decay=0.03, sustain=0.5, release=0.05)

        return audio


class CelebrationSound(BaseEffect):
    """축하 효과음 (화려한, 연속 코드)"""

    def generate(self) -> np.ndarray:
        """
        축하 효과음 생성

        특징:
        - 상승하는 아르페지오 (C-E-G-C)
        - 화려하고 긍정적
        - 1초 길이

        Returns:
            오디오 샘플 배열
        """
        duration = 1.0

        # 아르페지오 음표들 (C-E-G-C, 한 옥타브 위)
        notes = [
            (261.63, 0.15, 0.5),  # C4
            (329.63, 0.15, 0.5),  # E4
            (392.00, 0.15, 0.5),  # G4
            (523.25, 0.25, 0.6),  # C5 (마지막은 길게)
        ]

        audio = np.zeros(int(duration * self.sample_rate))
        current_pos = 0

        for freq, note_dur, vol in notes:
            # 각 음표 생성
            note = self.generate_tone(freq, note_dur, volume=vol)
            note = self.apply_adsr(note, attack=0.01, decay=0.03, sustain=0.7, release=0.05)

            # 오디오에 추가
            start = int(current_pos * self.sample_rate)
            end = start + len(note)

            if end > len(audio):
                note = note[:len(audio) - start]
                end = len(audio)

            audio[start:end] += note
            current_pos += note_dur * 0.7  # 약간 겹치게

        # 전체 페이드 아웃
        audio = self.apply_fade(audio, fade_in=0.01, fade_out=0.2)

        return audio


class EncouragementSound(BaseEffect):
    """격려 효과음 (따뜻한, 부드러운)"""

    def generate(self) -> np.ndarray:
        """
        격려 효과음 생성

        특징:
        - 따뜻한 메이저 코드
        - 중간 속도
        - 부드러운 ADSR

        Returns:
            오디오 샘플 배열
        """
        duration = 0.5

        # F 메이저 코드 (F-A-C)
        f_note = self.generate_tone(349.23, duration, volume=0.3)  # F4
        a_note = self.generate_tone(440.00, duration, volume=0.3)  # A4
        c_note = self.generate_tone(523.25, duration, volume=0.2)  # C5

        # 코드 믹스
        chord = f_note + a_note + c_note

        # 부드러운 ADSR
        chord = self.apply_adsr(chord, attack=0.05, decay=0.1, sustain=0.6, release=0.2)

        return chord


class StartSound(BaseEffect):
    """시작 효과음 (경쾌한, 주의 환기)"""

    def generate(self) -> np.ndarray:
        """
        시작 효과음 생성

        특징:
        - 짧은 벨 사운드
        - 주의를 끄는 느낌
        - 0.3초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.3

        # 높은 음 (E5 + G5)
        e_note = self.generate_tone(659.25, duration, volume=0.5)
        g_note = self.generate_tone(783.99, duration, volume=0.3)

        audio = e_note + g_note

        # 빠른 decay
        audio = self.apply_adsr(audio, attack=0.005, decay=0.05, sustain=0.3, release=0.1)

        return audio


class FinishSound(BaseEffect):
    """완료 효과음 (만족스러운, 끝맺음)"""

    def generate(self) -> np.ndarray:
        """
        완료 효과음 생성

        특징:
        - 하강하는 코드 (G→C)
        - 만족스러운 해결감
        - 0.6초

        Returns:
            오디오 샘플 배열
        """
        duration = 0.6

        # G → C 진행 (해결감)
        g_chord = self.generate_tone(392.00, 0.3, volume=0.4) + \
                  self.generate_tone(493.88, 0.3, volume=0.3)  # G4 + B4

        c_chord = self.generate_tone(261.63, 0.3, volume=0.5) + \
                  self.generate_tone(329.63, 0.3, volume=0.4) + \
                  self.generate_tone(392.00, 0.3, volume=0.3)  # C4 + E4 + G4

        # 두 코드 연결
        audio = np.zeros(int(duration * self.sample_rate))
        g_len = len(g_chord)
        c_len = len(c_chord)

        audio[:g_len] += g_chord
        audio[g_len:g_len+c_len] += c_chord

        # ADSR
        audio = self.apply_adsr(audio, attack=0.01, decay=0.1, sustain=0.7, release=0.2)

        return audio
