"""
통합 리소스 관리 모듈 v2.0
- 웹/데스크탑 호환
- 프로젝트 간 공유
- 캐시 최적화
"""
import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class ResourceManager:
    """
    통합 리소스 관리자

    특징:
    - 공유 리소스 풀 (프로젝트 외부)
    - MD5 해시 기반 캐싱
    - 프로젝트별 격리
    - 웹/데스크탑 호환
    """

    def __init__(self, project_name: str = "daily-english-mecca", config_path: Optional[str] = None):
        """
        ResourceManager 초기화

        Args:
            project_name: 프로젝트 이름 (예: "daily-english-mecca", "tech-news-digest")
            config_path: 설정 파일 경로 (기본: ./.resource_config.json)
        """
        self.project_name = project_name

        # 설정 파일 로드
        if config_path is None:
            config_path = Path.cwd() / '.resource_config.json'

        self.config = self._load_or_create_config(config_path)

        # 공유 리소스 풀 경로
        self.shared_root = Path(self.config['shared_resource_path']).expanduser()
        self.cache_dir = self.shared_root / 'cache'
        self.library_dir = self.shared_root / 'library'
        self.templates_dir = self.shared_root / 'templates'

        # 프로젝트별 작업 공간
        self.project_output = Path(self.config['project_output_path'])
        self.projects_dir = self.project_output / 'projects'
        self.videos_dir = self.project_output / 'videos'

        # 디렉토리 생성
        self._ensure_directories()

    def _load_or_create_config(self, config_path: Path) -> Dict:
        """설정 파일 로드 또는 생성"""
        default_config = {
            "version": "2.0",
            "shared_resource_path": "~/ContentCreatorResources",
            "project_output_path": "./output",
            "cache_enabled": True,
            "auto_cleanup": {
                "enabled": False,
                "older_than_days": 30
            }
        }

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 누락된 키 채우기
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # 기본 설정 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            print(f"✓ 리소스 설정 파일 생성: {config_path}")
            return default_config

    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            # 공유 리소스
            self.cache_dir / 'images',
            self.cache_dir / 'audio',
            self.cache_dir / 'fonts',
            self.library_dir / 'backgrounds',
            self.library_dir / 'music',
            self.library_dir / 'effects',
            self.templates_dir / self.project_name,
            # 프로젝트 작업 공간
            self.projects_dir,
            self.videos_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_hash(self, text: str) -> str:
        """텍스트로부터 MD5 해시 생성"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # ===== 캐시 리소스 관리 =====

    def get_cached_image_path(self, prompt: str) -> Path:
        """
        캐시된 이미지 경로 반환

        Args:
            prompt: DALL-E 프롬프트

        Returns:
            이미지 파일 경로 (존재 여부와 무관)
        """
        hash_value = self._generate_hash(prompt)
        return self.cache_dir / 'images' / f"{hash_value}.png"

    def get_cached_audio_path(self, sentence: str, voice: str = "nova") -> Path:
        """
        캐시된 오디오 경로 반환

        Args:
            sentence: 영어 문장
            voice: TTS 음성

        Returns:
            오디오 파일 경로 (존재 여부와 무관)
        """
        hash_value = self._generate_hash(f"{sentence}_{voice}")
        return self.cache_dir / 'audio' / f"{hash_value}.mp3"

    def cache_exists(self, cache_path: Path) -> bool:
        """캐시 파일 존재 여부 확인"""
        return cache_path.exists()

    # ===== 프로젝트 관리 =====

    def create_project(self, video_id: Optional[str] = None) -> str:
        """
        새 프로젝트 생성

        Args:
            video_id: 비디오 ID (기본: 타임스탬프)

        Returns:
            생성된 프로젝트 ID
        """
        if video_id is None:
            video_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        project_dir = self.projects_dir / video_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # 프로젝트 설정 파일 생성
        project_data = {
            "id": video_id,
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "status": "in_progress",
            "clips": [],
            "resources": []
        }

        project_file = project_dir / 'project.json'
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)

        # clips 폴더 생성
        (project_dir / 'clips').mkdir(exist_ok=True)

        return video_id

    def get_project_dir(self, video_id: str) -> Path:
        """프로젝트 디렉토리 경로 반환"""
        return self.projects_dir / video_id

    def add_resource_to_project(self, video_id: str, resource_type: str,
                                resource_path: Path, metadata: Optional[Dict] = None):
        """
        프로젝트에 리소스 참조 추가

        Args:
            video_id: 프로젝트 ID
            resource_type: 리소스 타입 (image, audio, music, etc.)
            resource_path: 리소스 경로 (캐시 또는 라이브러리)
            metadata: 추가 메타데이터
        """
        project_file = self.get_project_dir(video_id) / 'project.json'

        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        resource_entry = {
            "type": resource_type,
            "path": str(resource_path),
            "added_at": datetime.now().isoformat()
        }

        if metadata:
            resource_entry["metadata"] = metadata

        project_data['resources'].append(resource_entry)

        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)

    def get_video_output_path(self, video_id: str) -> Path:
        """최종 비디오 출력 경로 반환"""
        return self.videos_dir / f"{video_id}.mp4"

    # ===== 라이브러리 관리 =====

    def get_library_music(self, mood: str = "energetic") -> List[Path]:
        """
        라이브러리에서 배경음악 가져오기

        Args:
            mood: 음악 무드 (energetic, calm, upbeat, focus)

        Returns:
            음악 파일 경로 리스트
        """
        music_dir = self.library_dir / 'music' / mood
        if not music_dir.exists():
            return []

        return list(music_dir.glob("*.mp3"))

    def copy_to_library(self, source_path: Path, category: str, subcategory: Optional[str] = None):
        """
        파일을 라이브러리로 복사

        Args:
            source_path: 원본 파일 경로
            category: 카테고리 (backgrounds, music, effects)
            subcategory: 하위 카테고리 (선택사항)
        """
        if subcategory:
            dest_dir = self.library_dir / category / subcategory
        else:
            dest_dir = self.library_dir / category

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / source_path.name

        shutil.copy2(source_path, dest_path)
        print(f"✓ 라이브러리에 복사: {dest_path}")

        return dest_path

    # ===== 통계 & 정리 =====

    def get_stats(self) -> Dict:
        """리소스 통계 반환"""
        stats = {
            "shared_resources": {
                "cached_images": len(list((self.cache_dir / 'images').glob("*.png"))),
                "cached_audio": len(list((self.cache_dir / 'audio').glob("*.mp3"))),
                "library_music": len(list((self.library_dir / 'music').rglob("*.mp3"))),
            },
            "projects": {
                "total": len(list(self.projects_dir.iterdir())),
                "in_progress": 0,
                "completed": 0
            },
            "videos": {
                "total": len(list(self.videos_dir.glob("*.mp4"))),
            },
            "storage": {
                "cache_size_mb": self._get_directory_size(self.cache_dir),
                "library_size_mb": self._get_directory_size(self.library_dir),
                "projects_size_mb": self._get_directory_size(self.projects_dir),
                "videos_size_mb": self._get_directory_size(self.videos_dir),
            }
        }

        # 프로젝트 상태 카운트
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / 'project.json'
                if project_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        status = project_data.get('status', 'unknown')
                        if status in stats['projects']:
                            stats['projects'][status] += 1

        return stats

    def _get_directory_size(self, directory: Path) -> float:
        """디렉토리 크기 계산 (MB)"""
        if not directory.exists():
            return 0.0

        total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
        return round(total_size / (1024 * 1024), 2)

    def cleanup_old_projects(self, older_than_days: int = 30, dry_run: bool = True):
        """
        오래된 프로젝트 정리

        Args:
            older_than_days: 이 일수보다 오래된 프로젝트 삭제
            dry_run: True면 삭제하지 않고 목록만 출력
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            project_file = project_dir / 'project.json'
            if not project_file.exists():
                continue

            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            created_at = datetime.fromisoformat(project_data['created_at'])

            if created_at < cutoff_date:
                if dry_run:
                    print(f"[Dry Run] 삭제 대상: {project_dir.name} (생성일: {created_at.date()})")
                else:
                    shutil.rmtree(project_dir)
                    print(f"✓ 삭제됨: {project_dir.name}")
                deleted_count += 1

        if dry_run:
            print(f"\n총 {deleted_count}개 프로젝트가 삭제 대상입니다.")
            print("실제 삭제하려면 dry_run=False로 실행하세요.")
        else:
            print(f"\n총 {deleted_count}개 프로젝트를 삭제했습니다.")


# ===== 편의 함수 =====

def get_resource_manager(project_name: str = "daily-english-mecca") -> ResourceManager:
    """
    ResourceManager 싱글톤 인스턴스 반환

    Args:
        project_name: 프로젝트 이름

    Returns:
        ResourceManager 인스턴스
    """
    if not hasattr(get_resource_manager, '_instances'):
        get_resource_manager._instances = {}

    if project_name not in get_resource_manager._instances:
        get_resource_manager._instances[project_name] = ResourceManager(project_name)

    return get_resource_manager._instances[project_name]


if __name__ == "__main__":
    # 테스트
    manager = ResourceManager("daily-english-mecca")

    print("\n📊 리소스 통계:")
    print("=" * 60)
    stats = manager.get_stats()

    print(f"\n공유 리소스:")
    print(f"  - 캐시된 이미지: {stats['shared_resources']['cached_images']}개")
    print(f"  - 캐시된 오디오: {stats['shared_resources']['cached_audio']}개")
    print(f"  - 라이브러리 음악: {stats['shared_resources']['library_music']}개")

    print(f"\n프로젝트:")
    print(f"  - 총 프로젝트: {stats['projects']['total']}개")
    print(f"  - 진행 중: {stats['projects']['in_progress']}개")
    print(f"  - 완료: {stats['projects']['completed']}개")

    print(f"\n비디오:")
    print(f"  - 총 비디오: {stats['videos']['total']}개")

    print(f"\n저장 공간:")
    print(f"  - 캐시: {stats['storage']['cache_size_mb']} MB")
    print(f"  - 라이브러리: {stats['storage']['library_size_mb']} MB")
    print(f"  - 프로젝트: {stats['storage']['projects_size_mb']} MB")
    print(f"  - 비디오: {stats['storage']['videos_size_mb']} MB")
