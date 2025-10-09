"""
무료 배경음악 관리 시스템
Kevin MacLeod, Bensound 등 무료 음악 다운로드 및 관리
"""
import os
import requests
from pathlib import Path
from typing import Optional, Dict, List


class MusicLibrary:
    """무료 배경음악 관리"""

    # 무료 음악 카탈로그 (Kevin MacLeod - incompetech.com)
    CATALOG = {
        'energetic': [
            {
                'name': 'Happy Alley',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Alley.mp3',
                'duration': 110,
                'mood': 'energetic',
                'tempo': 'fast',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
            {
                'name': 'Breaktime',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Breaktime%20-%20Silent%20Film%20Light.mp3',
                'duration': 114,
                'mood': 'energetic',
                'tempo': 'medium',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
        ],
        'calm': [
            {
                'name': 'Carefree',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3',
                'duration': 205,
                'mood': 'calm',
                'tempo': 'slow',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
            {
                'name': 'Wallpaper',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wallpaper.mp3',
                'duration': 164,
                'mood': 'calm',
                'tempo': 'slow',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
        ],
        'upbeat': [
            {
                'name': 'Fluffing a Duck',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Fluffing%20a%20Duck.mp3',
                'duration': 150,
                'mood': 'upbeat',
                'tempo': 'fast',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
            {
                'name': 'Funky Chunk',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Funky%20Chunk.mp3',
                'duration': 179,
                'mood': 'upbeat',
                'tempo': 'medium',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
        ],
        'focus': [
            {
                'name': 'Deliberate Thought',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Deliberate%20Thought.mp3',
                'duration': 152,
                'mood': 'focus',
                'tempo': 'slow',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
            {
                'name': 'Meditation Impromptu 01',
                'url': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Meditation%20Impromptu%2001.mp3',
                'duration': 223,
                'mood': 'focus',
                'tempo': 'slow',
                'license': 'CC BY 4.0',
                'artist': 'Kevin MacLeod'
            },
        ],
    }

    def __init__(self, output_dir: str = "output/resources/music"):
        """
        MusicLibrary 초기화

        Args:
            output_dir: 음악 파일 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_music(self, mood: str, index: int = 0, force: bool = False) -> Optional[str]:
        """
        음악 다운로드 (캐싱)

        Args:
            mood: 음악 무드 (energetic, calm, upbeat, focus)
            index: 카탈로그 내 인덱스 (기본 0)
            force: 강제 재다운로드 (캐시 무시)

        Returns:
            다운로드된 파일 경로 (실패 시 None)
        """
        if mood not in self.CATALOG:
            print(f"⚠️ 알 수 없는 무드: {mood}")
            print(f"   사용 가능한 무드: {list(self.CATALOG.keys())}")
            return None

        if index >= len(self.CATALOG[mood]):
            print(f"⚠️ 인덱스 {index}가 범위를 벗어남 (최대 {len(self.CATALOG[mood])-1})")
            return None

        music_info = self.CATALOG[mood][index]
        filename = f"{mood}_{music_info['name'].replace(' ', '_')}.mp3"
        output_path = self.output_dir / filename

        # 캐시 확인
        if output_path.exists() and not force:
            print(f"✓ 캐시된 음악 사용: {filename}")
            return str(output_path)

        # 다운로드
        print(f"\n🎵 음악 다운로드 중...")
        print(f"   곡명: {music_info['name']}")
        print(f"   무드: {mood}")
        print(f"   길이: {music_info['duration']}초")

        try:
            response = requests.get(music_info['url'], timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ 다운로드 완료: {filename}")
            print(f"   크기: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"   라이선스: {music_info['license']}")

            return str(output_path)

        except Exception as e:
            print(f"✗ 다운로드 실패: {e}")
            return None

    def list_available_music(self, mood: Optional[str] = None) -> List[Dict]:
        """
        사용 가능한 음악 목록 조회

        Args:
            mood: 특정 무드 필터 (None이면 전체)

        Returns:
            음악 정보 리스트
        """
        if mood:
            if mood not in self.CATALOG:
                print(f"⚠️ 알 수 없는 무드: {mood}")
                return []
            return self.CATALOG[mood]

        # 전체 목록
        all_music = []
        for mood_key, music_list in self.CATALOG.items():
            for music in music_list:
                music_copy = music.copy()
                music_copy['mood'] = mood_key
                all_music.append(music_copy)

        return all_music

    def print_catalog(self):
        """카탈로그 출력 (사용자 친화적)"""
        print("\n" + "=" * 60)
        print("🎵 무료 배경음악 카탈로그")
        print("=" * 60)

        for mood, music_list in self.CATALOG.items():
            print(f"\n📁 {mood.upper()}")
            print("-" * 60)

            for idx, music in enumerate(music_list):
                print(f"  [{idx}] {music['name']}")
                print(f"      길이: {music['duration']}초 | 템포: {music['tempo']}")
                print(f"      아티스트: {music['artist']} | {music['license']}")

        print("\n" + "=" * 60)
        print("💡 사용 방법:")
        print("   library.download_music(mood='calm', index=0)")
        print("=" * 60 + "\n")

    def get_music_for_duration(self, duration: int, mood: str = 'energetic') -> Optional[str]:
        """
        특정 길이에 맞는 음악 찾기 및 다운로드

        Args:
            duration: 필요한 길이 (초)
            mood: 선호 무드

        Returns:
            다운로드된 파일 경로
        """
        if mood not in self.CATALOG:
            print(f"⚠️ 알 수 없는 무드: {mood}, 기본값(energetic) 사용")
            mood = 'energetic'

        # 길이에 가장 적합한 음악 찾기
        music_list = self.CATALOG[mood]
        best_match = None
        min_diff = float('inf')

        for idx, music in enumerate(music_list):
            # 음악이 충분히 긴지 확인
            if music['duration'] >= duration:
                diff = music['duration'] - duration
                if diff < min_diff:
                    min_diff = diff
                    best_match = idx

        if best_match is None:
            # 충분히 긴 음악이 없으면 가장 긴 음악 선택
            best_match = max(range(len(music_list)), key=lambda i: music_list[i]['duration'])
            print(f"⚠️ {duration}초보다 긴 음악이 없습니다.")
            print(f"   가장 긴 음악({music_list[best_match]['duration']}초) 사용")

        return self.download_music(mood, best_match)

    def get_music_info(self, mood: str, index: int = 0) -> Optional[Dict]:
        """
        음악 정보 조회

        Args:
            mood: 음악 무드
            index: 인덱스

        Returns:
            음악 정보 딕셔너리
        """
        if mood not in self.CATALOG:
            return None

        if index >= len(self.CATALOG[mood]):
            return None

        return self.CATALOG[mood][index]
