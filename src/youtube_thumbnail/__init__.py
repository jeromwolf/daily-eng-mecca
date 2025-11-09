"""
YouTube 썸네일 생성기 - 독립 모듈

기존 비디오 생성 시스템과 완전히 분리됨.
사이드 이펙트 없음을 보장.

Author: Kelly & Claude Code
Date: 2025-11-09
Version: 1.0.0
"""

from .metadata_extractor import YouTubeMetadataExtractor
from .channel_profile import ChannelProfile
from .thumbnail_engine import YouTubeThumbnailEngine
from .history_manager import ThumbnailHistory
from .style_analyzer import StyleAnalyzer
from .variation_engine import VariationEngine
from .styles import THUMBNAIL_STYLES, get_style, list_styles

__all__ = [
    'YouTubeMetadataExtractor',
    'ChannelProfile',
    'YouTubeThumbnailEngine',
    'ThumbnailHistory',
    'StyleAnalyzer',
    'VariationEngine',
    'THUMBNAIL_STYLES',
    'get_style',
    'list_styles'
]

__version__ = '1.0.0'
