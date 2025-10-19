"""
셜록 스타일 오프닝 음악 생성기 (numpy 기반)
"""
import numpy as np
import wave
from pathlib import Path


class SherlockMusicGenerator:
    """셜록 스타일 탐정 음악 생성기"""

    def __init__(self, output_dir: str):
        """
        SherlockMusicGenerator 초기화

        Args:
            output_dir: 음악 파일 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = 44100  # 44.1kHz

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

    def generate_sawtooth(self, frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """
        톱니파 생성 (바이올린 느낌)

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

    def apply_adsr(self, audio: np.ndarray, attack: float = 0.1, decay: float = 0.1,
                   sustain: float = 0.7, release: float = 0.2) -> np.ndarray:
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
        duration = length / self.sample_rate

        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = length - attack_samples - decay_samples - release_samples

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

    def generate_sherlock_intro(self, duration: float = 3.0) -> str:
        """
        셜록 스타일 오프닝 음악 생성 (3초)

        특징:
        - 극적인 바이올린 스타일 (높은 음역)
        - 빠른 템포 (180-200 BPM)
        - 미스터리/긴장감
        - 전자음과 현악기 믹스

        Args:
            duration: 음악 길이 (초)

        Returns:
            생성된 파일 경로
        """
        print(f"\n셜록 스타일 오프닝 음악 생성 중... ({duration}초)")

        # 전체 길이 초기화
        total_samples = int(duration * self.sample_rate)
        audio = np.zeros(total_samples)

        # 1. 메인 멜로디 (높은 음역 - 바이올린 스타일)
        # E5 - F#5 - G#5 - E5 패턴 (셜록 테마와 유사)
        melody_notes = [
            (659.25, 0.3, 0.6),   # E5 - 시작
            (739.99, 0.3, 0.6),   # F#5
            (830.61, 0.4, 0.7),   # G#5 - 강조
            (659.25, 0.3, 0.6),   # E5
            (587.33, 0.3, 0.5),   # D5
            (523.25, 0.3, 0.5),   # C5
            (659.25, 0.5, 0.6),   # E5 - 마무리
        ]

        current_pos = 0
        for freq, dur, vol in melody_notes:
            if current_pos >= duration:
                break

            # 톱니파로 바이올린 느낌
            note = self.generate_sawtooth(freq, dur, vol)
            note = self.apply_adsr(note, attack=0.03, decay=0.05, sustain=0.7, release=0.05)

            # 오디오에 추가
            start = int(current_pos * self.sample_rate)
            end = start + len(note)
            if end > len(audio):
                note = note[:len(audio) - start]
                end = len(audio)

            audio[start:end] += note
            current_pos += dur

        # 2. 베이스 라인 (낮은 음역)
        bass_notes = [
            (82.41, 0.5, 0.3),    # E2
            (110.00, 0.5, 0.3),   # A2
            (82.41, 0.5, 0.3),    # E2
            (73.42, 0.5, 0.3),    # D2
            (82.41, 0.5, 0.3),    # E2
            (98.00, 0.5, 0.3),    # G2
        ]

        current_pos = 0
        for freq, dur, vol in bass_notes:
            if current_pos >= duration:
                break

            # 사인파로 베이스
            note = self.generate_tone(freq, dur, vol * 0.4)  # 베이스 볼륨 낮춤
            note = self.apply_adsr(note, attack=0.01, decay=0.02, sustain=0.8, release=0.02)

            # 오디오에 추가
            start = int(current_pos * self.sample_rate)
            end = start + len(note)
            if end > len(audio):
                note = note[:len(audio) - start]
                end = len(audio)

            audio[start:end] += note
            current_pos += dur

        # 3. 리듬 펄스 (전자음)
        pulse_freq = 440  # A4
        pulse_dur = 0.15
        pulse_interval = 0.4

        current_pos = 0
        while current_pos < duration:
            pulse = self.generate_tone(pulse_freq, pulse_dur, 0.2)
            pulse = self.apply_adsr(pulse, attack=0.01, decay=0.01, sustain=0.6, release=0.01)

            start = int(current_pos * self.sample_rate)
            end = start + len(pulse)
            if end > len(audio):
                pulse = pulse[:len(audio) - start]
                end = len(audio)

            audio[start:end] += pulse
            current_pos += pulse_interval

        # 4. 정규화 및 최종 믹스 처리
        # 클리핑 방지
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.9  # 90%로 정규화

        # 페이드 인/아웃
        fade_in_samples = int(0.1 * self.sample_rate)
        fade_out_samples = int(0.2 * self.sample_rate)

        audio[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
        audio[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

        # 5. WAV 파일로 저장
        output_path = self.output_dir / "sherlock_intro.wav"

        # int16으로 변환 (-32768 ~ 32767)
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        print(f"✓ 셜록 스타일 음악 생성 완료!")
        print(f"  - 파일: {output_path}")
        print(f"  - 길이: {duration}초")
        print(f"  - 크기: {output_path.stat().st_size / 1024:.1f} KB")
        print(f"  - 특징: 극적인 바이올린 스타일, 빠른 템포, 미스터리 분위기")

        return str(output_path)

    def generate_netflix_tadum(self, duration: float = 2.5) -> str:
        """
        넷플릭스 "두둥" 스타일 인트로

        특징:
        - 강렬한 저음 베이스 임팩트
        - 두 번의 타격음 ("Ta" + "Dum")
        - 리버브 효과
        - 브랜드 각인 효과

        Args:
            duration: 음악 길이 (초)

        Returns:
            생성된 파일 경로
        """
        print(f"\n넷플릭스 스타일 '두둥' 인트로 생성 중... ({duration}초)")

        total_samples = int(duration * self.sample_rate)
        audio = np.zeros(total_samples)

        # 첫 번째 타격음 "Ta" (높은 음 - C5, 더 높게)
        ta_freq = 523.25  # C5 (더 선명하고 밝은 고음)
        ta_duration = 0.15
        ta_start = 0.0

        # 고음과 배음 혼합
        ta_sound = self.generate_tone(ta_freq, ta_duration, 0.8)
        ta_harmonic = self.generate_tone(ta_freq * 2, ta_duration, 0.4)  # 옥타브 위
        ta_sound += ta_harmonic

        ta_sound = self.apply_adsr(ta_sound, attack=0.005, decay=0.03, sustain=0.2, release=0.05)

        # 오디오에 추가
        ta_start_sample = int(ta_start * self.sample_rate)
        ta_end_sample = ta_start_sample + len(ta_sound)
        if ta_end_sample > len(audio):
            ta_sound = ta_sound[:len(audio) - ta_start_sample]
            ta_end_sample = len(audio)
        audio[ta_start_sample:ta_end_sample] += ta_sound

        # 두 번째 타격음 - 경쾌한 벨 사운드 (E5 - G5 코드)
        dum_duration = 0.8
        dum_start = 0.1

        # 밝은 코드 (E5 - G5 - B5)
        chord_freqs = [659.25, 783.99, 987.77]  # E5, G5, B5
        dum_sound = np.zeros(int(dum_duration * self.sample_rate))

        for i, freq in enumerate(chord_freqs):
            tone = self.generate_tone(freq, dum_duration, 0.6 - i * 0.1)
            tone = self.apply_adsr(tone, attack=0.01, decay=0.1, sustain=0.4, release=0.3)
            dum_sound += tone

        # 오디오에 추가
        dum_start_sample = int(dum_start * self.sample_rate)
        dum_end_sample = dum_start_sample + len(dum_sound)
        if dum_end_sample > len(audio):
            dum_sound = dum_sound[:len(audio) - dum_start_sample]
            dum_end_sample = len(audio)
        audio[dum_start_sample:dum_end_sample] += dum_sound

        # 리버브 효과 (간단한 에코)
        delay_samples = int(0.1 * self.sample_rate)  # 100ms 딜레이
        if delay_samples < len(audio):
            reverb = np.zeros(len(audio))
            reverb[delay_samples:] = audio[:-delay_samples] * 0.3
            audio += reverb

        # 정규화
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95

        # 페이드 아웃 (자연스럽게)
        fade_out_samples = int(0.8 * self.sample_rate)
        if fade_out_samples < len(audio):
            audio[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

        # 저장
        output_path = self.output_dir / "netflix_intro.wav"
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        print(f"✓ 넷플릭스 스타일 '두둥' 생성 완료!")
        print(f"  - 파일: {output_path}")
        print(f"  - 길이: {duration}초")
        print(f"  - 크기: {output_path.stat().st_size / 1024:.1f} KB")
        print(f"  - 특징: 강렬한 베이스 임팩트, 브랜드 각인 효과")

        return str(output_path)


if __name__ == "__main__":
    # 테스트
    import os

    # 절대 경로 사용
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "output", "resources")

    generator = SherlockMusicGenerator(output_dir)

    # 셜록 스타일 생성
    sherlock_path = generator.generate_sherlock_intro(duration=3.0)

    print(f"\n📁 생성된 파일 경로:")
    print(f"   {sherlock_path}")
