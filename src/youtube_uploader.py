"""
YouTube 자동 업로드 모듈
Google API를 사용하여 비디오를 YouTube에 업로드
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle


class YouTubeUploader:
    """YouTube 비디오 업로드 클래스"""

    # OAuth 2.0 스코프
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    def __init__(self, credentials_path=None, token_path=None):
        """
        Args:
            credentials_path: OAuth 2.0 클라이언트 시크릿 JSON 파일 경로
            token_path: 저장된 토큰 파일 경로
        """
        self.credentials_path = credentials_path or 'client_secrets.json'
        self.token_path = token_path or 'youtube_token.pickle'
        self.youtube = None

    def authenticate(self):
        """YouTube API 인증"""
        creds = None

        # 저장된 토큰이 있으면 로드
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # 토큰이 없거나 만료되었으면 재인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"❌ OAuth 클라이언트 시크릿 파일을 찾을 수 없습니다: {self.credentials_path}\n"
                        "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 다운로드하세요."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        # YouTube API 클라이언트 생성
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube API 인증 완료")

    def upload_video(
        self,
        video_path,
        title,
        description,
        tags=None,
        category_id='27',  # Education
        privacy_status='public',  # public, private, unlisted
        made_for_kids=False
    ):
        """
        비디오를 YouTube에 업로드

        Args:
            video_path: 업로드할 비디오 파일 경로
            title: 비디오 제목
            description: 비디오 설명
            tags: 태그 리스트
            category_id: 카테고리 ID (27=Education)
            privacy_status: 공개 상태 (public/private/unlisted)
            made_for_kids: 어린이용 콘텐츠 여부

        Returns:
            dict: 업로드 결과 (video_id, url 등)
        """
        if not self.youtube:
            self.authenticate()

        # 비디오 파일 존재 확인
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"❌ 비디오 파일을 찾을 수 없습니다: {video_path}")

        # 기본 태그
        if tags is None:
            tags = [
                "영어회화", "영어표현", "영어공부", "영어숏츠",
                "dailyenglish", "shorts", "영어초보", "영어발음"
            ]

        # 비디오 메타데이터
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': made_for_kids
            }
        }

        # 미디어 파일 업로드
        media = MediaFileUpload(
            video_path,
            chunksize=-1,  # 전체 파일 한 번에 업로드
            resumable=True,
            mimetype='video/mp4'
        )

        print(f"📤 YouTube 업로드 시작: {title}")
        print(f"   파일: {video_path}")
        print(f"   크기: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")

        # API 요청
        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        # 업로드 진행
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   업로드 진행: {progress}%")

        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"✅ 업로드 완료!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {video_url}")

        return {
            'success': True,
            'video_id': video_id,
            'video_url': video_url,
            'title': title,
            'privacy_status': privacy_status
        }

    def upload_from_metadata(self, video_path, metadata_path):
        """
        메타데이터 JSON 파일을 사용하여 업로드

        Args:
            video_path: 비디오 파일 경로
            metadata_path: 메타데이터 JSON 파일 경로

        Returns:
            dict: 업로드 결과
        """
        # 메타데이터 로드
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # 업로드
        return self.upload_video(
            video_path=video_path,
            title=metadata.get('title', 'Daily English Mecca'),
            description=metadata.get('description', ''),
            tags=metadata.get('tags', [])
        )


def test_upload():
    """테스트 업로드 함수"""
    uploader = YouTubeUploader()

    # 테스트할 비디오 찾기
    output_dir = Path(__file__).parent.parent / 'output'
    videos_dir = output_dir / 'videos'

    # 가장 최근 비디오
    videos = sorted(videos_dir.glob('daily_english_*.mp4'), key=os.path.getmtime, reverse=True)

    if not videos:
        print("❌ 테스트할 비디오가 없습니다.")
        return

    video_path = videos[0]
    video_id = video_path.stem.replace('daily_english_', '')

    # 메타데이터
    metadata_path = output_dir / 'metadata' / f'metadata_{video_id}.json'

    if metadata_path.exists():
        # 메타데이터 파일 사용
        result = uploader.upload_from_metadata(str(video_path), str(metadata_path))
    else:
        # 기본 메타데이터
        result = uploader.upload_video(
            video_path=str(video_path),
            title="Daily English Mecca - 영어 표현 배우기",
            description="매일 3문장으로 배우는 실전 영어 회화! #영어공부 #shorts",
            privacy_status='unlisted'  # 테스트는 비공개
        )

    print("\n업로드 결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    test_upload()
