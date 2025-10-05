#!/usr/bin/env python3
"""
MoviePy 2.x 기본 기능 테스트
"""

from moviepy import TextClip, ColorClip, CompositeVideoClip, vfx

print("MoviePy 버전 테스트 시작...")

try:
    # 1. ColorClip 테스트
    print("1. ColorClip 생성 중...")
    bg = ColorClip(size=(1080, 1920), color=(100, 150, 255), duration=2)
    print("   ✓ ColorClip 생성 성공")

    # 2. TextClip 테스트
    print("2. TextClip 생성 중...")
    txt = TextClip(
        text="테스트\nTest",
        font_size=80,
        color='white',
        font='Arial',
        size=(980, None),
        method='caption',
        text_align='center'
    )
    print("   ✓ TextClip 생성 성공")

    # 3. with_* 메서드 테스트
    print("3. with_position, with_duration 테스트 중...")
    txt = txt.with_position('center').with_duration(2)
    print("   ✓ with_position, with_duration 성공")

    # 4. with_effects 테스트
    print("4. with_effects (FadeIn, FadeOut) 테스트 중...")
    txt = txt.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
    print("   ✓ with_effects 성공")

    # 5. CompositeVideoClip 테스트
    print("5. CompositeVideoClip 생성 중...")
    final = CompositeVideoClip([bg, txt], size=(1080, 1920))
    print("   ✓ CompositeVideoClip 생성 성공")

    print("\n✅ 모든 테스트 통과!")
    print("MoviePy 2.x 설정이 올바릅니다.")

except Exception as e:
    print(f"\n❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
