"""
비디오 편집 설정 관리 모듈
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """비디오 편집 설정 관리"""

    def __init__(self, config_dir: str):
        """
        ConfigManager 초기화

        Args:
            config_dir: 설정 파일 저장 디렉토리
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def create_default_config(
        self,
        video_id: str,
        sentences: list,
        translations: list,
        image_paths: list,
        tts_data: list
    ) -> Dict[str, Any]:
        """
        기본 편집 설정 생성

        Args:
            video_id: 비디오 ID
            sentences: 영어 문장 리스트
            translations: 한글 번역 리스트
            image_paths: 이미지 경로 리스트
            tts_data: TTS 데이터 리스트

        Returns:
            기본 설정 딕셔너리
        """
        now = datetime.now().isoformat()

        config = {
            "version": "1.0",
            "video_id": video_id,
            "created_at": now,
            "edited_at": now,

            "global_settings": {
                "background_music": {
                    "file": "background_music.mp3",
                    "volume": 0.15,
                    "enabled": True
                },
                "intro": {
                    "enabled": True,
                    "duration": 3,
                    "font_size": 65,
                    "position": "center"
                },
                "outro": {
                    "enabled": True,
                    "duration": 2
                }
            },

            "clips": []
        }

        # 각 문장에 대한 클립 설정 생성
        for idx, (sentence, translation) in enumerate(zip(sentences, translations)):
            # 이미지 경로
            image_path = image_paths[idx] if idx < len(image_paths) else ""

            # 동적 폰트 크기 계산 (기존 로직과 동일)
            text_length = len(sentence + translation)
            if text_length < 50:
                font_size = 58
            elif text_length < 80:
                font_size = 52
            elif text_length < 120:
                font_size = 48
            elif text_length < 160:
                font_size = 44
            else:
                font_size = 38

            clip_config = {
                "clip_id": f"sentence_{idx}",
                "type": "sentence",
                "sentence_index": idx,
                "sentence_text": sentence,
                "translation": translation,

                "audio": {
                    "tts_voices": ["alloy", "nova", "shimmer"],  # 3회 반복
                    "pause_after": 2.0,
                    "repeat_count": 3
                },

                "text": {
                    "font_size": font_size,
                    "position": "center",
                    "color": "white",
                    "stroke_color": "black",
                    "stroke_width": 3,
                    "enabled": True
                },

                "image": {
                    "path": image_path,
                    "filter": None
                }
            }

            config["clips"].append(clip_config)

        return config

    def save_config(self, video_id: str, config: Dict[str, Any]) -> str:
        """
        설정 파일 저장

        Args:
            video_id: 비디오 ID
            config: 설정 딕셔너리

        Returns:
            저장된 파일 경로
        """
        config_path = self.config_dir / f"{video_id}_config.json"

        # edited_at 업데이트
        config["edited_at"] = datetime.now().isoformat()

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return str(config_path)

    def load_config(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        설정 파일 로드

        Args:
            video_id: 비디오 ID

        Returns:
            설정 딕셔너리 (파일이 없으면 None)
        """
        config_path = self.config_dir / f"{video_id}_config.json"

        if not config_path.exists():
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    def config_exists(self, video_id: str) -> bool:
        """
        설정 파일 존재 여부 확인

        Args:
            video_id: 비디오 ID

        Returns:
            존재 여부
        """
        config_path = self.config_dir / f"{video_id}_config.json"
        return config_path.exists()


if __name__ == "__main__":
    # 테스트
    manager = ConfigManager("../output/edit_configs")

    # 기본 설정 생성
    config = manager.create_default_config(
        video_id="test_video_001",
        sentences=["Hello", "World"],
        translations=["안녕", "세계"],
        image_paths=["image_0.jpg", "image_1.jpg"],
        tts_data=[]
    )

    # 저장
    path = manager.save_config("test_video_001", config)
    print(f"Config saved to: {path}")

    # 로드
    loaded = manager.load_config("test_video_001")
    print(f"Loaded config: {loaded['video_id']}")
