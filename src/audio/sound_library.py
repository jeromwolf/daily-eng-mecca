"""
사운드 리소스 통합 관리
효과음 + 배경음악 통합 인터페이스
"""
from pathlib import Path
from typing import Optional, Dict
from .effects.ui_sounds import (
    ClickSound, HoverSound, NotificationSound,
    ErrorSound, SuccessSound, ToggleSound
)
from .effects.learning_sounds import (
    CorrectSound, WrongSound, CelebrationSound,
    EncouragementSound, StartSound, FinishSound
)
from .effects.transition_sounds import (
    WhooshSound, SwipeSound, PopSound,
    SlideSound, FadeTransitionSound, PageTurnSound
)
from .music.music_library import MusicLibrary


class SoundLibrary:
    """사운드 리소스 통합 관리"""

    def __init__(self, output_dir: str = "output/resources/sounds"):
        """
        SoundLibrary 초기화

        Args:
            output_dir: 사운드 파일 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.effects_dir = self.output_dir / "effects"
        self.music_dir = self.output_dir / "music"

        # 디렉토리 생성
        self.effects_dir.mkdir(parents=True, exist_ok=True)
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # 배경음악 관리자
        self.music_library = MusicLibrary(str(self.music_dir))

        # 효과음 캐시
        self._effect_cache: Dict[str, str] = {}

    # ===== 효과음 생성 =====

    def get_effect(self, effect_type: str) -> str:
        """
        효과음 가져오기 (캐싱)

        Args:
            effect_type: 효과음 타입
                UI: 'click', 'hover', 'notification', 'error', 'success', 'toggle'
                학습: 'correct', 'wrong', 'celebration', 'encouragement', 'start', 'finish'
                전환: 'whoosh', 'swipe', 'pop', 'slide', 'fade', 'page_turn'

        Returns:
            생성된 파일 경로
        """
        # 캐시 확인
        if effect_type in self._effect_cache:
            cached_path = self._effect_cache[effect_type]
            if Path(cached_path).exists():
                return cached_path

        # 효과음 생성
        effect_map = {
            # UI 효과음
            'click': ClickSound(),
            'hover': HoverSound(),
            'notification': NotificationSound(),
            'error': ErrorSound(),
            'success': SuccessSound(),
            'toggle': ToggleSound(),

            # 학습 효과음
            'correct': CorrectSound(),
            'wrong': WrongSound(),
            'celebration': CelebrationSound(),
            'encouragement': EncouragementSound(),
            'start': StartSound(),
            'finish': FinishSound(),

            # 전환 효과음
            'whoosh': WhooshSound(),
            'swipe': SwipeSound(),
            'pop': PopSound(),
            'slide': SlideSound(),
            'fade': FadeTransitionSound(),
            'page_turn': PageTurnSound(),
        }

        if effect_type not in effect_map:
            raise ValueError(f"알 수 없는 효과음 타입: {effect_type}")

        effect = effect_map[effect_type]
        output_path = self.effects_dir / f"{effect_type}.wav"

        print(f"🔊 효과음 생성 중: {effect_type}")
        file_path = effect.save(str(output_path))

        # 캐시 저장
        self._effect_cache[effect_type] = file_path

        return file_path

    # ===== 배경음악 =====

    def get_background_music(self, mood: str = 'energetic', duration: Optional[int] = None, index: int = 0) -> Optional[str]:
        """
        배경음악 가져오기

        Args:
            mood: 음악 무드 ('energetic', 'calm', 'upbeat', 'focus')
            duration: 필요한 길이 (초, None이면 무시)
            index: 카탈로그 내 인덱스

        Returns:
            다운로드된 음악 파일 경로
        """
        if duration:
            return self.music_library.get_music_for_duration(duration, mood)
        else:
            return self.music_library.download_music(mood, index)

    def list_music(self, mood: Optional[str] = None):
        """사용 가능한 배경음악 목록"""
        return self.music_library.list_available_music(mood)

    def print_music_catalog(self):
        """배경음악 카탈로그 출력"""
        self.music_library.print_catalog()

    # ===== 프리셋 =====

    def apply_preset(self, preset_name: str) -> Dict[str, str]:
        """
        프리셋 적용 (자주 사용하는 사운드 조합)

        Args:
            preset_name: 프리셋 이름 ('daily_english', 'quiz', 'interactive')

        Returns:
            사운드 파일 경로 딕셔너리
        """
        presets = {
            'daily_english': {
                'intro_music': ('energetic', None, 0),  # (mood, duration, index)
                'correct': 'correct',
                'wrong': 'wrong',
                'start': 'start',
                'finish': 'finish',
                'transition': 'whoosh',
            },
            'quiz': {
                'background_music': ('focus', None, 0),
                'correct': 'celebration',
                'wrong': 'wrong',
                'timer': 'notification',
                'success': 'success',
            },
            'interactive': {
                'click': 'click',
                'hover': 'hover',
                'success': 'success',
                'error': 'error',
                'notification': 'notification',
            },
        }

        if preset_name not in presets:
            raise ValueError(f"알 수 없는 프리셋: {preset_name}")

        preset = presets[preset_name]
        result = {}

        print(f"\n🎵 프리셋 적용 중: {preset_name}")
        print("=" * 60)

        for key, value in preset.items():
            # 배경음악
            if 'music' in key:
                mood, duration, index = value
                result[key] = self.get_background_music(mood, duration, index)
            # 효과음
            else:
                result[key] = self.get_effect(value)

        print("=" * 60)
        print(f"✓ 프리셋 적용 완료\n")

        return result

    # ===== 정보 =====

    def list_all_effects(self) -> list[str]:
        """사용 가능한 모든 효과음 목록"""
        return [
            # UI
            'click', 'hover', 'notification', 'error', 'success', 'toggle',
            # 학습
            'correct', 'wrong', 'celebration', 'encouragement', 'start', 'finish',
            # 전환
            'whoosh', 'swipe', 'pop', 'slide', 'fade', 'page_turn',
        ]

    def print_info(self):
        """사운드 라이브러리 정보 출력"""
        print("\n" + "=" * 60)
        print("🎵 Daily English Mecca - Sound Library")
        print("=" * 60)

        print("\n📁 효과음 (17종)")
        print("-" * 60)
        print("  UI 효과음 (6종):")
        print("    click, hover, notification, error, success, toggle")
        print("\n  학습 효과음 (6종):")
        print("    correct, wrong, celebration, encouragement, start, finish")
        print("\n  전환 효과음 (6종):")
        print("    whoosh, swipe, pop, slide, fade, page_turn")

        print("\n🎶 배경음악 (무료)")
        print("-" * 60)
        music_count = sum(len(music_list) for music_list in self.music_library.CATALOG.values())
        print(f"  총 {music_count}곡 (Kevin MacLeod - CC BY 4.0)")
        print("  무드: energetic, calm, upbeat, focus")

        print("\n📦 프리셋 (3종)")
        print("-" * 60)
        print("  daily_english - Daily English Mecca 기본")
        print("  quiz          - 퀴즈 모드")
        print("  interactive   - 인터랙티브 UI")

        print("\n💡 사용 예시:")
        print("-" * 60)
        print("  # 효과음 생성")
        print("  library.get_effect('correct')")
        print("")
        print("  # 배경음악 다운로드")
        print("  library.get_background_music(mood='energetic')")
        print("")
        print("  # 프리셋 적용")
        print("  sounds = library.apply_preset('daily_english')")
        print("=" * 60 + "\n")
