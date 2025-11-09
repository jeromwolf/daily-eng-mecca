"""
YouTube 동영상 프레임 추출 모듈

FFmpeg를 사용하여 YouTube 동영상에서 3개의 프레임을 캡처합니다.
- 시작 부분 (0초)
- 중간 부분 (duration / 2)
- 끝 부분 (duration - 5초)

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, List
import yt_dlp


class VideoFrameExtractor:
    """
    YouTube 동영상에서 여러 프레임을 추출하는 클래스

    FFmpeg를 사용하여 특정 시간대의 프레임을 이미지로 저장합니다.
    """

    def __init__(self, output_dir: str = 'output/youtube_thumbnails/frames'):
        """
        Args:
            output_dir: 프레임 이미지 저장 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FFmpeg 설치 확인
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """FFmpeg 설치 여부 확인"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ FFmpeg 사용 가능")
                return True
        except Exception:
            pass

        print("⚠️ FFmpeg 없음 (프레임 추출 불가)")
        return False

    def extract_frames_from_url(
        self,
        youtube_url: str,
        count: int = 3
    ) -> List[str]:
        """
        YouTube URL에서 여러 프레임 추출 (FFmpeg 스트리밍 - 전체 다운로드 불필요)

        Args:
            youtube_url: YouTube 동영상 URL
            count: 추출할 프레임 개수 (기본 3개)

        Returns:
            프레임 이미지 파일 경로 리스트

        Example:
            >>> extractor = VideoFrameExtractor()
            >>> frames = extractor.extract_frames_from_url(
                    "https://www.youtube.com/watch?v=...",
                    count=3
                )
            >>> # frames = ['/path/frame_0s.jpg', '/path/frame_30s.jpg', '/path/frame_60s.jpg']
        """
        if not self.ffmpeg_available:
            print("❌ FFmpeg 없음, 프레임 추출 불가")
            return []

        try:
            print(f"📹 YouTube 프레임 추출 중: {youtube_url}")

            # 1. yt-dlp로 동영상 정보 가져오기 (duration + 스트림 URL)
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                duration = info.get('duration', 0)  # 초 단위
                video_id = info.get('id', 'unknown')

                # 스트림 URL 가져오기 (최저 화질 - 빠른 추출)
                formats = info.get('formats', [])

                # worst 포맷 선택 (mp4, 낮은 해상도)
                video_url = None
                for fmt in reversed(formats):  # worst부터 탐색
                    if fmt.get('ext') == 'mp4' and fmt.get('vcodec') != 'none' and fmt.get('url'):
                        video_url = fmt.get('url')
                        break

                # 대체: 아무 비디오 포맷이나
                if not video_url:
                    for fmt in formats:
                        if fmt.get('vcodec') != 'none' and fmt.get('url'):
                            video_url = fmt.get('url')
                            break

            if duration == 0:
                print("⚠️ 동영상 길이를 알 수 없음")
                return []

            if not video_url:
                print("⚠️ 스트림 URL을 찾을 수 없음")
                return []

            print(f"  ✅ 동영상 길이: {duration}초")

            # 2. 프레임 추출할 시간대 계산
            timestamps = self._calculate_timestamps(duration, count)
            print(f"  📸 프레임 추출 시간대: {timestamps}")

            # 3. FFmpeg로 각 시간대 프레임 추출 (스트리밍 - 다운로드 불필요!)
            frame_paths = []
            for i, timestamp in enumerate(timestamps, 1):
                frame_path = self.output_dir / f'{video_id}_frame_{i}_{timestamp}s.jpg'

                # 캐시 확인
                if frame_path.exists():
                    print(f"  ✓ 캐시된 프레임 사용: {frame_path.name}")
                    frame_paths.append(str(frame_path))
                    continue

                # FFmpeg 스트리밍 추출 (전체 다운로드 없이!)
                success = self._extract_frame_from_stream(
                    video_url,
                    timestamp,
                    str(frame_path)
                )

                if success:
                    frame_paths.append(str(frame_path))
                    print(f"  ✅ 프레임 추출: {frame_path.name}")
                else:
                    print(f"  ⚠️ 프레임 추출 실패: {timestamp}초")

            return frame_paths

        except Exception as e:
            print(f"❌ 프레임 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _calculate_timestamps(self, duration: int, count: int) -> List[int]:
        """
        동영상 길이에 따라 프레임 추출할 시간대 계산

        Args:
            duration: 동영상 길이 (초)
            count: 추출할 프레임 개수

        Returns:
            타임스탬프 리스트 (초 단위)

        Example:
            >>> _calculate_timestamps(60, 3)
            [5, 30, 55]  # 시작, 중간, 끝 (여유 5초)
        """
        if count == 1:
            return [duration // 2]  # 중간만

        if count == 2:
            return [5, max(5, duration - 5)]  # 시작, 끝

        # 3개 이상: 시작, 중간들, 끝
        timestamps = []

        # 시작 (5초 후)
        timestamps.append(5)

        # 중간 프레임들
        if count > 2:
            for i in range(1, count - 1):
                # 균등하게 분배
                timestamp = int(5 + (duration - 10) * i / (count - 1))
                timestamps.append(timestamp)

        # 끝 (5초 전)
        timestamps.append(max(5, duration - 5))

        return timestamps

    def _extract_frame_from_stream(
        self,
        video_url: str,
        timestamp: int,
        output_path: str
    ) -> bool:
        """
        스트림 URL에서 특정 시간대의 프레임을 직접 추출 (다운로드 불필요!)

        Args:
            video_url: 비디오 스트림 URL (yt-dlp에서 추출)
            timestamp: 추출할 시간 (초)
            output_path: 출력 이미지 경로

        Returns:
            성공 여부
        """
        try:
            # FFmpeg 명령어 (스트리밍 모드)
            # -ss: 시작 시간 (input 앞에 있으면 시크 속도 빠름)
            # -i: 입력 스트림 URL
            # -vframes 1: 1개 프레임만
            # -q:v 1: 최고 품질 (1-5, 낮을수록 좋음) - 2→1로 변경
            # -y: 덮어쓰기
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),        # 시크 시간 (input 앞에 - 빠름!)
                '-i', video_url,              # 스트림 URL
                '-vframes', '1',              # 1프레임만
                '-q:v', '1',                  # 최고 품질 (2→1)
                '-y',                         # 덮어쓰기
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 스트리밍은 60초 타임아웃
            )

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print(f"  ⚠️ FFmpeg 타임아웃 (60초 초과)")
            return False

        except Exception as e:
            print(f"  ⚠️ FFmpeg 실행 실패: {e}")
            return False

    def _extract_frame_at_timestamp(
        self,
        video_path: str,
        timestamp: int,
        output_path: str
    ) -> bool:
        """
        로컬 파일에서 특정 시간대의 프레임을 이미지로 추출

        Args:
            video_path: 동영상 파일 경로
            timestamp: 추출할 시간 (초)
            output_path: 출력 이미지 경로

        Returns:
            성공 여부
        """
        try:
            # FFmpeg 명령어
            # -ss: 시작 시간
            # -i: 입력 파일
            # -vframes 1: 1개 프레임만
            # -q:v 2: 고품질 (1-5, 낮을수록 좋음)
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                '-y',  # 덮어쓰기
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print(f"  ⚠️ FFmpeg 타임아웃 (30초 초과)")
            return False

        except Exception as e:
            print(f"  ⚠️ FFmpeg 실행 실패: {e}")
            return False


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("YouTube 프레임 추출기 테스트")
    print("=" * 60)

    extractor = VideoFrameExtractor()

    # 테스트 URL (짧은 동영상 권장)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"\n🔍 테스트 URL: {test_url}\n")

    frames = extractor.extract_frames_from_url(test_url, count=3)

    if frames:
        print(f"\n✅ 추출 성공! {len(frames)}개 프레임:")
        for i, frame in enumerate(frames, 1):
            print(f"  {i}. {frame}")
    else:
        print("\n❌ 추출 실패")

    print("\n" + "=" * 60)
