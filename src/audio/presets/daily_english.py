"""
Daily English Mecca 전용 사운드 프리셋
"""

# Daily English Mecca 비디오 생성용 프리셋
DAILY_ENGLISH_PRESET = {
    'name': 'Daily English Mecca',
    'description': '영어 학습 비디오 생성용 기본 프리셋',

    # 배경음악
    'background_music': {
        'mood': 'energetic',
        'volume': 0.05,  # 5% 볼륨 (TTS 방해하지 않도록)
        'duration': None,  # 비디오 길이에 맞춤
        'fade_in': 0.5,
        'fade_out': 1.0,
    },

    # 인트로 효과음
    'intro_sound': {
        'effect': 'start',
        'volume': 0.6,
        'delay': 0.0,  # 인트로 시작과 동시
    },

    # 문장 전환 효과음
    'sentence_transition': {
        'effect': 'whoosh',
        'volume': 0.3,
        'delay': 0.0,  # 각 문장 시작 0.1초 전
    },

    # 정답 효과음 (학습 모드용)
    'correct_answer': {
        'effect': 'correct',
        'volume': 0.7,
    },

    # 오답 효과음 (학습 모드용)
    'wrong_answer': {
        'effect': 'wrong',
        'volume': 0.5,
    },

    # 아웃트로 효과음
    'outro_sound': {
        'effect': 'finish',
        'volume': 0.6,
        'delay': 0.0,
    },
}

# 퀴즈 모드 프리셋
QUIZ_PRESET = {
    'name': 'English Quiz',
    'description': '영어 퀴즈 모드용 프리셋',

    # 배경음악
    'background_music': {
        'mood': 'focus',
        'volume': 0.03,
        'duration': None,
    },

    # 문제 시작
    'question_start': {
        'effect': 'notification',
        'volume': 0.5,
    },

    # 정답
    'correct': {
        'effect': 'celebration',
        'volume': 0.8,
    },

    # 오답
    'wrong': {
        'effect': 'wrong',
        'volume': 0.5,
    },

    # 타이머 (시간 제한)
    'timer_tick': {
        'effect': 'click',
        'volume': 0.3,
    },

    # 최종 성공
    'final_success': {
        'effect': 'celebration',
        'volume': 1.0,
    },
}

# 인터랙티브 UI 프리셋
INTERACTIVE_PRESET = {
    'name': 'Interactive UI',
    'description': '웹 인터페이스용 UI 효과음 프리셋',

    # 버튼 클릭
    'button_click': {
        'effect': 'click',
        'volume': 0.4,
    },

    # 호버
    'button_hover': {
        'effect': 'hover',
        'volume': 0.2,
    },

    # 성공 메시지
    'success_message': {
        'effect': 'success',
        'volume': 0.6,
    },

    # 에러 메시지
    'error_message': {
        'effect': 'error',
        'volume': 0.6,
    },

    # 알림
    'notification': {
        'effect': 'notification',
        'volume': 0.5,
    },

    # 토글 (ON/OFF)
    'toggle_switch': {
        'effect': 'toggle',
        'volume': 0.3,
    },
}

# 차분한 학습 모드 프리셋
CALM_LEARNING_PRESET = {
    'name': 'Calm Learning',
    'description': '차분한 분위기의 학습용 프리셋',

    # 배경음악
    'background_music': {
        'mood': 'calm',
        'volume': 0.04,
        'duration': None,
    },

    # 문장 전환
    'transition': {
        'effect': 'fade',
        'volume': 0.2,
    },

    # 정답
    'correct': {
        'effect': 'encouragement',
        'volume': 0.5,
    },

    # 완료
    'finish': {
        'effect': 'finish',
        'volume': 0.5,
    },
}

# 프리셋 딕셔너리
PRESETS = {
    'daily_english': DAILY_ENGLISH_PRESET,
    'quiz': QUIZ_PRESET,
    'interactive': INTERACTIVE_PRESET,
    'calm_learning': CALM_LEARNING_PRESET,
}


def get_preset(preset_name: str) -> dict:
    """
    프리셋 가져오기

    Args:
        preset_name: 프리셋 이름

    Returns:
        프리셋 딕셔너리

    Raises:
        ValueError: 알 수 없는 프리셋
    """
    if preset_name not in PRESETS:
        available = ', '.join(PRESETS.keys())
        raise ValueError(f"알 수 없는 프리셋: {preset_name}\n사용 가능: {available}")

    return PRESETS[preset_name]


def list_presets() -> list:
    """사용 가능한 프리셋 목록"""
    return [
        {
            'name': key,
            'title': preset['name'],
            'description': preset['description']
        }
        for key, preset in PRESETS.items()
    ]


def print_presets():
    """프리셋 정보 출력"""
    print("\n" + "=" * 60)
    print("📦 Daily English Mecca - 사운드 프리셋")
    print("=" * 60)

    for key, preset in PRESETS.items():
        print(f"\n🎵 {preset['name']} ({key})")
        print(f"   {preset['description']}")
        print("-" * 60)

        for sound_key, sound_info in preset.items():
            if sound_key in ['name', 'description']:
                continue

            if 'mood' in sound_info:
                print(f"   🎶 {sound_key}: {sound_info['mood']} (배경음악)")
            elif 'effect' in sound_info:
                print(f"   🔊 {sound_key}: {sound_info['effect']} (효과음)")

    print("\n" + "=" * 60)
    print("💡 사용 방법:")
    print("   from src.audio.presets.daily_english import get_preset")
    print("   preset = get_preset('daily_english')")
    print("=" * 60 + "\n")
