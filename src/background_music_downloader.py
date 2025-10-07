"""
무료 배경 음악 다운로드 모듈
"""
import os
import requests
from pathlib import Path


class BackgroundMusicDownloader:
    """무료 배경 음악 다운로드 및 생성"""

    # 무료 배경 음악 다운로드 가이드
    MUSIC_GUIDE = """
    무료 배경 음악 다운로드 가이드:

    1. YouTube Audio Library (추천)
       - https://studio.youtube.com/
       - YouTube 계정으로 로그인 → 왼쪽 메뉴 → 오디오 보관함
       - 장르: Happy, Bright, Cheerful 추천
       - MP3로 다운로드

    2. Pixabay Music
       - https://pixabay.com/music/
       - 무료 다운로드, 저작권 걱정 없음
       - "Happy", "Upbeat" 키워드로 검색

    3. Free Music Archive
       - https://freemusicarchive.org/
       - CC BY 라이선스 음악
       - 밝고 경쾌한 음악 추천

    다운로드 후:
    - output/resources/background_music.mp3 로 저장
    - 파일명은 정확히 'background_music.mp3'
    """

    def __init__(self, output_dir: str):
        """
        BackgroundMusicDownloader 초기화

        Args:
            output_dir: 음악 파일 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_music(self, filename: str = "background_music.mp3") -> str:
        """
        무료 배경 음악 다운로드 (Kevin MacLeod - Incompetech)

        Args:
            filename: 저장할 파일 이름

        Returns:
            다운로드된 파일 경로
        """
        try:
            output_path = self.output_dir / filename

            # Kevin MacLeod의 무료 음악 (직접 다운로드 가능)
            # "Pixel Peeker Polka" - 경쾌한 탐정 스타일 배경음악
            music_url = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Pixel%20Peeker%20Polka.mp3"
            music_name = "Pixel Peeker Polka"
            artist = "Kevin MacLeod"
            license_info = "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)"

            print(f"배경 음악 다운로드 중...")
            print(f"  - 곡명: {music_name}")
            print(f"  - 아티스트: {artist}")
            print(f"  - 라이선스: {license_info}")

            # 다운로드
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(music_url, timeout=60, headers=headers)
            response.raise_for_status()

            # 저장
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ 배경 음악 다운로드 완료: {output_path}")
            print(f"  - 크기: {len(response.content) / 1024 / 1024:.2f} MB")
            return str(output_path)

        except Exception as e:
            print(f"✗ 배경 음악 다운로드 실패: {e}")
            raise

    def print_music_info(self):
        """다운로드할 음악 정보 출력"""
        print("\n다운로드할 무료 배경 음악:")
        print("=" * 60)
        print("곡명: Pixel Peeker Polka (1분 35초)")
        print("아티스트: Kevin MacLeod (incompetech.com)")
        print("라이선스: CC BY 4.0")
        print("설명: 경쾌한 탐정 스타일 음악 (미스터리/코믹한 분위기)")
        print("=" * 60)

    def check_music_exists(self, filename: str = "background_music.mp3") -> bool:
        """
        배경 음악 파일이 이미 존재하는지 확인

        Args:
            filename: 확인할 파일 이름

        Returns:
            존재 여부
        """
        output_path = self.output_dir / filename
        return output_path.exists()


if __name__ == "__main__":
    # 테스트
    downloader = BackgroundMusicDownloader("../output/resources")
    downloader.list_available_music()

    if not downloader.check_music_exists():
        downloader.download_music(0)
    else:
        print("배경 음악이 이미 존재합니다.")
