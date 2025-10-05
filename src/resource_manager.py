"""
리소스(이미지, 오디오) 재활용 관리 모듈
"""
import os
import hashlib
from pathlib import Path


class ResourceManager:
    def __init__(self, resources_dir: str = None):
        """
        ResourceManager 초기화

        Args:
            resources_dir: 리소스 저장 디렉토리 (기본: ./resources)
        """
        if resources_dir is None:
            self.resources_dir = Path(__file__).parent.parent / 'resources'
        else:
            self.resources_dir = Path(resources_dir)

        # 리소스 디렉토리 생성
        self.images_dir = self.resources_dir / 'images'
        self.audio_dir = self.resources_dir / 'audio'
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def _generate_hash(self, text: str) -> str:
        """
        텍스트로부터 해시값 생성

        Args:
            text: 해시할 텍스트

        Returns:
            MD5 해시 문자열
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_image_path(self, prompt: str) -> str:
        """
        이미지 프롬프트에 대한 저장 경로 반환

        Args:
            prompt: DALL-E 프롬프트

        Returns:
            이미지 파일 경로
        """
        hash_value = self._generate_hash(prompt)
        return str(self.images_dir / f"{hash_value}.png")

    def get_audio_path(self, sentence: str, voice: str = "nova") -> str:
        """
        문장에 대한 오디오 저장 경로 반환

        Args:
            sentence: 영어 문장
            voice: TTS 음성

        Returns:
            오디오 파일 경로
        """
        # 문장과 음성을 함께 해시
        hash_value = self._generate_hash(f"{sentence}_{voice}")
        return str(self.audio_dir / f"{hash_value}.mp3")

    def image_exists(self, prompt: str) -> bool:
        """
        이미지가 이미 존재하는지 확인

        Args:
            prompt: DALL-E 프롬프트

        Returns:
            존재 여부
        """
        image_path = self.get_image_path(prompt)
        return Path(image_path).exists()

    def audio_exists(self, sentence: str, voice: str = "nova") -> bool:
        """
        오디오가 이미 존재하는지 확인

        Args:
            sentence: 영어 문장
            voice: TTS 음성

        Returns:
            존재 여부
        """
        audio_path = self.get_audio_path(sentence, voice)
        return Path(audio_path).exists()

    def get_resource_stats(self) -> dict:
        """
        리소스 통계 반환

        Returns:
            통계 정보 딕셔너리
        """
        image_files = list(self.images_dir.glob("*.png"))
        audio_files = list(self.audio_dir.glob("*.mp3"))

        return {
            'total_images': len(image_files),
            'total_audios': len(audio_files),
            'images_dir': str(self.images_dir),
            'audio_dir': str(self.audio_dir)
        }
