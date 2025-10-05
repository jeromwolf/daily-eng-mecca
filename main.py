#!/usr/bin/env python3
"""
Daily English Mecca - 유튜브 쇼츠 자동 생성 프로그램
하루 3문장 영어 학습 콘텐츠를 자동으로 제작합니다.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from src.content_analyzer import ContentAnalyzer
from src.image_generator import ImageGenerator
from src.tts_generator import TTSGenerator
from src.video_creator import VideoCreator
from src.youtube_metadata import YouTubeMetadataGenerator


def print_banner():
    """프로그램 배너 출력"""
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║   Daily English Mecca                         ║
    ║   매일 3문장 영어 학습 쇼츠 자동 생성기      ║
    ╚═══════════════════════════════════════════════╝
    """
    print(banner)


def get_sentences_from_user() -> list[str]:
    """
    사용자로부터 3개의 영어 문장 입력받기

    Returns:
        영어 문장 리스트
    """
    print("\n📝 오늘의 3문장을 입력해주세요:\n")

    sentences = []
    for i in range(3):
        while True:
            sentence = input(f"문장 {i+1}: ").strip()
            if sentence:
                sentences.append(sentence)
                break
            else:
                print("❌ 문장을 입력해주세요.")

    print("\n✅ 입력된 문장:")
    for i, s in enumerate(sentences):
        print(f"  {i+1}. {s}")

    return sentences


def main():
    """메인 실행 함수"""
    # 환경변수 로드
    load_dotenv()

    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일을 생성하고 API 키를 입력해주세요.")
        print("   예시: OPENAI_API_KEY=your_api_key_here\n")
        sys.exit(1)

    # 배너 출력
    print_banner()

    # 문장 입력 받기
    sentences = get_sentences_from_user()

    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 출력 디렉토리 설정
    output_dir = Path("output")
    images_dir = output_dir / "images" / timestamp
    audio_dir = output_dir / "audio" / timestamp
    videos_dir = output_dir / "videos"
    metadata_dir = output_dir / "metadata"

    # 디렉토리 생성
    for dir_path in [images_dir, audio_dir, videos_dir, metadata_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    try:
        # 1. 콘텐츠 분석
        print("\n" + "="*50)
        print("1️⃣  문장 분석 중...")
        print("="*50)

        analyzer = ContentAnalyzer(api_key=api_key)
        analysis = analyzer.analyze_sentences(sentences)

        print(f"\n📊 분석 결과:")
        print(f"   - 생성할 이미지 개수: {analysis['num_images']}개")
        print(f"   - 이미지 그룹: {analysis['image_groups']}")

        # 2. 이미지 생성
        print("\n" + "="*50)
        print("2️⃣  이미지 생성 중...")
        print("="*50)

        image_gen = ImageGenerator(api_key=api_key)
        image_paths = []

        for idx, prompt in enumerate(analysis['prompts']):
            img_path = images_dir / f"image_{idx+1}.png"
            image_path = image_gen.generate_image(
                prompt=prompt,
                output_path=str(img_path)
            )
            image_paths.append(image_path)

        # 3. 음성 생성
        print("\n" + "="*50)
        print("3️⃣  음성 생성 중...")
        print("="*50)

        tts_gen = TTSGenerator(api_key=api_key)
        audio_path = audio_dir / "speech.mp3"

        tts_gen.generate_speech_for_sentences(
            sentences=sentences,
            output_path=str(audio_path),
            voice="nova",
            add_pauses=True
        )

        audio_duration = tts_gen.get_audio_duration(str(audio_path))
        print(f"   - 음성 길이: {audio_duration:.1f}초")

        # 4. 비디오 생성
        print("\n" + "="*50)
        print("4️⃣  비디오 생성 중...")
        print("="*50)

        video_creator = VideoCreator()
        video_path = videos_dir / f"daily_english_{timestamp}.mp4"

        video_creator.create_video(
            sentences=sentences,
            image_paths=image_paths,
            audio_path=str(audio_path),
            output_path=str(video_path),
            image_groups=analysis['image_groups']
        )

        # 5. 유튜브 메타정보 생성
        print("\n" + "="*50)
        print("5️⃣  유튜브 메타정보 생성 중...")
        print("="*50)

        metadata_gen = YouTubeMetadataGenerator(api_key=api_key)
        metadata = metadata_gen.generate_metadata(sentences)

        # 메타정보 저장
        metadata_path = metadata_dir / f"metadata_{timestamp}.json"
        metadata_gen.save_metadata(metadata, str(metadata_path))

        # 메타정보 출력
        metadata_gen.print_metadata(metadata)

        # 완료 메시지
        print("\n" + "="*50)
        print("✨ 모든 작업이 완료되었습니다!")
        print("="*50)
        print(f"\n📁 생성된 파일:")
        print(f"   🎥 비디오: {video_path}")
        print(f"   📋 메타정보: {metadata_path}")
        print(f"   🖼️  이미지: {images_dir}")
        print(f"   🔊 음성: {audio_path}")

        print(f"\n🚀 다음 단계:")
        print(f"   1. 비디오 파일을 확인하세요: {video_path}")
        print(f"   2. 유튜브에 업로드하고 메타정보를 참고하여 제목/설명/태그를 입력하세요")
        print(f"   3. 구독자 증가를 기대해보세요! 📈\n")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
