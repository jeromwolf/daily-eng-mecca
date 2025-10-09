"""
효과음 생성 기본 클래스 (numpy 기반)
"""
from abc import ABC, abstractmethod
import numpy as np
import wave
from pathlib import Path
from typing import Optional


class BaseEffect(ABC):
    """효과음 생성 추상 클래스"""

    def __init__(self, sample_rate: int = 44100):
        """
        BaseEffect 초기화

        Args:
            sample_rate: 샘플링 레이트 (기본 44.1kHz)
        """
        self.sample_rate = sample_rate

    @abstractmethod
    def generate(self) -> np.ndarray:
        """
        효과음 생성 (추상 메서드)

        Returns:
            numpy 배열 (오디오 샘플)
        """
        pass

    def generate_tone(self, frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """
        사인파 톤 생성

        Args:
            frequency: 주파수 (Hz)
            duration: 지속 시간 (초)
            volume: 볼륨 (0.0~1.0)

        Returns:
            오디오 샘플 배열
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave_data = volume * np.sin(2 * np.pi * frequency * t)
        return wave_data

    def generate_square_wave(self, frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """
        사각파 생성 (8bit 게임 느낌)

        Args:
            frequency: 주파수 (Hz)
            duration: 지속 시간 (초)
            volume: 볼륨 (0.0~1.0)

        Returns:
            오디오 샘플 배열
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave_data = volume * np.sign(np.sin(2 * np.pi * frequency * t))
        return wave_data

    def generate_sawtooth(self, frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """
        톱니파 생성

        Args:
            frequency: 주파수 (Hz)
            duration: 지속 시간 (초)
            volume: 볼륨 (0.0~1.0)

        Returns:
            오디오 샘플 배열
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave_data = volume * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        return wave_data

    def generate_white_noise(self, duration: float, volume: float = 0.3) -> np.ndarray:
        """
        화이트 노이즈 생성

        Args:
            duration: 지속 시간 (초)
            volume: 볼륨 (0.0~1.0)

        Returns:
            오디오 샘플 배열
        """
        samples = int(self.sample_rate * duration)
        wave_data = volume * np.random.uniform(-1, 1, samples)
        return wave_data

    def apply_adsr(
        self,
        audio: np.ndarray,
        attack: float = 0.01,
        decay: float = 0.05,
        sustain: float = 0.7,
        release: float = 0.1
    ) -> np.ndarray:
        """
        ADSR 엔벨로프 적용

        Args:
            audio: 오디오 샘플 배열
            attack: Attack 시간 (초)
            decay: Decay 시간 (초)
            sustain: Sustain 레벨 (0.0~1.0)
            release: Release 시간 (초)

        Returns:
            ADSR이 적용된 오디오 샘플 배열
        """
        length = len(audio)

        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = length - attack_samples - decay_samples - release_samples

        if sustain_samples < 0:
            sustain_samples = 0

        envelope = np.ones(length)

        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        if decay_samples > 0:
            start = attack_samples
            end = start + decay_samples
            envelope[start:end] = np.linspace(1, sustain, decay_samples)

        # Sustain
        if sustain_samples > 0:
            start = attack_samples + decay_samples
            end = start + sustain_samples
            envelope[start:end] = sustain

        # Release
        if release_samples > 0:
            start = length - release_samples
            envelope[start:] = np.linspace(sustain, 0, release_samples)

        return audio * envelope

    def apply_fade(self, audio: np.ndarray, fade_in: float = 0.01, fade_out: float = 0.05) -> np.ndarray:
        """
        페이드 인/아웃 적용

        Args:
            audio: 오디오 샘플 배열
            fade_in: 페이드 인 시간 (초)
            fade_out: 페이드 아웃 시간 (초)

        Returns:
            페이드가 적용된 오디오 샘플 배열
        """
        length = len(audio)
        fade_in_samples = int(fade_in * self.sample_rate)
        fade_out_samples = int(fade_out * self.sample_rate)

        result = audio.copy()

        # Fade in
        if fade_in_samples > 0 and fade_in_samples < length:
            result[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)

        # Fade out
        if fade_out_samples > 0 and fade_out_samples < length:
            result[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

        return result

    def normalize(self, audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
        """
        오디오 정규화

        Args:
            audio: 오디오 샘플 배열
            target_level: 목표 레벨 (0.0~1.0)

        Returns:
            정규화된 오디오 샘플 배열
        """
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * target_level
        return audio

    def save(self, output_path: str, audio: Optional[np.ndarray] = None) -> str:
        """
        WAV 파일로 저장

        Args:
            output_path: 저장 경로
            audio: 오디오 샘플 배열 (None이면 generate() 호출)

        Returns:
            저장된 파일 경로
        """
        if audio is None:
            audio = self.generate()

        # 정규화
        audio = self.normalize(audio)

        # int16으로 변환 (-32768 ~ 32767)
        audio_int16 = (audio * 32767).astype(np.int16)

        # 경로 생성
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # WAV 파일 저장
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return str(output_path)
