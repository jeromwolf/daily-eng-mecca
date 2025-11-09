"""
YouTube 메타데이터 추출 모듈

yt-dlp를 사용하여 YouTube URL에서 메타데이터를 추출합니다.
의존성: yt-dlp (선택사항, 없어도 기존 시스템 정상 작동)

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import subprocess
import json
import requests
from pathlib import Path
from typing import Optional


class YouTubeMetadataExtractor:
    """
    YouTube 메타데이터 추출기

    기존 코드와 완전히 독립적.
    yt-dlp가 없어도 None을 반환하여 안전하게 처리.
    """

    def __init__(self):
        self.yt_dlp_available = self._check_yt_dlp()

    def _check_yt_dlp(self) -> bool:
        """yt-dlp 설치 여부 확인"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ yt-dlp 사용 가능: {result.stdout.strip()}")
                return True
        except Exception:
            pass

        print("⚠️ yt-dlp 없음 (선택 기능, YouTube URL 분석 불가)")
        return False

    def extract(self, url: str) -> Optional[dict]:
        """
        YouTube URL에서 메타데이터 추출

        Args:
            url: YouTube URL (watch?v=... 또는 youtu.be/...)

        Returns:
            {
                'title': str,           # 비디오 제목
                'duration': int,        # 초 단위
                'duration_string': str, # "3:42" 형식
                'description': str,     # 설명
                'channel': str,         # 채널명
                'thumbnail_url': str    # 썸네일 URL
            }
            또는 None (실패 시)
        """
        if not self.yt_dlp_available:
            return None

        try:
            # yt-dlp 실행 (JSON 출력, 다운로드 없음)
            result = subprocess.run([
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--no-warnings',
                url
            ], capture_output=True, text=True, timeout=15)

            if result.returncode != 0:
                print(f"⚠️ yt-dlp 실행 실패: {result.stderr}")
                return None

            # JSON 파싱
            data = json.loads(result.stdout)

            # 메타데이터 추출
            metadata = {
                'title': data.get('title', ''),
                'duration': data.get('duration', 0),
                'duration_string': self._format_duration(data.get('duration', 0)),
                'description': data.get('description', ''),
                'channel': data.get('channel', ''),
                'thumbnail_url': data.get('thumbnail', ''),
                'view_count': data.get('view_count', 0),
                'upload_date': data.get('upload_date', '')
            }

            print(f"✅ YouTube 메타데이터 추출 성공: {metadata['title'][:50]}...")
            return metadata

        except subprocess.TimeoutExpired:
            print("⚠️ YouTube 메타데이터 추출 타임아웃 (15초 초과)")
            return None

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패: {e}")
            return None

        except Exception as e:
            print(f"⚠️ YouTube 메타데이터 추출 실패: {e}")
            return None

    def extract_channel_info(self, channel_url: str, output_dir: str = 'output/youtube_thumbnails/channels') -> Optional[dict]:
        """
        YouTube 채널 정보 추출 (아이콘 포함)

        Args:
            channel_url: YouTube 채널 URL (예: https://www.youtube.com/@aion-vibecoding)
            output_dir: 채널 아이콘 저장 디렉토리

        Returns:
            {
                'channel_name': str,
                'channel_id': str,
                'icon_url': str,
                'icon_path': str,  # 다운로드된 로컬 경로
                'subscriber_count': int
            }
            또는 None (실패 시)

        Example:
            >>> extractor = YouTubeMetadataExtractor()
            >>> info = extractor.extract_channel_info("https://www.youtube.com/@aion-vibecoding")
            >>> # info['icon_path'] → '/path/to/channel_icon.jpg'
        """
        if not self.yt_dlp_available:
            print("⚠️ yt-dlp 없음 (채널 정보 추출 불가)")
            return None

        try:
            print(f"📺 채널 정보 추출 중: {channel_url}")

            # yt-dlp로 채널 정보 추출
            result = subprocess.run([
                'yt-dlp',
                '--dump-json',
                '--playlist-items', '0',  # 비디오 다운로드 방지
                '--no-download',
                '--no-warnings',
                channel_url
            ], capture_output=True, text=True, timeout=20)

            if result.returncode != 0:
                print(f"⚠️ yt-dlp 채널 추출 실패: {result.stderr}")
                return None

            # JSON 파싱
            data = json.loads(result.stdout)

            # 채널 정보 추출
            channel_info = {
                'channel_name': data.get('channel', data.get('uploader', '')),
                'channel_id': data.get('channel_id', ''),
                'icon_url': '',
                'icon_path': '',
                'subscriber_count': data.get('channel_follower_count', 0)
            }

            # 썸네일에서 채널 아이콘 추출 (채널 아이콘은 thumbnails에 포함됨)
            thumbnails = data.get('thumbnails', [])
            if thumbnails:
                # 가장 고해상도 썸네일 선택
                icon_url = thumbnails[-1].get('url', '')
                channel_info['icon_url'] = icon_url

                # 아이콘 다운로드
                if icon_url:
                    icon_path = self._download_channel_icon(
                        icon_url,
                        channel_info['channel_id'] or 'unknown',
                        output_dir
                    )
                    channel_info['icon_path'] = icon_path

            print(f"✅ 채널 정보 추출 성공: {channel_info['channel_name']}")
            return channel_info

        except subprocess.TimeoutExpired:
            print("⚠️ 채널 정보 추출 타임아웃 (20초 초과)")
            return None

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패: {e}")
            return None

        except Exception as e:
            print(f"⚠️ 채널 정보 추출 실패: {e}")
            return None

    def _download_channel_icon(self, icon_url: str, channel_id: str, output_dir: str) -> str:
        """
        채널 아이콘 이미지 다운로드

        Args:
            icon_url: 아이콘 URL
            channel_id: 채널 ID
            output_dir: 저장 디렉토리

        Returns:
            다운로드된 파일 경로
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 파일 확장자 추출
            ext = icon_url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'

            icon_file = output_path / f'{channel_id}_icon.{ext}'

            # 이미 다운로드된 경우 재사용
            if icon_file.exists():
                print(f"✓ 캐시된 채널 아이콘 사용: {icon_file}")
                return str(icon_file)

            # 다운로드
            response = requests.get(icon_url, timeout=10)
            response.raise_for_status()

            with open(icon_file, 'wb') as f:
                f.write(response.content)

            print(f"✅ 채널 아이콘 다운로드: {icon_file}")
            return str(icon_file)

        except Exception as e:
            print(f"⚠️ 채널 아이콘 다운로드 실패: {e}")
            return ''

    def _format_duration(self, seconds: int) -> str:
        """
        초를 MM:SS 형식으로 변환

        Args:
            seconds: 초 단위 시간

        Returns:
            "3:42" 형식 문자열

        Examples:
            >>> _format_duration(222)
            "3:42"
            >>> _format_duration(3661)
            "61:01"
        """
        if seconds <= 0:
            return "0:00"

        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def extract_title_keywords(self, title: str) -> dict:
        """
        제목에서 핵심 키워드 추출 (간단한 휴리스틱)

        Args:
            title: YouTube 비디오 제목

        Returns:
            {
                'main_text': str,      # 메인 텍스트 (숫자/이모지 제거)
                'numbers': list[str],  # 추출된 숫자들
                'emojis': list[str]    # 추출된 이모지들
            }

        Examples:
            >>> extract_title_keywords("여행영어 10문장 🌍 필수 회화")
            {
                'main_text': '여행영어 필수 회화',
                'numbers': ['10'],
                'emojis': ['🌍']
            }
        """
        import re

        # 숫자 추출 (단독으로 있는 숫자만)
        numbers = re.findall(r'\b\d+\b', title)

        # 이모지 추출 (간단한 패턴)
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # 이모티콘
            u"\U0001F300-\U0001F5FF"  # 기호 & 픽토그램
            u"\U0001F680-\U0001F6FF"  # 교통 & 지도 기호
            u"\U0001F1E0-\U0001F1FF"  # 국기
            "]+",
            flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(title)

        # 메인 텍스트 (숫자, 이모지, 특수문자 제거)
        main_text = title
        for num in numbers:
            main_text = main_text.replace(num, '')
        main_text = emoji_pattern.sub('', main_text)
        main_text = re.sub(r'[|•·→←]', '', main_text)  # 구분자 제거
        main_text = ' '.join(main_text.split())  # 중복 공백 제거

        return {
            'main_text': main_text.strip(),
            'numbers': numbers,
            'emojis': emojis
        }


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("YouTube 메타데이터 추출기 테스트")
    print("=" * 60)

    extractor = YouTubeMetadataExtractor()

    # 테스트 URL (Fire English 채널 예시)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"\n🔍 테스트 URL: {test_url}\n")

    metadata = extractor.extract(test_url)

    if metadata:
        print("✅ 추출 성공!\n")
        print(f"제목: {metadata['title']}")
        print(f"채널: {metadata['channel']}")
        print(f"길이: {metadata['duration_string']} ({metadata['duration']}초)")
        print(f"조회수: {metadata['view_count']:,}")

        # 제목 키워드 추출
        keywords = extractor.extract_title_keywords(metadata['title'])
        print(f"\n키워드 분석:")
        print(f"  메인 텍스트: {keywords['main_text']}")
        print(f"  숫자: {keywords['numbers']}")
        print(f"  이모지: {keywords['emojis']}")
    else:
        print("❌ 추출 실패 (yt-dlp 없거나 URL 오류)")

    print("\n" + "=" * 60)
