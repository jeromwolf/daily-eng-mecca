"""
OpenAI DALL-E를 사용한 이미지 생성 모듈
"""
import os
from openai import OpenAI
from pathlib import Path
from .resource_manager import ResourceManager


class ImageGenerator:
    def __init__(self, api_key: str = None, use_cache: bool = True, resource_manager=None):
        """
        ImageGenerator 초기화

        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
            use_cache: 리소스 캐싱 사용 여부
            resource_manager: ResourceManager 인스턴스 (선택사항, 없으면 자동 생성)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.use_cache = use_cache
        self.resource_manager = resource_manager if resource_manager else (ResourceManager() if use_cache else None)

    def generate_image(self, prompt: str, output_path: str, size: str = "1024x1792") -> str:
        """
        텍스트 프롬프트로 이미지 생성 (캐싱 지원)

        Args:
            prompt: 이미지 생성을 위한 프롬프트
            output_path: 이미지 저장 경로
            size: 이미지 크기 (유튜브 쇼츠용 세로 형식: 1024x1792)

        Returns:
            생성된 이미지 파일 경로
        """
        try:
            # 캐싱 사용 시, 이미 존재하는지 확인
            if self.use_cache and self.resource_manager:
                cached_path = self.resource_manager.get_image_path(prompt)
                if self.resource_manager.image_exists(prompt):
                    print(f"✓ 캐시된 이미지 사용: {prompt[:50]}...")
                    # 캐시된 이미지를 output_path로 복사
                    import shutil
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(cached_path, output_path)
                    return output_path

            print(f"이미지 생성 중: {prompt[:50]}...")

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # 이미지 다운로드 및 저장
            import requests
            from PIL import Image
            import io

            image_data = requests.get(image_url).content

            # PIL로 이미지 로드하여 회전 필요 여부 확인
            img = Image.open(io.BytesIO(image_data))
            print(f"📸 원본 이미지 크기: {img.size} (width x height)")

            # 가로 방향이면 90도 회전
            if img.width > img.height:
                print(f"⚠ 이미지가 가로 방향입니다. 90도 회전합니다.")
                img = img.rotate(-90, expand=True)
                print(f"✓ 회전 후 크기: {img.size}")

                # 회전된 이미지를 바이트로 변환
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_data = buffer.getvalue()

            # output_path에 저장
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_data)

            # 캐싱 사용 시, 리소스 폴더에도 저장
            if self.use_cache and self.resource_manager:
                cached_path = self.resource_manager.get_image_path(prompt)
                with open(cached_path, 'wb') as f:
                    f.write(image_data)

            print(f"✓ 이미지 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ 이미지 생성 실패: {e}")
            raise

    def generate_images_for_sentences(self, sentences: list[str], output_dir: str) -> list[str]:
        """
        여러 문장에 대한 이미지들을 생성

        Args:
            sentences: 영어 문장 리스트
            output_dir: 이미지 저장 디렉토리

        Returns:
            생성된 이미지 파일 경로 리스트
        """
        image_paths = []

        for idx, sentence in enumerate(sentences):
            # 문장을 이미지 생성 프롬프트로 변환
            prompt = self._create_image_prompt(sentence)
            output_path = os.path.join(output_dir, f"image_{idx+1}.png")

            image_path = self.generate_image(prompt, output_path)
            image_paths.append(image_path)

        return image_paths

    def _create_image_prompt(self, sentence: str) -> str:
        """
        영어 문장을 이미지 생성 프롬프트로 변환

        Args:
            sentence: 영어 문장

        Returns:
            DALL-E용 이미지 프롬프트
        """
        # 간단하고 시각적인 일러스트 스타일로 생성
        prompt = f"""Create a simple, clean, and visually appealing illustration that represents: "{sentence}"

        Style: Minimalist, modern, flat design with soft colors
        Mood: Friendly and educational
        Background: Clean and simple
        Aspect: Vertical format suitable for mobile viewing
        """
        return prompt
