"""
기존 리소스를 새 구조로 마이그레이션

실행 전 반드시 백업하세요!
"""
import shutil
from pathlib import Path
from src.resource_manager_v2 import ResourceManager


def migrate_resources(dry_run=True):
    """
    기존 output/ 구조를 새 구조로 마이그레이션

    Args:
        dry_run: True면 실제 이동하지 않고 목록만 출력
    """
    print("\n" + "=" * 70)
    print("📦 리소스 마이그레이션 시작")
    print("=" * 70)

    manager = ResourceManager("daily-english-mecca")

    # 기존 경로
    old_output = Path("output")
    old_resources = old_output / "resources"
    old_images = old_resources / "images"
    old_audio_cache = old_resources / "audio"
    old_music = old_resources / "sounds" / "music"

    # === 1. 캐시된 이미지 이동 ===
    print("\n[1/4] 캐시된 이미지 이동...")
    if old_images.exists():
        image_files = list(old_images.glob("*.png"))
        print(f"  → {len(image_files)}개 이미지 발견")

        for image_file in image_files:
            dest = manager.cache_dir / 'images' / image_file.name

            if dry_run:
                print(f"  [Dry Run] {image_file.name} → {dest}")
            else:
                shutil.copy2(image_file, dest)
                print(f"  ✓ {image_file.name}")

    # === 2. 캐시된 오디오 이동 ===
    print("\n[2/4] 캐시된 오디오 이동...")
    if old_audio_cache.exists():
        audio_files = list(old_audio_cache.glob("*.mp3"))
        print(f"  → {len(audio_files)}개 오디오 발견")

        for audio_file in audio_files:
            dest = manager.cache_dir / 'audio' / audio_file.name

            if dry_run:
                print(f"  [Dry Run] {audio_file.name} → {dest}")
            else:
                shutil.copy2(audio_file, dest)
                print(f"  ✓ {audio_file.name}")

    # === 3. 배경음악 이동 ===
    print("\n[3/4] 배경음악 라이브러리로 이동...")
    if old_music.exists():
        music_files = list(old_music.glob("*.mp3"))
        print(f"  → {len(music_files)}개 음악 발견")

        for music_file in music_files:
            # 파일명에서 무드 추출 (예: energetic_Happy_Alley.mp3)
            filename = music_file.stem
            if '_' in filename:
                mood = filename.split('_')[0]  # energetic, calm, upbeat, focus
            else:
                mood = "other"

            dest_dir = manager.library_dir / 'music' / mood
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / music_file.name

            if dry_run:
                print(f"  [Dry Run] {music_file.name} → music/{mood}/")
            else:
                shutil.copy2(music_file, dest)
                print(f"  ✓ {music_file.name} → {mood}/")

    # === 4. 기존 비디오 프로젝트 생성 ===
    print("\n[4/4] 기존 비디오 프로젝트 데이터 생성...")
    old_videos = old_output / "videos"
    if old_videos.exists():
        video_files = list(old_videos.glob("*.mp4"))
        print(f"  → {len(video_files)}개 비디오 발견")

        for video_file in video_files:
            # 비디오 ID 추출 (예: daily_english_20251007_123742.mp4)
            video_id = video_file.stem.replace("daily_english_", "")

            if dry_run:
                print(f"  [Dry Run] 프로젝트 생성: {video_id}")
            else:
                # 프로젝트 생성만 (비디오는 이미 output/videos/에 있음)
                manager.create_project(video_id)

                print(f"  ✓ 프로젝트 생성: {video_id}")

    # === 마이그레이션 완료 ===
    print("\n" + "=" * 70)
    if dry_run:
        print("✅ [Dry Run] 마이그레이션 시뮬레이션 완료!")
        print("\n실제로 실행하려면:")
        print("  python migrate_resources.py --execute")
    else:
        print("✅ 마이그레이션 완료!")
        print("\n새 리소스 통계:")
        stats = manager.get_stats()
        print(f"  - 캐시된 이미지: {stats['shared_resources']['cached_images']}개")
        print(f"  - 캐시된 오디오: {stats['shared_resources']['cached_audio']}개")
        print(f"  - 라이브러리 음악: {stats['shared_resources']['library_music']}개")
        print(f"  - 프로젝트: {stats['projects']['total']}개")
        print(f"  - 비디오: {stats['videos']['total']}개")

        print("\n⚠️ 기존 output/ 폴더는 백업 후 삭제하세요:")
        print("  mv output output_backup")

    print("=" * 70)


if __name__ == "__main__":
    import sys

    # 커맨드 라인 인자 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("\n⚠️  실제 마이그레이션을 시작합니다!")
        print("계속하시겠습니까? (y/n): ", end="")
        confirm = input().lower()

        if confirm == 'y':
            migrate_resources(dry_run=False)
        else:
            print("취소되었습니다.")
    else:
        print("\n💡 이것은 Dry Run입니다. 실제로 파일을 이동하지 않습니다.")
        print("실제 마이그레이션: python migrate_resources.py --execute\n")
        migrate_resources(dry_run=True)
