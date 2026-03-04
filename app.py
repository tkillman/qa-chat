"""
QA Chat - Gradio 애플리케이션
Hugging Face Spaces 배포 엔트리포인트
"""
import os
import sys
import asyncio
import logging

# 프로젝트 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import QAChatApp

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수 - 앱 초기화 및 실행"""
    try:
        logger.info("QA Chat 애플리케이션 시작...")
        
        # 앱 초기화
        app = QAChatApp()
        
        # 비동기 초기화 수행 (데이터 로드)
        asyncio.run(app.on_startup())
        
        # Gradio 앱 실행
        logger.info("Gradio 인터페이스 시작...")
        app.launch(share=False)
        
    except Exception as e:
        logger.error(f"애플리케이션 시작 오류: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
