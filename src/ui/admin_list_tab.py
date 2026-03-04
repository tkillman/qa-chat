"""관리자 Q&A 목록 조회 UI 컴포넌트

Gradio를 사용하여 관리자가 등록된 Q&A 항목을 페이징하여 조회할 수 있는 UI를 제공합니다.
"""

import gradio as gr
import logging
from typing import List, Tuple, Optional, Dict, Any

# 경로 설정
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qa_list_models import QAListItem, ListViewState
from services.qa_list_service import get_qa_list_service
from models.qa_delete_models import QADeleteRequest
from services.qa_delete_service import get_qa_delete_service

logger = logging.getLogger(__name__)


def _default_deletion_state() -> Dict[str, Any]:
    return {
        "show_dialog": False,
        "selected_qa_id": None,
        "selected_question_preview": None,
        "is_deleting": False,
    }


def _build_delete_choices(items: List[QAListItem]) -> List[Tuple[str, str]]:
    choices: List[Tuple[str, str]] = []
    for item in items:
        question_preview = item.question.strip().replace("\n", " ")
        if len(question_preview) > 30:
            question_preview = f"{question_preview[:30]}..."
        choices.append((f"{question_preview} ({item.id[:8]}...)", item.id))
    return choices


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
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; gap: 12px;">
                    <div style="display: flex; align-items: baseline; min-width: 0;">
                        <strong style="color: #2563eb; font-size: 14px; font-weight: 600; 
                                       text-transform: uppercase; letter-spacing: 0.5px;">
                            ❓ 질문
                        </strong>
                        <span style="color: #999; font-size: 12px; margin-left: 8px;">
                            ID: {item.id[:8]}...
                        </span>
                    </div>
                    <button type="button"
                            title="삭제"
                            style="border: 1px solid #fecaca; background: #fff1f2; color: #be123c;
                                   border-radius: 6px; padding: 6px 10px; font-size: 12px;
                                   font-weight: 600; cursor: pointer; white-space: nowrap;">
                        🗑️ 삭제
                    </button>
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
    delete_service = get_qa_delete_service()
    
    with gr.Tab("📋 목록 조회"):
        gr.Markdown("### 등록된 질문답변 목록")
        gr.Markdown("최신 등록순으로 정렬되며, 페이징을 통해 조회할 수 있습니다.")
        
        # 상태 관리
        current_page = gr.State(1)
        items_per_page = gr.State(10)
        deletion_state = gr.State(_default_deletion_state())
        
        # 컨트롤 영역
        with gr.Row():
            refresh_btn = gr.Button("🔄 새로고침", variant="secondary", scale=1)
            items_selector = gr.Dropdown(
                choices=[10, 20, 50],
                value=10,
                label="페이지당 항목 수",
                scale=2
            )

        with gr.Row():
            delete_target = gr.Dropdown(
                choices=[],
                value=None,
                label="삭제 대상 선택",
                scale=4,
                interactive=True,
            )
            delete_open_btn = gr.Button("🗑️ 삭제", variant="stop", scale=1)

        with gr.Group(visible=False) as delete_confirm_dialog:
            gr.Markdown("### 이 항목을 삭제하시겠습니까?")
            selected_qa_md = gr.Markdown(value="")
            with gr.Row():
                delete_confirm_yes = gr.Button("예", variant="stop")
                delete_confirm_no = gr.Button("아니오", variant="secondary")
        
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
        def load_list(page: int, per_page: int) -> Tuple[str, str, str, int, Any]:
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
                    return html, "페이지 1/1", "오류 발생", 1, gr.update(choices=[], value=None)
                
                if view_state.is_empty:
                    # 빈 목록
                    html = render_empty_message(view_state.get_display_message())
                    return html, "페이지 1/1", "총 0개의 항목", 1, gr.update(choices=[], value=None)
                
                # 정상 표시
                html, _ = render_qa_cards(view_state.items, visible=True)
                page_info_text = view_state.pagination.get_page_info_text()
                total_items_text = view_state.pagination.get_total_items_text()
                delete_choices = _build_delete_choices(view_state.items)
                
                return html, page_info_text, total_items_text, page, gr.update(choices=delete_choices, value=None)
                
            except Exception as e:
                logger.error(f"목록 로드 실패: {e}", exc_info=True)
                html = render_empty_message(f"목록 로드 중 오류 발생: {str(e)}")
                return html, "페이지 1/1", "오류 발생", 1, gr.update(choices=[], value=None)
        
        # 업데이트 함수들
        def refresh(per_page: int):
            """새로고침 버튼"""
            return load_list(1, per_page)
        
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
            per_page = int(new_per_page)
            html, page_text, total_text, page, delete_update = load_list(1, per_page)
            return html, page_text, total_text, page, delete_update, per_page

        def open_delete_dialog(selected_qa_id: Optional[str], state: Dict[str, Any]):
            """삭제 확인 다이얼로그 열기"""
            if not selected_qa_id:
                gr.Error("삭제할 항목을 선택해주세요")
                return gr.update(visible=False), gr.update(value=""), state

            next_state = {
                **state,
                "show_dialog": True,
                "selected_qa_id": selected_qa_id,
                "is_deleting": False,
            }
            return (
                gr.update(visible=True),
                gr.update(value=f"선택된 항목 ID: `{selected_qa_id}`"),
                next_state,
            )

        def cancel_delete_dialog(_state: Dict[str, Any]):
            """삭제 확인 다이얼로그 닫기"""
            return gr.update(visible=False), gr.update(value=""), _default_deletion_state()

        def confirm_delete(state: Dict[str, Any], page: int, per_page: int):
            """삭제 실행 후 목록 갱신"""
            selected_qa_id = state.get("selected_qa_id") if state else None
            if not selected_qa_id:
                gr.Error("삭제할 항목을 찾을 수 없습니다")
                html, page_text, total_text, current, delete_update = load_list(page, per_page)
                return (
                    html,
                    page_text,
                    total_text,
                    current,
                    delete_update,
                    gr.update(visible=False),
                    gr.update(value=""),
                    _default_deletion_state(),
                )

            gr.Info("삭제 중...")
            request = QADeleteRequest(qa_id=selected_qa_id, admin_user="admin")
            result = delete_service.delete_qa_item(request)

            if result.success:
                gr.Info("✓ 삭제되었습니다")
                refreshed_view = service.list_items(page=page, items_per_page=per_page)
                target_page = page
                if page > 1 and len(refreshed_view.items) == 0:
                    target_page = 1

                html, page_text, total_text, current, delete_update = load_list(target_page, per_page)
                return (
                    html,
                    page_text,
                    total_text,
                    current,
                    delete_update,
                    gr.update(visible=False),
                    gr.update(value=""),
                    _default_deletion_state(),
                )

            gr.Error(f"❌ 삭제 실패했습니다 - {result.message}")
            html, page_text, total_text, current, delete_update = load_list(page, per_page)
            failed_state = {
                **_default_deletion_state(),
                "show_dialog": True,
                "selected_qa_id": selected_qa_id,
            }
            return (
                html,
                page_text,
                total_text,
                current,
                delete_update,
                gr.update(visible=True),
                gr.update(value=f"선택된 항목 ID: `{selected_qa_id}`"),
                failed_state,
            )
        
        # 초기 로드
        initial_html, initial_page_info, initial_total, initial_page, initial_delete_choices = load_list(1, 10)
        qa_list_html.value = initial_html
        page_info.value = initial_page_info
        total_items_md.value = initial_total
        current_page.value = initial_page
        if isinstance(initial_delete_choices, dict):
            delete_target.choices = initial_delete_choices.get("choices", [])
            delete_target.value = initial_delete_choices.get("value")
        else:
            delete_target.choices = []
            delete_target.value = None
        
        # 이벤트 핸들러 등록
        refresh_btn.click(
            fn=refresh,
            inputs=[items_per_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page, delete_target]
        )
        
        next_btn.click(
            fn=go_next,
            inputs=[current_page, items_per_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page, delete_target]
        )
        
        prev_btn.click(
            fn=go_prev,
            inputs=[current_page, items_per_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page, delete_target]
        )
        
        items_selector.change(
            fn=change_items_per_page,
            inputs=items_selector,
            outputs=[qa_list_html, page_info, total_items_md, current_page, delete_target, items_per_page]
        )

        delete_open_btn.click(
            fn=open_delete_dialog,
            inputs=[delete_target, deletion_state],
            outputs=[delete_confirm_dialog, selected_qa_md, deletion_state],
        )

        delete_confirm_no.click(
            fn=cancel_delete_dialog,
            inputs=[deletion_state],
            outputs=[delete_confirm_dialog, selected_qa_md, deletion_state],
        )

        delete_confirm_yes.click(
            fn=confirm_delete,
            inputs=[deletion_state, current_page, items_per_page],
            outputs=[
                qa_list_html,
                page_info,
                total_items_md,
                current_page,
                delete_target,
                delete_confirm_dialog,
                selected_qa_md,
                deletion_state,
            ],
        )
        
        return qa_list_html, page_info, total_items_md, current_page, items_per_page
