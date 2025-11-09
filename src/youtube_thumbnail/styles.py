"""
썸네일 스타일 템플릿 시스템

5가지 전문적인 스타일 템플릿 제공
Fire English, Minimalist, Bold & Bright, Professional, Custom

Author: Kelly & Claude Code
Date: 2025-11-09
"""
from typing import Dict, Any


# ============================================================
# 스타일 템플릿 정의 (5종)
# ============================================================

THUMBNAIL_STYLES: Dict[str, Dict[str, Any]] = {
    # 1. Fire English 스타일 (구독자 95만명 채널)
    'fire_english': {
        'name': 'Fire English 스타일',
        'description': '빨간 헤더 + 큰 텍스트 + 숫자 배지',

        # 레이아웃
        'layout': {
            'header_enabled': True,
            'header_height': 120,
            'header_color': '#D32F2F',  # 빨간색
            'background_color': '#FFFFFF',  # 흰색
            'character_position': 'center',  # 중앙
            'character_opacity': 0.9
        },

        # 텍스트
        'text': {
            'main': {
                'position': 'header',  # 헤더 영역
                'y_offset': 30,
                'font_size': 100,
                'color': '#FFFFFF',
                'stroke_width': 0,
                'shadow': True,
                'shadow_offset': 4,
                'shadow_color': '#000000'
            },
            'subtitle': {
                'position': 'bottom',
                'y_offset': -150,
                'font_size': 60,
                'color': '#FFFFFF',
                'background_box': True,
                'box_color': '#000000',
                'box_outline': '#FFD700',  # 금색
                'box_outline_width': 3
            }
        },

        # 배지
        'badges': {
            'sentence_count': {
                'enabled': True,
                'position': 'top-left',
                'x': 30,
                'y': 150,
                'size': 80,
                'bg_color': '#FF5722',  # 주황색
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 4
            },
            'duration': {
                'enabled': True,
                'position': 'bottom-right',
                'x_offset': -150,
                'y_offset': -80,
                'width': 120,
                'height': 50,
                'bg_color': '#000000',
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 2
            }
        }
    },

    # 2. Minimalist 스타일 (심플 깔끔)
    'minimalist': {
        'name': 'Minimalist',
        'description': '심플하고 깔끔한 디자인',

        'layout': {
            'header_enabled': False,
            'background_color': '#F5F5F5',  # 밝은 회색
            'character_position': 'center',
            'character_opacity': 0.8
        },

        'text': {
            'main': {
                'position': 'center',
                'y_offset': 200,
                'font_size': 120,
                'color': '#212121',  # 진한 회색
                'stroke_width': 0,
                'shadow': False
            },
            'subtitle': {
                'position': 'center',
                'y_offset': 350,
                'font_size': 50,
                'color': '#757575',  # 중간 회색
                'background_box': False
            }
        },

        'badges': {
            'sentence_count': {
                'enabled': True,
                'position': 'top-left',
                'x': 30,
                'y': 30,
                'size': 60,
                'bg_color': '#424242',
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 2
            },
            'duration': {
                'enabled': True,
                'position': 'bottom-right',
                'x_offset': -130,
                'y_offset': -50,
                'width': 100,
                'height': 40,
                'bg_color': '#424242',
                'text_color': '#FFFFFF',
                'border_color': None,
                'border_width': 0
            }
        }
    },

    # 3. Bold & Bright 스타일 (화려한 색상)
    'bold_bright': {
        'name': 'Bold & Bright',
        'description': '강렬한 색상 + 눈에 띄는 디자인',

        'layout': {
            'header_enabled': True,
            'header_height': 150,
            'header_color': '#E91E63',  # 핑크
            'background_type': 'gradient',  # 그라데이션
            'gradient_colors': ['#E91E63', '#FFEB3B'],  # 핑크→노랑
            'character_position': 'left',
            'character_opacity': 1.0
        },

        'text': {
            'main': {
                'position': 'header',
                'y_offset': 40,
                'font_size': 110,
                'color': '#FFFFFF',
                'stroke_width': 6,
                'stroke_color': '#000000',
                'shadow': True,
                'shadow_offset': 5,
                'shadow_color': '#000000'
            },
            'subtitle': {
                'position': 'bottom',
                'y_offset': -120,
                'font_size': 70,
                'color': '#000000',
                'background_box': True,
                'box_color': '#FFEB3B',  # 노란색
                'box_outline': '#E91E63',  # 핑크
                'box_outline_width': 5
            }
        },

        'badges': {
            'sentence_count': {
                'enabled': True,
                'position': 'top-right',
                'x_offset': -120,
                'y': 40,
                'size': 100,
                'bg_color': '#00BCD4',  # 청록색
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 5
            },
            'duration': {
                'enabled': True,
                'position': 'bottom-left',
                'x': 30,
                'y_offset': -70,
                'width': 130,
                'height': 55,
                'bg_color': '#FF5722',  # 주황색
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 3
            }
        }
    },

    # 4. Professional 스타일 (비즈니스 느낌)
    'professional': {
        'name': 'Professional',
        'description': '비즈니스/교육용 전문적인 디자인',

        'layout': {
            'header_enabled': True,
            'header_height': 100,
            'header_color': '#1976D2',  # 파란색
            'background_color': '#ECEFF1',  # 밝은 회색-파랑
            'character_position': 'right',
            'character_opacity': 0.85
        },

        'text': {
            'main': {
                'position': 'header',
                'y_offset': 25,
                'font_size': 90,
                'color': '#FFFFFF',
                'stroke_width': 0,
                'shadow': False
            },
            'subtitle': {
                'position': 'bottom',
                'y_offset': -100,
                'font_size': 55,
                'color': '#FFFFFF',
                'background_box': True,
                'box_color': '#37474F',  # 진한 회색
                'box_outline': '#1976D2',  # 파란색
                'box_outline_width': 2
            }
        },

        'badges': {
            'sentence_count': {
                'enabled': True,
                'position': 'top-left',
                'x': 40,
                'y': 120,
                'size': 70,
                'bg_color': '#1976D2',
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 3
            },
            'duration': {
                'enabled': True,
                'position': 'bottom-right',
                'x_offset': -140,
                'y_offset': -60,
                'width': 110,
                'height': 45,
                'bg_color': '#37474F',
                'text_color': '#FFFFFF',
                'border_color': None,
                'border_width': 0
            }
        }
    },

    # 5. Custom 스타일 (참고 이미지 기반)
    'custom': {
        'name': 'Custom (참고 이미지 분석)',
        'description': 'GPT-4 Vision으로 참고 이미지의 스타일을 자동 분석',

        # 동적으로 GPT-4 Vision이 채움
        'layout': {},
        'text': {},
        'badges': {}
    }
}


# ============================================================
# 헬퍼 함수
# ============================================================

def get_style(style_name: str) -> Dict[str, Any]:
    """
    스타일 템플릿 가져오기

    Args:
        style_name: 스타일 이름 ('fire_english', 'minimalist', 등)

    Returns:
        스타일 설정 dict

    Raises:
        KeyError: 스타일이 없으면

    Example:
        >>> style = get_style('fire_english')
        >>> print(style['name'])
        'Fire English 스타일'
    """
    if style_name not in THUMBNAIL_STYLES:
        raise KeyError(f"스타일 없음: {style_name}. 사용 가능: {list(THUMBNAIL_STYLES.keys())}")

    return THUMBNAIL_STYLES[style_name]


def list_styles() -> list[dict]:
    """
    모든 스타일 목록

    Returns:
        스타일 정보 리스트

    Example:
        >>> styles = list_styles()
        >>> for style in styles:
                print(f"{style['id']}: {style['name']}")
    """
    return [
        {
            'id': key,
            'name': style['name'],
            'description': style['description']
        }
        for key, style in THUMBNAIL_STYLES.items()
    ]


def merge_style_with_brand(style: dict, brand_colors: dict) -> dict:
    """
    스타일 템플릿에 브랜드 색상 병합

    Args:
        style: 기본 스타일 dict
        brand_colors: 브랜드 색상 dict

    Returns:
        병합된 스타일 dict

    Example:
        >>> style = get_style('fire_english')
        >>> brand = {'primary': '#00FF00', 'secondary': '#0000FF'}
        >>> merged = merge_style_with_brand(style, brand)
        >>> # 헤더 색상이 브랜드 primary로 변경됨
    """
    import copy
    merged = copy.deepcopy(style)

    # 헤더 색상 (primary)
    if 'layout' in merged and 'header_color' in merged['layout']:
        if 'primary' in brand_colors:
            merged['layout']['header_color'] = brand_colors['primary']

    # 강조 색상 (accent)
    if 'text' in merged and 'subtitle' in merged['text']:
        if 'box_outline' in merged['text']['subtitle'] and 'accent' in brand_colors:
            merged['text']['subtitle']['box_outline'] = brand_colors['accent']

    return merged


def create_custom_style_from_analysis(analysis: dict) -> dict:
    """
    GPT-4 Vision 분석 결과로 커스텀 스타일 생성

    Args:
        analysis: GPT-4 Vision 분석 결과

    Returns:
        커스텀 스타일 dict

    Example:
        >>> analysis = {
                'color_palette': ['#FF0000', '#0000FF'],
                'layout': {'header_height': 120, ...},
                'typography': {'main_font_size': 100, ...}
            }
        >>> custom_style = create_custom_style_from_analysis(analysis)
    """
    layout = analysis.get('layout', {})
    typography = analysis.get('typography', {})
    colors = analysis.get('color_palette', ['#000000', '#FFFFFF'])

    custom_style = {
        'name': 'Custom (분석됨)',
        'description': '참고 이미지 스타일 자동 분석',

        'layout': {
            'header_enabled': layout.get('header', {}).get('height', 0) > 0,
            'header_height': layout.get('header', {}).get('height', 100),
            'header_color': layout.get('header', {}).get('color', colors[0]),
            'background_color': analysis.get('background', {}).get('colors', [colors[-1]])[0],
            'character_position': layout.get('character_position', 'center'),
            'character_opacity': 0.9
        },

        'text': {
            'main': {
                'position': 'header' if layout.get('header', {}).get('height', 0) > 0 else 'center',
                'y_offset': 30,
                'font_size': typography.get('main_font_size', 100),
                'color': '#FFFFFF',
                'stroke_width': 0,
                'shadow': True,
                'shadow_offset': 4,
                'shadow_color': '#000000'
            },
            'subtitle': {
                'position': 'bottom',
                'y_offset': -150,
                'font_size': typography.get('subtitle_font_size', 60),
                'color': '#FFFFFF',
                'background_box': True,
                'box_color': colors[1] if len(colors) > 1 else '#000000',
                'box_outline': colors[0],
                'box_outline_width': 3
            }
        },

        'badges': {
            'sentence_count': {
                'enabled': True,
                'position': 'top-left',
                'x': 30,
                'y': 150,
                'size': 80,
                'bg_color': colors[0],
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 4
            },
            'duration': {
                'enabled': True,
                'position': 'bottom-right',
                'x_offset': -150,
                'y_offset': -80,
                'width': 120,
                'height': 50,
                'bg_color': '#000000',
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'border_width': 2
            }
        }
    }

    return custom_style


# 테스트 코드
if __name__ == '__main__':
    print("=" * 60)
    print("스타일 템플릿 시스템 테스트")
    print("=" * 60)

    # 1. 스타일 목록
    print("\n1️⃣ 사용 가능한 스타일:")
    for style_info in list_styles():
        print(f"  - {style_info['id']}: {style_info['name']}")
        print(f"    {style_info['description']}")

    # 2. Fire English 스타일 가져오기
    print("\n2️⃣ Fire English 스타일 상세:")
    fire_style = get_style('fire_english')
    print(f"  헤더 색상: {fire_style['layout']['header_color']}")
    print(f"  메인 텍스트 크기: {fire_style['text']['main']['font_size']}px")

    # 3. 브랜드 색상 병합
    print("\n3️⃣ 브랜드 색상 병합:")
    brand_colors = {'primary': '#00FF00', 'accent': '#FFD700'}
    merged = merge_style_with_brand(fire_style, brand_colors)
    print(f"  원래 헤더: {fire_style['layout']['header_color']}")
    print(f"  병합 후: {merged['layout']['header_color']}")

    print("\n" + "=" * 60)
