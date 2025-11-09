"""
썸네일 히스토리 관리 모듈

세션별로 생성된 썸네일 버전들을 저장하고 관리합니다.
재생성 기능을 위한 버전 관리 시스템.

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class ThumbnailHistory:
    """
    썸네일 생성 히스토리 관리

    세션 단위로 썸네일 버전을 관리하며,
    기존 코드와 완전히 독립적.
    """

    def __init__(self, session_dir: str = 'output/youtube_thumbnails/sessions'):
        """
        Args:
            session_dir: 세션 저장 디렉토리
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, initial_data: dict = None) -> str:
        """
        새 썸네일 생성 세션 시작

        Args:
            initial_data: 초기 데이터 (선택사항)

        Returns:
            세션 ID (8자리 UUID)

        Example:
            >>> history = ThumbnailHistory()
            >>> session_id = history.create_session({
                    'main_text': '여행영어 마스터',
                    'youtube_url': 'https://...'
                })
        """
        # 고유한 세션 ID 생성
        session_id = str(uuid.uuid4())[:8]
        session_path = self.session_dir / session_id
        session_path.mkdir(exist_ok=True)

        # 세션 메타데이터 초기화
        metadata = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'initial_data': initial_data or {},
            'thumbnails': []  # 버전 리스트
        }

        # 세션 파일 저장
        session_file = session_path / 'session.json'
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 새 세션 생성: {session_id}")
        return session_id

    def save_thumbnail(
        self,
        session_id: str,
        thumbnail_path: str,
        config: dict,
        version: Optional[int] = None
    ) -> int:
        """
        썸네일 버전 저장

        Args:
            session_id: 세션 ID
            thumbnail_path: 생성된 썸네일 파일 경로
            config: 썸네일 생성 설정
            version: 버전 번호 (None이면 자동 증가)

        Returns:
            저장된 버전 번호

        Example:
            >>> history = ThumbnailHistory()
            >>> version = history.save_thumbnail(
                    session_id='abc123',
                    thumbnail_path='/path/to/thumbnail.png',
                    config={'style': 'fire_english', ...}
                )
        """
        session_path = self.session_dir / session_id

        if not session_path.exists():
            raise ValueError(f"세션 없음: {session_id}")

        # 세션 메타데이터 로드
        session_file = session_path / 'session.json'
        with open(session_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # 버전 번호 결정
        if version is None:
            version = len(metadata['thumbnails']) + 1

        # 썸네일 복사 (버전별 파일명)
        thumbnail_file = session_path / f'thumbnail_v{version}.png'
        shutil.copy(thumbnail_path, thumbnail_file)

        # 설정 저장
        config_file = session_path / f'config_v{version}.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        # 메타데이터 업데이트
        thumbnail_info = {
            'version': version,
            'thumbnail_path': str(thumbnail_file),
            'config_path': str(config_file),
            'created_at': datetime.now().isoformat(),
            'variation_type': config.get('variation_type', 'initial'),
            'file_size': thumbnail_file.stat().st_size
        }

        metadata['thumbnails'].append(thumbnail_info)
        metadata['updated_at'] = datetime.now().isoformat()

        # 세션 파일 업데이트
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 썸네일 저장: {session_id} v{version}")
        return version

    def get_session_thumbnails(self, session_id: str) -> List[dict]:
        """
        세션의 모든 썸네일 버전 가져오기

        Args:
            session_id: 세션 ID

        Returns:
            썸네일 정보 리스트

        Example:
            >>> history = ThumbnailHistory()
            >>> thumbnails = history.get_session_thumbnails('abc123')
            >>> for thumb in thumbnails:
                    print(f"v{thumb['version']}: {thumb['created_at']}")
        """
        session_path = self.session_dir / session_id
        session_file = session_path / 'session.json'

        if not session_file.exists():
            print(f"⚠️ 세션 없음: {session_id}")
            return []

        with open(session_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        return metadata['thumbnails']

    def load_thumbnail_config(self, session_id: str, version: int) -> Optional[dict]:
        """
        특정 버전의 설정 로드 (재생성용)

        Args:
            session_id: 세션 ID
            version: 버전 번호

        Returns:
            설정 dict 또는 None

        Example:
            >>> history = ThumbnailHistory()
            >>> config = history.load_thumbnail_config('abc123', 2)
            >>> # 버전 2의 설정으로 재생성 가능
        """
        config_file = self.session_dir / session_id / f'config_v{version}.json'

        if not config_file.exists():
            print(f"⚠️ 설정 파일 없음: v{version}")
            return None

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_thumbnail_path(self, session_id: str, version: int) -> Optional[str]:
        """
        특정 버전의 썸네일 파일 경로

        Args:
            session_id: 세션 ID
            version: 버전 번호

        Returns:
            파일 경로 또는 None
        """
        thumbnail_file = self.session_dir / session_id / f'thumbnail_v{version}.png'

        if thumbnail_file.exists():
            return str(thumbnail_file)
        else:
            return None

    def get_latest_version(self, session_id: str) -> Optional[int]:
        """
        세션의 최신 버전 번호

        Args:
            session_id: 세션 ID

        Returns:
            최신 버전 번호 또는 None
        """
        thumbnails = self.get_session_thumbnails(session_id)

        if thumbnails:
            return max(t['version'] for t in thumbnails)
        else:
            return None

    def delete_version(self, session_id: str, version: int) -> bool:
        """
        특정 버전 삭제

        Args:
            session_id: 세션 ID
            version: 삭제할 버전 번호

        Returns:
            성공 여부

        Note:
            최초 버전(v1)은 삭제 불가
        """
        if version == 1:
            print("❌ 최초 버전(v1)은 삭제할 수 없습니다.")
            return False

        session_path = self.session_dir / session_id
        thumbnail_file = session_path / f'thumbnail_v{version}.png'
        config_file = session_path / f'config_v{version}.json'

        # 파일 삭제
        deleted = False
        if thumbnail_file.exists():
            thumbnail_file.unlink()
            deleted = True

        if config_file.exists():
            config_file.unlink()
            deleted = True

        # 메타데이터 업데이트
        if deleted:
            session_file = session_path / 'session.json'
            with open(session_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 해당 버전 제거
            metadata['thumbnails'] = [
                t for t in metadata['thumbnails'] if t['version'] != version
            ]
            metadata['updated_at'] = datetime.now().isoformat()

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✅ 버전 삭제: {session_id} v{version}")

        return deleted

    def delete_session(self, session_id: str) -> bool:
        """
        세션 전체 삭제

        Args:
            session_id: 세션 ID

        Returns:
            성공 여부
        """
        session_path = self.session_dir / session_id

        if session_path.exists():
            shutil.rmtree(session_path)
            print(f"✅ 세션 삭제: {session_id}")
            return True
        else:
            print(f"⚠️ 세션 없음: {session_id}")
            return False

    def list_sessions(self, limit: int = 10) -> List[dict]:
        """
        최근 세션 목록

        Args:
            limit: 반환할 세션 개수

        Returns:
            세션 정보 리스트 (최신순)

        Example:
            >>> history = ThumbnailHistory()
            >>> sessions = history.list_sessions(5)
            >>> for session in sessions:
                    print(f"{session['session_id']}: {session['created_at']}")
        """
        session_files = list(self.session_dir.glob('*/session.json'))

        # 세션 정보 로드
        sessions = []
        for session_file in session_files:
            with open(session_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                sessions.append({
                    'session_id': metadata['session_id'],
                    'created_at': metadata['created_at'],
                    'updated_at': metadata['updated_at'],
                    'thumbnail_count': len(metadata['thumbnails'])
                })

        # 최신순 정렬
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)

        return sessions[:limit]

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        오래된 세션 자동 삭제

        Args:
            days: 보관 일수 (기본 30일)

        Returns:
            삭제된 세션 개수
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for session_file in self.session_dir.glob('*/session.json'):
            with open(session_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            created_at = datetime.fromisoformat(metadata['created_at'])

            if created_at < cutoff_date:
                session_id = metadata['session_id']
                self.delete_session(session_id)
                deleted_count += 1

        if deleted_count > 0:
            print(f"✅ 오래된 세션 {deleted_count}개 삭제 ({days}일 이상)")

        return deleted_count


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("썸네일 히스토리 관리 테스트")
    print("=" * 60)

    history = ThumbnailHistory()

    # 1. 세션 생성
    print("\n1️⃣ 세션 생성")
    session_id = history.create_session({
        'main_text': '여행영어 마스터',
        'youtube_url': 'https://example.com'
    })
    print(f"  세션 ID: {session_id}")

    # 2. 더미 썸네일 저장 (테스트용)
    print("\n2️⃣ 썸네일 저장 (더미)")
    # 실제 파일이 필요하므로 테스트는 스킵
    # version = history.save_thumbnail(...)

    # 3. 세션 목록
    print("\n3️⃣ 최근 세션 목록")
    sessions = history.list_sessions(5)
    for session in sessions:
        print(f"  {session['session_id']}: {session['thumbnail_count']}개 버전")

    print("\n" + "=" * 60)
