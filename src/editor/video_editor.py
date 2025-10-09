"""
비디오 편집 설정 적용 엔진
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.video_creator import VideoCreator
from src.editor.config_manager import ConfigManager
from src.resource_manager import ResourceManager


class VideoEditor:
    """편집 설정을 비디오 생성에 적용하는 엔진"""

    def __init__(self, config_dir: str, output_dir: str):
        """
        VideoEditor 초기화

        Args:
            config_dir: 설정 파일 디렉토리
            output_dir: 비디오 출력 디렉토리
        """
        self.config_manager = ConfigManager(config_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ResourceManager 초기화 (인트로/아웃트로 이미지 캐시 사용)
        resources_dir = self.output_dir.parent / "resources"
        self.resource_manager = ResourceManager(str(resources_dir))

    def regenerate_video(
        self,
        video_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        편집된 설정으로 비디오 재생성

        Args:
            video_id: 비디오 ID
            config: 편집 설정 (None이면 파일에서 로드)

        Returns:
            생성된 비디오 파일 경로
        """
        # 설정 로드
        if config is None:
            config = self.config_manager.load_config(video_id)
            if config is None:
                raise ValueError(f"설정 파일을 찾을 수 없습니다: {video_id}")

        print(f"\n🎬 비디오 재생성 시작: {video_id}")
        print(f"  - 설정 버전: {config['version']}")
        print(f"  - 편집 시간: {config['edited_at']}")

        # VideoCreator 인스턴스 생성 (resource_manager 전달로 인트로/아웃트로 이미지 사용)
        creator = VideoCreator(resource_manager=self.resource_manager)

        # 전역 설정 적용
        global_settings = config.get("global_settings", {})
        self._apply_global_settings(creator, global_settings)

        # 클립 데이터 추출 (기존 audio 파일 경로 포함)
        clips = config.get("clips", [])
        sentences, translations, image_paths, audio_info = self._extract_clip_data_with_audio(clips, video_id)

        # 비디오 생성
        output_path = self.output_dir / f"{video_id}_edited.mp4"
        creator.create_video(
            sentences=sentences,
            translations=translations,
            image_paths=image_paths,
            audio_info=audio_info,
            output_path=str(output_path)
        )

        print(f"\n✅ 비디오 재생성 완료!")
        print(f"  - 파일: {output_path}")

        return str(output_path)

    def _apply_global_settings(
        self,
        creator: VideoCreator,
        global_settings: Dict[str, Any]
    ):
        """
        전역 설정을 VideoCreator에 적용

        Args:
            creator: VideoCreator 인스턴스
            global_settings: 전역 설정 딕셔너리
        """
        # 배경 음악 설정
        bg_music = global_settings.get("background_music", {})
        if bg_music.get("enabled", True):
            # 배경 음악 볼륨 설정
            creator.bg_music_volume = bg_music.get("volume", 0.15)
            print(f"  - 배경 음악 볼륨: {creator.bg_music_volume * 100:.0f}%")

        # 인트로 설정
        intro = global_settings.get("intro", {})
        if intro.get("enabled", True):
            creator.intro_duration = intro.get("duration", 3)
            creator.intro_font_size = intro.get("font_size", 65)

            # 커스텀 인트로 이미지 경로 설정
            custom_intro_image = intro.get("custom_image")
            if custom_intro_image and os.path.exists(custom_intro_image):
                creator.intro_custom_image = custom_intro_image
                print(f"  - 인트로: {creator.intro_duration}초, 폰트 {creator.intro_font_size}px, 커스텀 이미지 사용")
            else:
                print(f"  - 인트로: {creator.intro_duration}초, 폰트 {creator.intro_font_size}px")

        # 아웃트로 설정
        outro = global_settings.get("outro", {})
        if outro.get("enabled", True):
            creator.outro_duration = outro.get("duration", 2)

            # 커스텀 아웃트로 이미지 경로 설정
            custom_outro_image = outro.get("custom_image")
            if custom_outro_image and os.path.exists(custom_outro_image):
                creator.outro_custom_image = custom_outro_image
                print(f"  - 아웃트로: {creator.outro_duration}초, 커스텀 이미지 사용")
            else:
                print(f"  - 아웃트로: {creator.outro_duration}초")

    def _extract_clip_data(
        self,
        clips: list
    ) -> tuple:
        """
        클립 설정에서 VideoCreator에 필요한 데이터 추출

        Args:
            clips: 클립 설정 리스트

        Returns:
            (sentences, translations, image_paths, tts_data) 튜플
        """
        sentences = []
        translations = []
        image_paths = []
        tts_data = []

        for clip in clips:
            if clip.get("type") != "sentence":
                continue

            # 텍스트 데이터
            sentences.append(clip.get("sentence_text", ""))
            translations.append(clip.get("translation", ""))

            # 이미지 경로
            image = clip.get("image", {})
            image_paths.append(image.get("path", ""))

            # TTS 데이터
            audio = clip.get("audio", {})
            tts_voices = audio.get("tts_voices", ["alloy", "nova", "shimmer"])
            pause_after = audio.get("pause_after", 2.0)
            repeat_count = audio.get("repeat_count", 3)

            # TTS 데이터 구조 (멀티보이스 반복)
            clip_tts_data = []
            for voice in tts_voices[:repeat_count]:
                clip_tts_data.append({
                    "voice": voice,
                    "pause_after": pause_after
                })

            tts_data.append(clip_tts_data)

        print(f"  - 클립 수: {len(clips)}")
        print(f"  - 문장 수: {len(sentences)}")

        return sentences, translations, image_paths, tts_data

    def _extract_clip_data_with_audio(
        self,
        clips: list,
        video_id: str
    ) -> tuple:
        """
        클립 설정에서 데이터 추출 (기존 audio 파일 경로 포함)

        Args:
            clips: 클립 설정 리스트
            video_id: 비디오 ID (audio 파일 경로 찾기용)

        Returns:
            (sentences, translations, image_paths, audio_info) 튜플
        """
        from mutagen.mp3 import MP3

        sentences = []
        translations = []
        image_paths = []
        audio_info = []

        # audio 파일 경로 구하기
        project_root = Path(__file__).parent.parent.parent
        audio_base_dir = project_root / "output" / "audio" / video_id

        for i, clip in enumerate(clips, start=1):
            if clip.get("type") != "sentence":
                continue

            # 텍스트 데이터
            sentence_text = clip.get("sentence_text", "")
            sentences.append(sentence_text)
            translations.append(clip.get("translation", ""))

            # 이미지 경로
            image = clip.get("image", {})
            image_paths.append(image.get("path", ""))

            # Audio 파일 경로 및 duration
            audio = clip.get("audio", {})
            tts_voices = audio.get("tts_voices", ["alloy", "nova", "shimmer"])

            voices_dict = {}
            for voice in tts_voices:
                audio_file = audio_base_dir / f"sentence_{i}_{voice}.mp3"
                if audio_file.exists():
                    try:
                        audio_obj = MP3(str(audio_file))
                        duration = audio_obj.info.length
                    except Exception as e:
                        print(f"⚠ Audio duration 측정 실패: {audio_file}, {e}")
                        duration = 1.0  # 기본값

                    voices_dict[voice] = {
                        'path': str(audio_file),
                        'duration': duration
                    }
                else:
                    print(f"⚠ Audio 파일 없음: {audio_file}")

            audio_info.append({
                'sentence': sentence_text,
                'voices': voices_dict
            })

        print(f"  - 클립 수: {len(clips)}")
        print(f"  - 문장 수: {len(sentences)}")
        print(f"  - Audio 파일: {audio_base_dir}")

        return sentences, translations, image_paths, audio_info

    def create_video_with_config(
        self,
        video_id: str,
        sentences: list,
        translations: list,
        image_paths: list,
        tts_data: list,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        새 비디오 생성 + 편집 설정 저장

        Args:
            video_id: 비디오 ID
            sentences: 영어 문장 리스트
            translations: 한글 번역 리스트
            image_paths: 이미지 경로 리스트
            tts_data: TTS 데이터 리스트
            config_overrides: 설정 오버라이드 (선택)

        Returns:
            (video_path, config_path) 튜플
        """
        print(f"\n🎬 비디오 생성 + 설정 저장: {video_id}")

        # 1. 기본 설정 생성
        config = self.config_manager.create_default_config(
            video_id=video_id,
            sentences=sentences,
            translations=translations,
            image_paths=image_paths,
            tts_data=tts_data
        )

        # 2. 설정 오버라이드 적용
        if config_overrides:
            config.update(config_overrides)

        # 3. 설정 저장
        config_path = self.config_manager.save_config(video_id, config)
        print(f"  - 설정 저장: {config_path}")

        # 4. 비디오 생성 (resource_manager 전달로 인트로/아웃트로 이미지 사용)
        creator = VideoCreator(resource_manager=self.resource_manager)
        self._apply_global_settings(creator, config.get("global_settings", {}))

        output_path = self.output_dir / f"{video_id}.mp4"
        creator.create_video(
            sentences=sentences,
            translations=translations,
            image_paths=image_paths,
            audio_info=tts_data,  # VideoCreator는 audio_info 파라미터를 받음
            output_path=str(output_path)
        )

        print(f"\n✅ 비디오 + 설정 생성 완료!")
        print(f"  - 비디오: {output_path}")
        print(f"  - 설정: {config_path}")

        return str(output_path), config_path


if __name__ == "__main__":
    # 테스트
    import os

    # 절대 경로 사용
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_dir = os.path.join(project_root, "output", "edit_configs")
    output_dir = os.path.join(project_root, "output", "videos")

    editor = VideoEditor(config_dir, output_dir)

    # 테스트 데이터
    video_id = "test_video_002"
    sentences = ["Hello world", "How are you?"]
    translations = ["안녕 세상", "어떻게 지내세요?"]
    image_paths = [
        os.path.join(project_root, "output", "resources", "images", "image_0.jpg"),
        os.path.join(project_root, "output", "resources", "images", "image_1.jpg")
    ]
    tts_data = [
        [{"voice": "alloy"}, {"voice": "nova"}, {"voice": "shimmer"}],
        [{"voice": "alloy"}, {"voice": "nova"}, {"voice": "shimmer"}]
    ]

    # 비디오 생성 + 설정 저장
    video_path, config_path = editor.create_video_with_config(
        video_id=video_id,
        sentences=sentences,
        translations=translations,
        image_paths=image_paths,
        tts_data=tts_data
    )

    print(f"\n📁 생성 결과:")
    print(f"   비디오: {video_path}")
    print(f"   설정: {config_path}")

    # 설정 로드 및 재생성 테스트
    print(f"\n🔄 재생성 테스트...")
    regenerated_path = editor.regenerate_video(video_id)
    print(f"   재생성 비디오: {regenerated_path}")
