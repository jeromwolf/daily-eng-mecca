"""
OpenAI TTS를 사용한 음성 생성 모듈
"""
import os
from openai import OpenAI
from pathlib import Path
from .resource_manager import ResourceManager


class TTSGenerator:
    def __init__(self, api_key: str = None, use_cache: bool = True, resource_manager=None):
        """
        TTSGenerator 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
            use_cache: 리소스 캐싱 사용 여부
            resource_manager: ResourceManager 인스턴스 (선택사항, 없으면 자동 생성)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.use_cache = use_cache
        self.resource_manager = resource_manager if resource_manager else (ResourceManager() if use_cache else None)

    def generate_speech(self, text: str, output_path: str, voice: str = "nova") -> str:
        """
        텍스트를 음성으로 변환 (캐싱 지원)

        Args:
            text: 음성으로 변환할 텍스트
            output_path: 음성 파일 저장 경로
            voice: 음성 종류 (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            생성된 음성 파일 경로
        """
        try:
            # 캐싱 사용 시, 이미 존재하는지 확인
            if self.use_cache and self.resource_manager:
                cached_path = self.resource_manager.get_audio_path(text, voice)
                if self.resource_manager.audio_exists(text, voice):
                    print(f"✓ 캐시된 오디오 사용: {text[:50]}...")
                    # 캐시된 오디오를 output_path로 복사
                    import shutil
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(cached_path, output_path)
                    return output_path

            print(f"음성 생성 중: {text[:50]}...")

            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )

            # output_path에 저장
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            response.stream_to_file(output_path)

            # 캐싱 사용 시, 리소스 폴더에도 저장
            if self.use_cache and self.resource_manager:
                cached_path = self.resource_manager.get_audio_path(text, voice)
                import shutil
                shutil.copy(output_path, cached_path)

            print(f"✓ 음성 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ 음성 생성 실패: {e}")
            raise

    def generate_speech_for_sentences(self, sentences: list[str], output_path: str,
                                     voice: str = "nova", add_pauses: bool = True) -> str:
        """
        여러 문장을 하나의 음성 파일로 변환

        Args:
            sentences: 영어 문장 리스트
            output_path: 음성 파일 저장 경로
            voice: 음성 종류
            add_pauses: 문장 사이에 일시정지 추가 여부

        Returns:
            생성된 음성 파일 경로
        """
        # 문장들을 하나의 텍스트로 결합 (각 문장 후 일시정지 추가)
        if add_pauses:
            # SSML 스타일 일시정지를 텍스트로 표현 (,로 약간의 pause 효과)
            combined_text = " ... ".join(sentences)
        else:
            combined_text = " ".join(sentences)

        return self.generate_speech(combined_text, output_path, voice)

    def get_audio_duration(self, audio_path: str) -> float:
        """
        오디오 파일의 길이를 반환

        Args:
            audio_path: 오디오 파일 경로

        Returns:
            오디오 길이 (초)
        """
        try:
            from moviepy import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
        except Exception as e:
            print(f"오디오 길이 측정 실패: {e}")
            return 0.0

    def generate_speech_per_sentence(self, sentences: list[str], output_dir: str,
                                    voice: str = "nova") -> list[dict]:
        """
        각 문장별로 개별 음성 파일을 생성하고 duration 정보 반환

        Args:
            sentences: 영어 문장 리스트
            output_dir: 음성 파일 저장 디렉토리
            voice: 음성 종류

        Returns:
            각 문장별 정보 리스트 [{'path': str, 'duration': float}, ...]
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        audio_info = []

        for idx, sentence in enumerate(sentences):
            audio_path = Path(output_dir) / f"sentence_{idx+1}.mp3"

            # 음성 생성
            self.generate_speech(sentence, str(audio_path), voice)

            # duration 측정
            duration = self.get_audio_duration(str(audio_path))

            audio_info.append({
                'path': str(audio_path),
                'duration': duration,
                'sentence': sentence
            })

            print(f"  문장 {idx+1}: {duration:.2f}초")

        return audio_info

    def generate_speech_per_sentence_multi_voice(
        self,
        sentences: list[str],
        output_dir: str,
        voices: list[str] = None
    ) -> list[dict]:
        """
        각 문장을 여러 음성으로 생성 (학습 효과 향상)

        Args:
            sentences: 영어 문장 리스트
            output_dir: 음성 파일 저장 디렉토리
            voices: 음성 리스트 (기본값: ["alloy", "nova", "shimmer"])

        Returns:
            각 문장별 정보 리스트
            [
                {
                    'sentence': str,
                    'voices': {
                        'alloy': {'path': str, 'duration': float},
                        'nova': {'path': str, 'duration': float},
                        'shimmer': {'path': str, 'duration': float}
                    }
                },
                ...
            ]
        """
        if voices is None:
            voices = ["alloy", "nova", "shimmer"]

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        audio_info = []

        for idx, sentence in enumerate(sentences):
            sentence_info = {
                'sentence': sentence,
                'voices': {}
            }

            print(f"\n문장 {idx+1}/{len(sentences)}: {sentence}")

            for voice in voices:
                audio_path = Path(output_dir) / f"sentence_{idx+1}_{voice}.mp3"

                # 음성 생성
                self.generate_speech(sentence, str(audio_path), voice)

                # duration 측정
                duration = self.get_audio_duration(str(audio_path))

                sentence_info['voices'][voice] = {
                    'path': str(audio_path),
                    'duration': duration
                }

                print(f"  {voice}: {duration:.2f}초")

            audio_info.append(sentence_info)

        return audio_info
