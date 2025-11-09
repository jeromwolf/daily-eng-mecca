"""
YouTube 썸네일 생성기 독립 라우트

기존 web/app.py의 라우트와 완전히 분리됨.
URL 네임스페이스: /thumbnail-studio/*

Author: Kelly & Claude Code
Date: 2025-11-09
"""
from flask import Blueprint, render_template, request, jsonify, send_file
from pathlib import Path
import os
import sys

# 부모 디렉토리를 Python path에 추가 (src 모듈 import)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.youtube_thumbnail import (
    YouTubeMetadataExtractor,
    ChannelProfile,
    YouTubeThumbnailEngine,
    ThumbnailHistory,
    StyleAnalyzer,
    VariationEngine,
    get_style
)
from src.youtube_thumbnail.title_optimizer import ThumbnailTitleOptimizer

# Blueprint 생성 (독립 네임스페이스)
thumbnail_bp = Blueprint(
    'thumbnail',
    __name__,
    url_prefix='/thumbnail-studio'
)

# 전역 변수 (모듈 초기화)
output_base = project_root / 'output' / 'youtube_thumbnails'
output_base.mkdir(parents=True, exist_ok=True)

metadata_extractor = YouTubeMetadataExtractor()
channel_manager = ChannelProfile(profile_dir=str(output_base / 'profiles'))
history_manager = ThumbnailHistory(session_dir=str(output_base / 'sessions'))

# API 키 로드 (기존 시스템과 동일한 방식)
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    api_key_file = project_root / 'api_key.txt'
    if api_key_file.exists():
        api_key = api_key_file.read_text().strip()

@thumbnail_bp.route('/')
def index():
    """
    썸네일 생성기 메인 페이지 (독립)

    기존 메인 페이지 (/)와 완전히 분리됨.
    """
    return render_template('thumbnail_studio.html')


@thumbnail_bp.route('/api/analyze-channel', methods=['POST'])
def analyze_channel():
    """
    YouTube 채널 정보 추출 API (아이콘 다운로드 포함)

    엔드포인트: POST /thumbnail-studio/api/analyze-channel
    Body: {"channel_url": "https://www.youtube.com/@aion-vibecoding"}

    Returns:
        {
            "success": true,
            "channel_info": {
                "channel_name": str,
                "channel_id": str,
                "icon_url": str,
                "icon_path": str,
                "subscriber_count": int
            }
        }
    """
    try:
        data = request.get_json()
        channel_url = data.get('channel_url', '').strip()

        if not channel_url:
            return jsonify({
                'success': False,
                'error': 'YouTube 채널 URL이 필요합니다.'
            }), 400

        # 채널 정보 추출 (아이콘 다운로드 포함)
        channel_info = metadata_extractor.extract_channel_info(channel_url)

        if not channel_info:
            if not metadata_extractor.yt_dlp_available:
                return jsonify({
                    'success': False,
                    'error': 'YouTube 채널 분석 기능을 사용하려면 yt-dlp 설치가 필요합니다.\n\n설치 명령어:\npip install yt-dlp'
                }), 503
            else:
                return jsonify({
                    'success': False,
                    'error': 'YouTube 채널 분석에 실패했습니다. 올바른 채널 URL인지 확인해주세요.'
                }), 400

        return jsonify({
            'success': True,
            'channel_info': channel_info
        })

    except Exception as e:
        print(f"❌ YouTube 채널 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'오류 발생: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    """
    YouTube URL 분석 API

    엔드포인트: POST /thumbnail-studio/api/analyze-url
    Body: {"url": "https://youtube.com/watch?v=..."}

    Returns:
        {
            "success": true,
            "metadata": {
                "title": str,
                "duration_string": str,
                "channel": str,
                "thumbnail_url": str
            }
        }
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL이 필요합니다.'
            }), 400

        # YouTube 메타데이터 추출
        metadata = metadata_extractor.extract(url)

        if not metadata:
            # yt-dlp가 설치되지 않았거나 URL이 잘못된 경우
            if not metadata_extractor.yt_dlp_available:
                return jsonify({
                    'success': False,
                    'error': 'YouTube URL 분석 기능을 사용하려면 yt-dlp 설치가 필요합니다.\n\n설치 명령어:\npip install yt-dlp\n\n또는 수동으로 제목과 영상 길이를 입력해주세요.'
                }), 503  # Service Unavailable
            else:
                return jsonify({
                    'success': False,
                    'error': 'YouTube URL 분석에 실패했습니다. 올바른 URL인지 확인해주세요.'
                }), 400

        return jsonify({
            'success': True,
            'metadata': metadata
        })

    except Exception as e:
        print(f"❌ YouTube URL 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'오류 발생: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/generate', methods=['POST'])
def generate():
    """
    썸네일 생성 API

    엔드포인트: POST /thumbnail-studio/api/generate
    기존 /api/generate와 다른 경로 → 충돌 없음

    FormData:
        - main_text: str (required)
        - subtitle_text: str (optional)
        - style: str (fire_english, minimalist, bold_bright, professional)
        - sentence_count: int (optional)
        - video_duration: str (optional, "3:42" format)
        - brand_color_primary: str (optional, hex)
        - brand_color_secondary: str (optional, hex)
        - brand_color_accent: str (optional, hex)
        - use_kelly: bool (optional, Kelly 캐릭터 사용 여부)
        - reference_image: file (optional)

    Returns:
        {
            "success": true,
            "session_id": str,
            "version": int,
            "thumbnail_url": str
        }
    """
    try:
        # FormData 파싱
        main_text = request.form.get('main_text', '').strip()
        subtitle_text = request.form.get('subtitle_text', '').strip()
        style = request.form.get('style', 'fire_english')  # 기본값: Fire English 스타일
        sentence_count = request.form.get('sentence_count', type=int)
        video_duration = request.form.get('video_duration', '').strip()
        text_position = request.form.get('text_position', 'center')  # left/center/right
        youtube_url = request.form.get('youtube_url', '').strip()  # NEW: YouTube URL
        channel_url = request.form.get('channel_url', '').strip()  # NEW: 채널 URL
        use_kelly = request.form.get('use_kelly', 'false').lower() == 'true'  # Kelly 캐릭터 사용 여부

        # 브랜드 색상
        brand_colors = None
        brand_primary = request.form.get('brand_color_primary', '').strip()
        brand_secondary = request.form.get('brand_color_secondary', '').strip()
        brand_accent = request.form.get('brand_color_accent', '').strip()

        if brand_primary or brand_secondary or brand_accent:
            brand_colors = {
                'primary': brand_primary or '#FF5733',
                'secondary': brand_secondary or '#3357FF',
                'accent': brand_accent or '#FFD700'
            }

        # 필수 필드 검증
        if not main_text:
            return jsonify({
                'success': False,
                'error': '메인 텍스트는 필수입니다.'
            }), 400

        # YouTube URL에서 3개의 프레임 추출 (동영상의 다른 장면)
        background_image_paths = []  # 3개 배경 이미지
        if youtube_url:
            try:
                # 1. 메타데이터 추출
                from src.youtube_thumbnail.metadata_extractor import YouTubeMetadataExtractor
                metadata_extractor = YouTubeMetadataExtractor()
                video_metadata = metadata_extractor.extract(youtube_url)

                if video_metadata:
                    print(f"✅ YouTube 메타데이터 추출: {video_metadata['title'][:50]}...")

                    # 영상 길이는 사용자가 입력한 경우만 사용 (자동 설정 제거)
                    # video_duration이 비어있으면 배지가 표시되지 않음

                # 2. 동영상에서 3개 프레임 추출 (다른 장면)
                from src.youtube_thumbnail.frame_extractor import VideoFrameExtractor
                frame_extractor = VideoFrameExtractor(output_dir=str(output_base / 'temp' / 'frames'))

                print(f"📹 동영상에서 3개 프레임 추출 중...")
                frame_paths = frame_extractor.extract_frames_from_url(youtube_url, count=3)

                if frame_paths and len(frame_paths) >= 3:
                    background_image_paths = frame_paths
                    print(f"✅ 3개 프레임 추출 완료:")
                    for i, path in enumerate(frame_paths, 1):
                        print(f"  {i}. {Path(path).name}")
                else:
                    # 폴백: 기본 썸네일 1개만 사용
                    print(f"⚠️ 프레임 추출 실패, 기본 썸네일 사용")
                    thumbnail_url = video_metadata.get('thumbnail_url', '')
                    if thumbnail_url:
                        import requests
                        response = requests.get(thumbnail_url, timeout=10)
                        response.raise_for_status()
                        temp_bg_path = output_base / 'temp' / f'youtube_thumbnail_{hash(youtube_url)}.jpg'
                        temp_bg_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(temp_bg_path, 'wb') as f:
                            f.write(response.content)
                        background_image_paths = [str(temp_bg_path)]  # 1개만

            except Exception as e:
                print(f"⚠️ YouTube 프레임 추출 실패: {e}")
                import traceback
                traceback.print_exc()

        # 채널 아이콘 다운로드
        channel_icon_path = None
        if channel_url:
            try:
                from src.youtube_thumbnail.metadata_extractor import YouTubeMetadataExtractor
                metadata_extractor = YouTubeMetadataExtractor()
                channel_info = metadata_extractor.extract_channel_info(channel_url)

                if channel_info and channel_info.get('icon_path'):
                    channel_icon_path = channel_info['icon_path']
                    print(f"✅ 채널 아이콘 로드: {channel_icon_path}")
            except Exception as e:
                print(f"⚠️ 채널 아이콘 추출 실패 (계속 진행): {e}")

        # 메인 텍스트를 YouTube CTR 최적화 제목으로 변환
        if api_key:
            try:
                title_optimizer = ThumbnailTitleOptimizer(api_key=api_key)
                optimized_title = title_optimizer.optimize_title(
                    original_title=main_text,
                    context=subtitle_text if subtitle_text else None
                )
                print(f"📝 제목 최적화: '{main_text}' → '{optimized_title}'")
                main_text = optimized_title  # 최적화된 제목 사용
            except Exception as e:
                print(f"⚠️ 제목 최적화 실패 (원본 사용): {e}")
                # 실패해도 원본 제목으로 계속 진행

        # 참고 이미지 처리 (GPT-4 Vision)
        reference_analysis = None
        if 'reference_image' in request.files:
            reference_file = request.files['reference_image']
            if reference_file.filename:
                # 임시 저장
                temp_image_path = output_base / 'temp' / reference_file.filename
                temp_image_path.parent.mkdir(parents=True, exist_ok=True)
                reference_file.save(str(temp_image_path))

                # GPT-4 Vision 분석
                if api_key:
                    try:
                        analyzer = StyleAnalyzer(api_key=api_key)
                        reference_analysis = analyzer.analyze_reference_image(str(temp_image_path))
                        print(f"✅ 참고 이미지 분석 완료: {reference_analysis}")
                    except Exception as e:
                        print(f"⚠ 참고 이미지 분석 실패 (계속 진행): {e}")

                # 임시 파일 삭제
                try:
                    temp_image_path.unlink()
                except:
                    pass

        # 세션 생성 또는 기존 세션 사용
        # 텍스트 수정 시: 기존 세션 ID가 있으면 재사용 (배경 이미지 보존)
        existing_session_id = request.form.get('session_id')

        if existing_session_id and history_manager.get_session_thumbnails(existing_session_id):
            # 기존 세션 재사용 (텍스트 수정 모드)
            session_id = existing_session_id
            print(f"📁 기존 세션 재사용: {session_id}")

            # 마지막 썸네일의 배경 이미지 및 채널 아이콘 경로 가져오기
            session_thumbnails = history_manager.get_session_thumbnails(session_id)
            if session_thumbnails:
                last_config = session_thumbnails[-1].get('config', {})

                # 배경 이미지 재사용
                if not background_image_paths:
                    last_bg_path = last_config.get('background_image_path')
                    if last_bg_path and Path(last_bg_path).exists():
                        background_image_paths = [last_bg_path]
                        print(f"✅ 이전 배경 이미지 재사용: {Path(last_bg_path).name}")

                # 채널 아이콘 재사용
                if not channel_icon_path:
                    last_icon_path = last_config.get('channel_icon_path')
                    if last_icon_path and Path(last_icon_path).exists():
                        channel_icon_path = last_icon_path
                        print(f"✅ 이전 채널 아이콘 재사용: {Path(last_icon_path).name}")
        else:
            # 새 세션 생성 (초기 생성)
            session_id = history_manager.create_session({
                'main_text': main_text,
                'subtitle_text': subtitle_text,
                'style': style,
                'reference_analysis': reference_analysis
            })
            print(f"📁 새 세션 생성: {session_id}")

        # Kelly 캐릭터 경로 (사용 설정 시)
        kelly_path = None
        if use_kelly:
            # 기존 Kelly 이미지 찾기
            kelly_candidates = [
                project_root / 'output' / 'resources' / 'images' / 'kelly_casual_hoodie.png',
                project_root / 'output' / 'resources' / 'images' / 'kelly_ponytail.png',
                project_root / 'output' / 'resources' / 'images' / 'kelly_glasses.png'
            ]
            for path in kelly_candidates:
                if path.exists():
                    kelly_path = str(path)
                    print(f"✅ Kelly 캐릭터 로드: {path.name}")
                    break

        # 썸네일 엔진 초기화
        thumbnail_engine = YouTubeThumbnailEngine(output_dir=str(output_base / session_id))

        # 스타일 설정 가져오기 (참고 이미지 분석 결과 병합)
        style_config = get_style(style)
        if reference_analysis:
            # 참고 이미지의 색상 팔레트 적용
            if 'color_palette' in reference_analysis:
                if not brand_colors:
                    brand_colors = {}
                palette = reference_analysis['color_palette']
                brand_colors['primary'] = palette.get('primary', brand_colors.get('primary'))
                brand_colors['secondary'] = palette.get('secondary', brand_colors.get('secondary'))
                brand_colors['accent'] = palette.get('accent', brand_colors.get('accent'))

        # 썸네일 생성 (3개의 배경 이미지로 각각 생성)
        print(f"🎨 TED 스타일 썸네일 생성 중...")
        print(f"  - 배경 이미지 개수: {len(background_image_paths)}")
        print(f"  - 채널 아이콘: {'있음' if channel_icon_path else '없음'}")
        print(f"  - 텍스트 위치: {text_position}")

        thumbnail_paths = []
        thumbnail_versions = []

        # 배경 이미지가 없으면 1개만 생성
        if not background_image_paths:
            background_image_paths = [None]

        # 각 배경 이미지로 썸네일 생성
        for i, bg_image_path in enumerate(background_image_paths, 1):
            print(f"\n  📸 썸네일 {i}/{len(background_image_paths)} 생성 중...")

            thumbnail_path = thumbnail_engine.create_thumbnail(
                main_text=main_text,
                subtitle_text=subtitle_text,
                style=style,
                sentence_count=sentence_count,
                video_duration=video_duration,
                background_image_path=bg_image_path,  # 각기 다른 배경
                channel_icon_path=channel_icon_path,  # 모든 썸네일에 동일
                text_position=text_position,
                brand_colors=brand_colors
            )

            print(f"    ✅ 생성 완료: {Path(thumbnail_path).name}")
            thumbnail_paths.append(thumbnail_path)

            # 히스토리에 각각 저장
            version = history_manager.save_thumbnail(
                session_id=session_id,
                thumbnail_path=thumbnail_path,
                config={
                    'main_text': main_text,
                    'subtitle_text': subtitle_text,
                    'style': style,
                    'sentence_count': sentence_count,
                    'video_duration': video_duration,
                    'brand_colors': brand_colors,
                    'background_image_path': bg_image_path,
                    'channel_icon_path': channel_icon_path,
                    'text_position': text_position,
                    'youtube_url': youtube_url,
                    'channel_url': channel_url,
                    'thumbnail_index': i  # 몇 번째 썸네일인지
                }
            )
            thumbnail_versions.append(version)

        print(f"\n✅ 총 {len(thumbnail_paths)}개 썸네일 생성 완료!")

        # 썸네일 URL 리스트 생성
        thumbnail_urls = [
            f'/thumbnail-studio/api/download/{session_id}/v{v}'
            for v in thumbnail_versions
        ]

        return jsonify({
            'success': True,
            'session_id': session_id,
            'versions': thumbnail_versions,  # [1, 2, 3]
            'thumbnail_urls': thumbnail_urls,  # 3개 URL
            'count': len(thumbnail_paths)
        })

    except Exception as e:
        print(f"❌ 썸네일 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'썸네일 생성 실패: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/regenerate', methods=['POST'])
def regenerate():
    """
    썸네일 재생성 API (3가지 변형)

    엔드포인트: POST /thumbnail-studio/api/regenerate
    Body: {
        "session_id": str,
        "current_version": int,
        "variation_type": "color" | "layout" | "complete"
    }

    Returns:
        {
            "success": true,
            "session_id": str,
            "version": int,
            "thumbnail_url": str
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', '').strip()
        current_version = data.get('current_version', 1)
        variation_type = data.get('variation_type', 'color')

        if not session_id:
            return jsonify({
                'success': False,
                'error': '세션 ID가 필요합니다.'
            }), 400

        # 현재 버전의 설정 로드
        current_config = history_manager.load_thumbnail_config(session_id, current_version)
        if not current_config:
            return jsonify({
                'success': False,
                'error': '버전을 찾을 수 없습니다.'
            }), 404

        # Variation Engine 초기화
        variation_engine = VariationEngine()

        # 변형 타입별 새 설정 생성
        print(f"🔄 재생성 시작: {variation_type}")

        if variation_type == 'color':
            new_config = variation_engine.regenerate_color_variation(current_config)
        elif variation_type == 'layout':
            new_config = variation_engine.regenerate_layout_variation(current_config)
        elif variation_type == 'complete':
            new_config = variation_engine.regenerate_complete_new(current_config)
        else:
            return jsonify({
                'success': False,
                'error': f'알 수 없는 변형 타입: {variation_type}'
            }), 400

        # 새 썸네일 생성
        thumbnail_engine = YouTubeThumbnailEngine(output_dir=str(output_base / session_id))

        thumbnail_path = thumbnail_engine.create_thumbnail(
            main_text=new_config.get('main_text', ''),
            subtitle_text=new_config.get('subtitle_text', ''),
            style=new_config.get('style', 'fire_english'),
            sentence_count=new_config.get('sentence_count'),
            video_duration=new_config.get('video_duration', ''),
            character_path=new_config.get('kelly_path'),
            brand_colors=new_config.get('brand_colors')
        )

        print(f"✅ 재생성 완료: {thumbnail_path}")

        # 히스토리에 추가
        new_config['variation_type'] = variation_type
        version = history_manager.save_thumbnail(
            session_id=session_id,
            thumbnail_path=thumbnail_path,
            config=new_config
        )

        # 썸네일 URL 생성
        thumbnail_url = f'/thumbnail-studio/api/download/{session_id}/v{version}'

        return jsonify({
            'success': True,
            'session_id': session_id,
            'version': version,
            'thumbnail_url': thumbnail_url
        })

    except Exception as e:
        print(f"❌ 재생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'재생성 실패: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id: str):
    """
    세션의 썸네일 히스토리 조회

    엔드포인트: GET /thumbnail-studio/api/history/<session_id>

    Returns:
        {
            "session_id": str,
            "created_at": str,
            "thumbnails": [
                {
                    "version": int,
                    "url": str,
                    "variation_type": str,
                    "created_at": str
                }
            ]
        }
    """
    try:
        session_thumbnails = history_manager.get_session_thumbnails(session_id)

        if not session_thumbnails:
            return jsonify({
                'success': False,
                'error': '세션을 찾을 수 없습니다.'
            }), 404

        # 썸네일 URL 변환
        thumbnails = []
        for thumb in session_thumbnails:
            thumbnails.append({
                'version': thumb['version'],
                'url': f'/thumbnail-studio/api/download/{session_id}/v{thumb["version"]}',
                'variation_type': thumb.get('variation_type', 'original'),
                'created_at': thumb.get('created_at', '')
            })

        return jsonify({
            'session_id': session_id,
            'thumbnails': thumbnails
        })

    except Exception as e:
        print(f"❌ 히스토리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'히스토리 조회 실패: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/download/<session_id>/v<int:version>', methods=['GET'])
def download_thumbnail(session_id: str, version: int):
    """
    특정 버전 썸네일 다운로드

    엔드포인트: GET /thumbnail-studio/api/download/<session_id>/v<version>
    """
    try:
        # 썸네일 경로 가져오기
        thumbnail_path_str = history_manager.get_thumbnail_path(session_id, version)

        if not thumbnail_path_str:
            return jsonify({
                'success': False,
                'error': f'버전 {version}을 찾을 수 없습니다.'
            }), 404

        thumbnail_path = Path(thumbnail_path_str)

        if not thumbnail_path.exists():
            return jsonify({
                'success': False,
                'error': '썸네일 파일을 찾을 수 없습니다.'
            }), 404

        # 파일 전송
        return send_file(
            str(thumbnail_path),
            mimetype='image/png',
            as_attachment=False,  # 브라우저에서 바로 표시
            download_name=f'thumbnail_{session_id}_v{version}.png'
        )

    except Exception as e:
        print(f"❌ 다운로드 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'다운로드 실패: {str(e)}'
        }), 500


@thumbnail_bp.route('/api/channel-profile', methods=['GET', 'POST'])
def channel_profile():
    """
    채널 프로필 저장/로드

    GET: 저장된 프로필 로드
    POST: 프로필 저장

    POST Body:
        {
            "channel_name": str,
            "brand_colors": {
                "primary": str,
                "secondary": str,
                "accent": str
            },
            "use_kelly": bool
        }
    """
    try:
        if request.method == 'GET':
            # 프로필 로드 (default 프로필)
            profile = channel_manager.load_profile('default')

            if not profile:
                # 기본 프로필 반환
                profile = {
                    'channel_name': 'Daily English Mecca',
                    'logo_path': None,
                    'brand_colors': {
                        'primary': '#FF5733',
                        'secondary': '#3357FF',
                        'accent': '#FFD700'
                    },
                    'use_kelly': True
                }

            return jsonify({
                'success': True,
                'profile': profile
            })

        else:  # POST
            data = request.get_json()

            profile_data = {
                'channel_name': data.get('channel_name', 'Daily English Mecca'),
                'brand_colors': data.get('brand_colors', {
                    'primary': '#FF5733',
                    'secondary': '#3357FF',
                    'accent': '#FFD700'
                }),
                'use_kelly': data.get('use_kelly', True)
            }

            # 프로필 저장
            profile_path = channel_manager.save_profile(profile_data, 'default')
            print(f"✅ 채널 프로필 저장: {profile_path}")

            return jsonify({
                'success': True,
                'message': '프로필이 저장되었습니다.',
                'profile_path': str(profile_path)
            })

    except Exception as e:
        print(f"❌ 채널 프로필 오류: {e}")
        return jsonify({
            'success': False,
            'error': f'채널 프로필 처리 실패: {str(e)}'
        }), 500
