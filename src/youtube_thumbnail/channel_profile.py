"""
채널 프로필 관리 모듈

YouTube 채널의 브랜딩 정보를 저장하고 로드합니다.
로고, 색상, 폰트 등을 저장하여 일관된 썸네일 생성.

Author: Kelly & Claude Code
Date: 2025-11-09
"""
import json
from pathlib import Path
from typing import Optional


class ChannelProfile:
    """
    채널 브랜딩 정보 관리

    기존 코드와 완전히 독립적.
    """

    def __init__(self, profile_dir: str = 'output/channel_profiles'):
        """
        Args:
            profile_dir: 프로필 저장 디렉토리
        """
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        self.default_profile_path = self.profile_dir / 'default_profile.json'

    def save_profile(self, profile_data: dict, profile_name: str = 'default') -> str:
        """
        채널 프로필 저장

        Args:
            profile_data: 프로필 데이터 dict
            profile_name: 프로필 이름 (기본: 'default')

        Returns:
            저장된 파일 경로

        Example:
            >>> profile = ChannelProfile()
            >>> data = {
                    'channel_name': 'Daily English Mecca',
                    'logo_path': 'kelly_casual_hoodie.png',
                    'brand_colors': {
                        'primary': '#FF5733',
                        'secondary': '#3357FF'
                    },
                    'brand_font': 'AppleGothic',
                    'watermark_text': '@DailyEnglishMecca'
                }
            >>> profile.save_profile(data)
        """
        # 필수 필드 검증
        required_fields = ['channel_name', 'brand_colors']
        for field in required_fields:
            if field not in profile_data:
                raise ValueError(f"필수 필드 누락: {field}")

        # 프로필 파일 경로
        profile_path = self.profile_dir / f'{profile_name}_profile.json'

        # 저장
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 채널 프로필 저장: {profile_path}")
        return str(profile_path)

    def load_profile(self, profile_name: str = 'default') -> dict:
        """
        채널 프로필 로드

        Args:
            profile_name: 프로필 이름 (기본: 'default')

        Returns:
            프로필 데이터 dict
            없으면 기본 프로필 반환
        """
        profile_path = self.profile_dir / f'{profile_name}_profile.json'

        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            print(f"✅ 채널 프로필 로드: {profile['channel_name']}")
            return profile

        # 저장된 프로필 없으면 기본값 반환
        print("⚠️ 저장된 프로필 없음, 기본 프로필 사용")
        return self.get_default_profile()

    def get_default_profile(self) -> dict:
        """
        기본 채널 프로필 (Daily English Mecca)

        Returns:
            기본 프로필 dict
        """
        return {
            'channel_name': 'Daily English Mecca',
            'logo_path': 'output/resources/images/kelly_casual_hoodie.png',
            'brand_colors': {
                'primary': '#FF5733',      # 빨간색 (Fire English 스타일)
                'secondary': '#3357FF',    # 파란색
                'accent': '#FFD700'        # 금색 (CTA)
            },
            'brand_font': 'AppleGothic',
            'watermark_text': '@DailyEnglishMecca',
            'watermark_position': 'bottom-right',
            'character_enabled': True,      # Kelly 캐릭터 사용
            'character_position': 'center'  # 중앙 배치
        }

    def list_profiles(self) -> list[str]:
        """
        저장된 모든 프로필 이름 목록

        Returns:
            프로필 이름 리스트
        """
        profile_files = list(self.profile_dir.glob('*_profile.json'))
        profile_names = [f.stem.replace('_profile', '') for f in profile_files]

        return profile_names

    def delete_profile(self, profile_name: str) -> bool:
        """
        프로필 삭제

        Args:
            profile_name: 삭제할 프로필 이름

        Returns:
            성공 여부

        Note:
            'default' 프로필은 삭제 불가
        """
        if profile_name == 'default':
            print("❌ 기본 프로필은 삭제할 수 없습니다.")
            return False

        profile_path = self.profile_dir / f'{profile_name}_profile.json'

        if profile_path.exists():
            profile_path.unlink()
            print(f"✅ 프로필 삭제: {profile_name}")
            return True
        else:
            print(f"⚠️ 프로필 없음: {profile_name}")
            return False

    def update_profile(self, profile_name: str, updates: dict) -> str:
        """
        기존 프로필 업데이트 (부분 수정)

        Args:
            profile_name: 프로필 이름
            updates: 업데이트할 필드 dict

        Returns:
            업데이트된 파일 경로

        Example:
            >>> profile = ChannelProfile()
            >>> profile.update_profile('default', {
                    'brand_colors': {'primary': '#00FF00'}
                })
        """
        # 기존 프로필 로드
        current = self.load_profile(profile_name)

        # 업데이트 병합 (deep merge)
        for key, value in updates.items():
            if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                # 딕셔너리는 병합
                current[key].update(value)
            else:
                # 나머지는 덮어쓰기
                current[key] = value

        # 저장
        return self.save_profile(current, profile_name)

    def export_profile(self, profile_name: str, export_path: str) -> str:
        """
        프로필을 외부 파일로 내보내기

        Args:
            profile_name: 프로필 이름
            export_path: 내보낼 파일 경로

        Returns:
            내보낸 파일 경로
        """
        profile = self.load_profile(profile_name)

        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        print(f"✅ 프로필 내보내기: {export_file}")
        return str(export_file)

    def import_profile(self, import_path: str, profile_name: str = None) -> str:
        """
        외부 파일에서 프로필 가져오기

        Args:
            import_path: 가져올 파일 경로
            profile_name: 저장할 프로필 이름 (None이면 파일명 사용)

        Returns:
            저장된 파일 경로
        """
        import_file = Path(import_path)

        if not import_file.exists():
            raise FileNotFoundError(f"프로필 파일 없음: {import_path}")

        # 파일 로드
        with open(import_file, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)

        # 프로필 이름 결정
        if profile_name is None:
            profile_name = import_file.stem.replace('_profile', '')

        # 저장
        return self.save_profile(profile_data, profile_name)


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("채널 프로필 관리 테스트")
    print("=" * 60)

    profile_manager = ChannelProfile()

    # 1. 기본 프로필 로드
    print("\n1️⃣ 기본 프로필 로드")
    default = profile_manager.get_default_profile()
    print(f"  채널명: {default['channel_name']}")
    print(f"  메인 색상: {default['brand_colors']['primary']}")
    print(f"  워터마크: {default['watermark_text']}")

    # 2. 커스텀 프로필 저장
    print("\n2️⃣ 커스텀 프로필 저장")
    custom_profile = {
        'channel_name': 'Test Channel',
        'logo_path': 'test_logo.png',
        'brand_colors': {
            'primary': '#00FF00',
            'secondary': '#0000FF'
        },
        'brand_font': 'Arial',
        'watermark_text': '@TestChannel'
    }
    profile_manager.save_profile(custom_profile, 'test')

    # 3. 프로필 목록
    print("\n3️⃣ 저장된 프로필 목록")
    profiles = profile_manager.list_profiles()
    print(f"  프로필: {profiles}")

    # 4. 프로필 업데이트
    print("\n4️⃣ 프로필 업데이트")
    profile_manager.update_profile('test', {
        'brand_colors': {'primary': '#FF0000'}
    })

    # 5. 프로필 로드 (업데이트 확인)
    print("\n5️⃣ 업데이트된 프로필 로드")
    updated = profile_manager.load_profile('test')
    print(f"  메인 색상: {updated['brand_colors']['primary']}")

    print("\n" + "=" * 60)
