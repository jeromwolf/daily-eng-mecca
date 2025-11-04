#!/usr/bin/env python3
"""
Shorts 비디오 Kelly 캐릭터 테스트
인트로/아웃트로에 Kelly 캐릭터가 배경으로 표시되는지 확인
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from video_creator import VideoCreator
from resource_manager import ResourceManager

def test_shorts_kelly():
    """Shorts 비디오에 Kelly 캐릭터 배경 테스트"""

    print("=" * 80)
    print("Shorts 비디오 Kelly 캐릭터 테스트 시작")
    print("=" * 80)

    # 테스트 데이터
    sentences = [
        "Break a leg!",
        "Piece of cake!",
        "Hit the books!"
    ]

    translations = [
        "행운을 빌어!",
        "식은 죽 먹기!",
        "열심히 공부하다!"
    ]

    # 더미 이미지 경로 (실제로는 사용되지 않지만 필수)
    image_paths = [
        str(project_root / "output/resources/images/kelly_casual_hoodie.png"),
        str(project_root / "output/resources/images/kelly_casual_hoodie.png"),
        str(project_root / "output/resources/images/kelly_casual_hoodie.png"),
    ]

    # 더미 오디오 정보
    audio_info = []
    for i, sentence in enumerate(sentences):
        audio_info.append({
            'sentence': sentence,
            'voices': {
                'alloy': {
                    'path': f'dummy_audio_{i}_alloy.mp3',
                    'duration': 2.0
                },
                'nova': {
                    'path': f'dummy_audio_{i}_nova.mp3',
                    'duration': 2.0
                },
                'shimmer': {
                    'path': f'dummy_audio_{i}_shimmer.mp3',
                    'duration': 2.0
                }
            }
        })

    # 출력 경로
    output_dir = project_root / "output" / "test_shorts_kelly"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "test_shorts_with_kelly.mp4"

    print(f"\n출력 경로: {output_path}")

    # ResourceManager 생성
    resource_manager = ResourceManager(base_dir=str(project_root / "output"))

    # VideoCreator 생성 (Shorts 모드)
    print("\nVideoCreator 생성 중 (Shorts 모드)...")
    creator = VideoCreator(
        format_type='9:16',  # Shorts 포맷
        resource_manager=resource_manager
    )

    print("\n✓ Kelly 캐릭터 인트로/아웃트로 테스트:")
    print("  - 인트로: Kelly 캐릭터 배경 + 텍스트 오버레이")
    print("  - 아웃트로: Kelly 캐릭터 배경 + CTA 텍스트")

    # 비디오 생성
    print("\n비디오 생성 시작...")
    print("(인트로/아웃트로에서 Kelly 이미지 로드 메시지 확인)")
    print("-" * 80)

    try:
        creator.create_video(
            sentences=sentences,
            translations=translations,
            image_paths=image_paths,
            audio_info=audio_info,
            output_path=str(output_path),
            hook_phrase="99% 틀리는 영어 표현!"
        )

        print("-" * 80)
        print(f"\n✅ 테스트 완료!")
        print(f"📁 비디오 저장: {output_path}")
        print(f"📏 파일 크기: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

        print("\n🔍 확인사항:")
        print("  1. 인트로에 Kelly 캐릭터가 전체 화면 배경으로 표시되는가?")
        print("  2. 인트로 텍스트가 Kelly 위에 오버레이되는가?")
        print("  3. 아웃트로에 Kelly 캐릭터가 전체 화면 배경으로 표시되는가?")
        print("  4. 아웃트로 CTA 텍스트가 읽기 쉬운가?")

        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shorts_kelly()
    sys.exit(0 if success else 1)
