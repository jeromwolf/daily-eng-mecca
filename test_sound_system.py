#!/usr/bin/env python3
"""
사운드 시스템 테스트 스크립트
모든 효과음과 배경음악을 생성하여 검증
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.audio.sound_library import SoundLibrary
from src.audio.presets.daily_english import print_presets, list_presets


def test_effects():
    """모든 효과음 생성 테스트"""
    print("\n" + "=" * 60)
    print("🔊 효과음 생성 테스트")
    print("=" * 60)

    library = SoundLibrary()

    # 모든 효과음 타입
    effects = library.list_all_effects()

    print(f"\n총 {len(effects)}개 효과음 생성 중...\n")

    success_count = 0
    failed = []

    for effect_type in effects:
        try:
            file_path = library.get_effect(effect_type)
            file_size = Path(file_path).stat().st_size / 1024  # KB
            print(f"✓ {effect_type:20} → {file_size:.1f} KB")
            success_count += 1
        except Exception as e:
            print(f"✗ {effect_type:20} → 실패: {e}")
            failed.append(effect_type)

    print("\n" + "=" * 60)
    print(f"결과: {success_count}/{len(effects)} 성공")
    if failed:
        print(f"실패: {', '.join(failed)}")
    print("=" * 60)

    return success_count == len(effects)


def test_music():
    """배경음악 다운로드 테스트"""
    print("\n" + "=" * 60)
    print("🎶 배경음악 다운로드 테스트")
    print("=" * 60)

    library = SoundLibrary()

    # 각 무드별로 1개씩 테스트
    moods = ['energetic', 'calm', 'upbeat', 'focus']

    print(f"\n무드별 음악 다운로드 (총 {len(moods)}개)...\n")

    success_count = 0
    failed = []

    for mood in moods:
        try:
            file_path = library.get_background_music(mood=mood, index=0)
            if file_path:
                file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
                print(f"✓ {mood:20} → {file_size:.2f} MB")
                success_count += 1
            else:
                print(f"✗ {mood:20} → 실패 (None 반환)")
                failed.append(mood)
        except Exception as e:
            print(f"✗ {mood:20} → 실패: {e}")
            failed.append(mood)

    print("\n" + "=" * 60)
    print(f"결과: {success_count}/{len(moods)} 성공")
    if failed:
        print(f"실패: {', '.join(failed)}")
    print("=" * 60)

    return success_count == len(moods)


def test_presets():
    """프리셋 적용 테스트"""
    print("\n" + "=" * 60)
    print("📦 프리셋 적용 테스트")
    print("=" * 60)

    library = SoundLibrary()

    # 프리셋 목록 확인
    presets = list_presets()
    print(f"\n사용 가능한 프리셋: {len(presets)}개")
    for preset in presets:
        print(f"  - {preset['name']}: {preset['title']}")

    # daily_english 프리셋 테스트
    print("\n프리셋 'daily_english' 적용 중...")
    try:
        sounds = library.apply_preset('daily_english')

        print(f"\n생성된 사운드: {len(sounds)}개")
        for key, path in sounds.items():
            file_size = Path(path).stat().st_size / 1024
            print(f"  {key:20} → {file_size:.1f} KB")

        print("\n✓ 프리셋 적용 성공")
        return True
    except Exception as e:
        print(f"\n✗ 프리셋 적용 실패: {e}")
        return False


def test_info():
    """정보 출력 테스트"""
    print("\n" + "=" * 60)
    print("ℹ️ 정보 출력 테스트")
    print("=" * 60)

    library = SoundLibrary()

    # 라이브러리 정보
    library.print_info()

    # 배경음악 카탈로그
    library.print_music_catalog()

    # 프리셋 정보
    print_presets()

    return True


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🎵 사운드 시스템 테스트")
    print("=" * 70)

    results = {
        '효과음 생성': test_effects(),
        '배경음악 다운로드': test_music(),
        '프리셋 적용': test_presets(),
        '정보 출력': test_info(),
    }

    # 최종 결과
    print("\n" + "=" * 70)
    print("📊 최종 결과")
    print("=" * 70)

    total = len(results)
    passed = sum(results.values())

    for test_name, result in results.items():
        status = "✓ 통과" if result else "✗ 실패"
        print(f"  {test_name:20} {status}")

    print("=" * 70)
    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n🎉 모든 테스트 통과! 사운드 시스템이 정상 작동합니다.")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
