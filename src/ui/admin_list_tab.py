"""관리자 Q&A 목록 조회 UI 컴포넌트

Gradio를 사용하여 관리자가 등록된 Q&A 항목을 페이징하여 조회할 수 있는 UI를 제공합니다.
"""

import gradio as gr
import logging
from typing import List, Tuple, Optional

# 경로 설정
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qa_list_models import QAListItem, ListViewState
from services.qa_list_service import get_qa_list_service

logger = logging.getLogger(__name__)


def render_qa_cards(items: List[QAListItem], visible: bool = True) -> Tuple[str, bool]:
    """QA 항목들을 카드 형식 HTML로 렌더링
    
    Args:
        items: QAListItem 리스트
        visible: 컴포넌트 표시 여부
        
    Returns:
        (HTML 문자열, 표시 여부)
    """
    if not items:
        html = '''
        <div style="text-align: center; padding: 60px 20px; color: #999; font-size: 16px;">
            <div style="font-size: 48px; margin-bottom: 20px;">📭</div>
            등록된 질문답변이 없습니다
        </div>
        '''
        return html, False
    
    # 카드 HTML 생성
    html = '<div style="display: flex; flex-direction: column; gap: 16px; max-height: 600px; overflow-y: auto; padding-right: 10px;">'
    
    for item in items:
        # HTML 이스케이프 처리
        question_html = item.question.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        answer_html = item.answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        card = f'''
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; 
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    transition: box-shadow 0.3s ease;">
            
            <div style="margin-bottom: 14px;">
                <div style="display: flex; align-items: baseline; margin-bottom: 8px;">
                    <strong style="color: #2563eb; font-size: 14px; font-weight: 600; 
                                   text-transform: uppercase; letter-spacing: 0.5px;">
                        ❓ 질문
                    </strong>
                    <span style="color: #999; font-size: 12px; margin-left: 8px;">
                        ID: {item.id[:8]}...
                    </span>
                </div>
                <div style="max-height: 120px; overflow-y: auto; margin-top: 8px;
                            padding: 10px; background: white; border-radius: 4px;
                            border-left: 3px solid #2563eb; font-family: monospace;
                            font-size: 13px; line-height: 1.5; color: #333;">
                    {question_html}
                </div>
            </div>
            
            <div>
                <div style="display: flex; align-items: baseline; margin-bottom: 8px;">
                    <strong style="color: #059669; font-size: 14px; font-weight: 600;
                                   text-transform: uppercase; letter-spacing: 0.5px;">
                        ✅ 답변
                    </strong>
                    <span style="color: #999; font-size: 12px; margin-left: 8px;">
                        {item.created_at[:10]}
                    </span>
                </div>
                <div style="max-height: 180px; overflow-y: auto; margin-top: 8px;
                            padding: 10px; background: white; border-radius: 4px;
                            border-left: 3px solid #059669; font-family: monospace;
                            font-size: 13px; line-height: 1.6; color: #333;">
                    {answer_html}
                </div>
            </div>
        </div>
        '''
        html += card
    
    html += '</div>'
    return html, True


def render_empty_message(message: str) -> str:
    """빈 목록 또는 오류 메시지 렌더링
    
    Args:
        message: 표시할 메시지
        
    Returns:
        HTML 문자열
    """
    return f'''
    <div style="text-align: center; padding: 60px 20px; color: #666; font-size: 16px;">
        <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
        {message}
    </div>
    '''


def create_admin_list_tab():
    """관리자 목록 조회 탭 생성
    
    Returns:
        탭 컴포넌트들의 참조 (테스트용)
    """
    service = get_qa_list_service()
    
    with gr.Tab("📋 목록 조회"):
        gr.Markdown("### 등록된 질문답변 목록")
        gr.Markdown("최신 등록순으로 정렬되며, 페이징을 통해 조회할 수 있습니다.")
        
        # 상태 관리
        current_page = gr.State(1)
        items_per_page = gr.State(10)
        
        # 컨트롤 영역
        with gr.Row():
            refresh_btn = gr.Button("🔄 새로고침", variant="secondary", scale=1)
            items_selector = gr.Dropdown(
                choices=[10, 20, 50],
                value=10,
                label="페이지당 항목 수",
                scale=2
            )
        
        # 목록 표시 영역
        qa_list_html = gr.HTML(
            value="<div style='text-align: center; padding: 40px; color: #999;'>로딩 중...</div>"
        )
        
        # 페이징 정보 및 컨트롤
        with gr.Row():
            prev_btn = gr.Button("◀ 이전", scale=1, variant="secondary")
            with gr.Column(scale=2):
                page_info = gr.Markdown("페이지 1/1")
            next_btn = gr.Button("다음 ▶", scale=1, variant="secondary")
        
        # 전체 항목 수 표시
        total_items_md = gr.Markdown("총 0개의 항목")
        
        # 초기 로드 함수
        def load_list(page: int, per_page: int) -> Tuple[str, str, str, int]:
            """목록 로드 함수
            
            Args:
                page: 페이지 번호
                per_page: 페이지당 항목 수
                
            Returns:
                (카드 HTML, 페이지 정보, 총 항목 수 텍스트, 현재 페이지)
            """
            try:
                view_state = service.list_items(page=page, items_per_page=per_page)
                
                if view_state.has_error():
                    # 오류 상태
                    html = render_empty_message(view_state.get_display_message())
                    return html, "페이지 1/1", "오류 발생", 1
                
                if view_state.is_empty:
                    # 빈 목록
                    html = render_empty_message(view_state.get_display_message())
                    return html, "페이지 1/1", "총 0개의 항목", 1
                
                # 정상 표시
                html, _ = render_qa_cards(view_state.items, visible=True)
                page_info_text = view_state.pagination.get_page_info_text()
                total_items_text = view_state.pagination.get_total_items_text()
                
                return html, page_info_text, total_items_text, page
                
            except Exception as e:
                logger.error(f"목록 로드 실패: {e}", exc_info=True)
                html = render_empty_message(f"목록 로드 중 오류 발생: {str(e)}")
                return html, "페이지 1/1", "오류 발생", 1
        
        # 업데이트 함수들
        def refresh():
            """새로고침 버튼"""
            return load_list(1, 10)
        
        def go_next(page: int, per_page: int):
            """다음 페이지"""
            next_page = page + 1
            return load_list(next_page, per_page)
        
        def go_prev(page: int, per_page: int):
            """이전 페이지"""
            prev_page = max(1, page - 1)
            return load_list(prev_page, per_page)
        
        def change_items_per_page(new_per_page: int):
            """페이지당 항목 수 변경"""
            return load_list(1, new_per_page)
        
        # 초기 로드
        initial_html, initial_page_info, initial_total, initial_page = load_list(1, 10)
        qa_list_html.value = initial_html
        page_info.value = initial_page_info
        total_items_md.value = initial_total
        current_page.value = initial_page
        
        # 이벤트 핸들러 등록
        refresh_btn.click(
            fn=refresh,
            inputs=None,
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        next_btn.click(
            fn=go_next,
            inputs=[current_page, items_per_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        prev_btn.click(
            fn=go_prev,
            inputs=[current_page, items_per_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        items_selector.change(
            fn=change_items_per_page,
            inputs=items_selector,
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        ).then(
            lambda: 10,  # 드롭다운 값 저장 후 items_per_page 업데이트
            outputs=items_per_page
        )
        
        return qa_list_html, page_info, total_items_md, current_page, items_per_page
