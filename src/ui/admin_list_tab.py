"""관리자 Q&A 목록 조회 UI 컴포넌트

Gradio를 사용하여 관리자가 등록된 Q&A 항목을 페이징하여 조회할 수 있는 UI를 제공합니다.
"""

import gradio as gr
import logging
import json
import html as html_module
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field, asdict

# 경로 설정
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qa_list_models import QAListItem, ListViewState
from services.qa_list_service import get_qa_list_service
from models.qa_delete_models import QADeleteRequest
from services.qa_delete_service import get_qa_delete_service

logger = logging.getLogger(__name__)


@dataclass
class DeletionState:
    """Q&A 항목 삭제 모달 대화 상태 (Phase 2: Foundational - T009)
    
    Gradio State 컴포넌트에서 추적되는 삭제 UI 상태 관리
    
    속성:
        show_dialog: 확인 모달 표시 여부
        selected_qa_id: 선택된 Q&A 항목 ID
        selected_question_preview: 삭제될 항목의 질문 미리보기
        is_deleting: 삭제 작업 진행 중 여부
    
    상태 변환 (data-model.md 상태 다이어그램):
        초기화 → open_dialog() → 모달표시 → confirm_delete() → 삭제중
                             ↓ cancel()
                             초기화
    """
    show_dialog: bool = False
    selected_qa_id: Optional[str] = None
    selected_question_preview: Optional[str] = None
    is_deleting: bool = False
    
    def open_dialog(self, qa_id: str, question_preview: str) -> None:
        """삭제 확인 모달 열기
        
        Args:
            qa_id: 삭제할 Q&A 항목 ID
            question_preview: 삭제될 항목의 질문 (UI 표시용)
        """
        self.show_dialog = True
        self.selected_qa_id = qa_id
        self.selected_question_preview = question_preview
        self.is_deleting = False
    
    def mark_deleting(self) -> None:
        """삭제 작업 시작 표시 (UI 로딩 상태)"""
        self.is_deleting = True
    
    def reset(self) -> None:
        """상태 초기화 (모달 닫기)"""
        self.show_dialog = False
        self.selected_qa_id = None
        self.selected_question_preview = None
        self.is_deleting = False
    
    def to_dict(self) -> Dict[str, Any]:
        """상태를 딕셔너리로 변환 (Gradio State 호환)
        
        Returns:
            상태 딕셔너리
        """
        return asdict(self)


def _default_deletion_state() -> Dict[str, Any]:
    """기본 삭제 상태 생성 (레거시 호환성, DeletionState.to_dict() 래퍼)
    
    Returns:
        기본 삭제 상태 딕셔너리
    """
    return DeletionState().to_dict()


def _normalize_deletion_state(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """삭제 상태를 안전한 딕셔너리로 정규화"""
    if not state:
        return _default_deletion_state()
    return {
        **_default_deletion_state(),
        **state,
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
    """QA 항목들을 테이블 형식 HTML로 렌더링
    
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
    
    # 테이블 시작
    html = '''
    <div style="overflow-x: auto; max-height: 700px; overflow-y: auto;">
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <thead style="background: #f0f4f8; position: sticky; top: 0; z-index: 10;">
            <tr>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #d0d0d0; font-weight: 600; color: #2c3e50; width: 40%;">
                    ❓ 질문
                </th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #d0d0d0; font-weight: 600; color: #2c3e50; width: 45%;">
                    ✅ 답변
                </th>
                <th style="padding: 12px; text-align: center; border-bottom: 2px solid #d0d0d0; font-weight: 600; color: #2c3e50; width: 15%;">
                    작업
                </th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for idx, item in enumerate(items):
        qa_id_js = json.dumps(item.id)
        # 단순화: 숨겨진 텍스트박스 값 변경만 수행 (Gradio가 change 이벤트 감지)
        onclick_js = (
            "try{"
            f"const qaId={qa_id_js};"
            "let hiddenInput=document.getElementById('hidden-qa-id');"
            "if(hiddenInput){"
            "const inputEl=(hiddenInput.matches&&hiddenInput.matches('input,textarea'))?hiddenInput:hiddenInput.querySelector('input,textarea');"
            "if(inputEl){"
            "inputEl.value=qaId;"
            "inputEl.dispatchEvent(new Event('input',{bubbles:true,composed:true}));"
            "inputEl.dispatchEvent(new Event('change',{bubbles:true,composed:true}));"
            "}"
            "}"
            "}catch(e){console.error('delete button error:',e);}"
        )
        onclick_attr = html_module.escape(onclick_js, quote=True)

        # HTML 이스케이프 처리
        question_html = item.question.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        answer_html = item.answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 한 줄로 표시되도록 길이 제한
        question_preview = question_html[:100] + '...' if len(question_html) > 100 else question_html
        answer_preview = answer_html[:150] + '...' if len(answer_html) > 150 else answer_html
        
        # 짝수/홀수 행 배경색
        row_bg = '#ffffff' if idx % 2 == 0 else '#f9fafb'
        
        row = f'''
            <tr style="background: {row_bg}; border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 12px; vertical-align: top; max-width: 0; word-break: break-word; font-family: monospace; color: #333;">
                    {question_preview}
                    <div style="font-size: 11px; color: #999; margin-top: 4px;">ID: {item.id[:12]}...</div>
                </td>
                <td style="padding: 12px; vertical-align: top; max-width: 0; word-break: break-word; font-family: monospace; color: #333;">
                    {answer_preview}
                </td>
                <td style="padding: 12px; text-align: center; vertical-align: middle; white-space: nowrap;">
                    <button type="button" 
                            onclick="{onclick_attr}"
                            title="삭제"
                            style="border: 1px solid #fecaca; background: #fff1f2; color: #be123c;
                                   border-radius: 4px; padding: 6px 10px; font-size: 12px;
                                   font-weight: 600; cursor: pointer; transition: all 0.2s;
                                   hover: background: #fee2e2;">
                        🗑️ 삭제
                    </button>
                </td>
            </tr>
        '''
        html += row
    
    html += '''
        </tbody>
    </table>
    </div>
    '''
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
        # 숨겨진 브리지용 스타일 정의
        gr.HTML('''
        <style>
        .delete-hidden-bridge {
            position: absolute !important;
            left: -9999px !important;
            top: 0 !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            overflow: hidden !important;
        }
        </style>
        ''')
        
        with gr.Column(elem_classes="tab-content-padding"):
            gr.Markdown("### 등록된 질문답변 목록")
            gr.Markdown("최신 등록순으로 정렬되며, 페이징을 통해 조회할 수 있습니다.")
            
            # 상태 관리
            current_page = gr.State(1)
            items_per_page = gr.State(10)
            deletion_state = gr.State(_default_deletion_state())
            
            # 숨겨진 브리지 컴포넌트 (JavaScript에서 사용)
            # visible=False 대신 CSS 숨김을 사용해 DOM에서 항상 조회 가능하도록 유지
            hidden_qa_id = gr.Textbox(
                visible=True,
                elem_id="hidden-qa-id",
                elem_classes=["delete-hidden-bridge"],
                container=False,
                label=""
            )
            hidden_open_delete_trigger = gr.Button(
                value="open-delete-trigger",
                visible=True,
                elem_id="hidden-open-delete-trigger",
                elem_classes=["delete-hidden-bridge"],
            )
            
            # 새로고침 버튼 (우측 정렬)
            with gr.Row(elem_classes="control-row-right"):
                gr.Markdown("")  # 왼쪽 공간 채우기
                refresh_btn = gr.Button("🔄 새로고침", variant="secondary", scale=0)

            # 삭제 확인 다이얼로그
            with gr.Group(visible=False) as delete_confirm_dialog:
                gr.Markdown("### 이 항목을 삭제하시겠습니까?")
                selected_qa_md = gr.Markdown(value="")
                with gr.Row():
                    delete_confirm_yes = gr.Button("예", variant="stop")
                    delete_confirm_no = gr.Button("아니오", variant="secondary")
            
            # 초기 로드 함수 (컴포넌트 생성 전에 정의)
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
            
            # 초기 데이터 로드
            initial_html, initial_page_info, initial_total, initial_page = load_list(1, 10)
            
            # 목록 표시 영역 (초기값 포함)
            qa_list_html = gr.HTML(value=initial_html)
            
            # 페이징 정보 및 컨트롤
            with gr.Row():
                prev_btn = gr.Button("◀ 이전", scale=1, variant="secondary")
                with gr.Column(scale=2, min_width=0):
                    page_info = gr.Markdown(initial_page_info, elem_classes="page-info-center")
                next_btn = gr.Button("다음 ▶", scale=1, variant="secondary")
            
            # 전체 항목 수 표시
            total_items_md = gr.Markdown(initial_total)

        
        def open_delete_dialog(qa_id: str, state: Dict[str, Any]):
            """삭제 확인 다이얼로그 열기 (카드 버튼에서 호출)"""
            state = _normalize_deletion_state(state)
            if not qa_id or not qa_id.strip():
                gr.Error("삭제할 항목을 선택해주세요")
                return gr.update(visible=False), gr.update(value=""), state

            next_state = {
                **state,
                "show_dialog": True,
                "selected_qa_id": qa_id,
                "is_deleting": False,
            }
            return (
                gr.update(visible=True),
                gr.update(value=f"선택된 항목 ID: `{qa_id}`"),
                next_state,
            )

        def cancel_delete_dialog(_state: Dict[str, Any]):
            """삭제 확인 다이얼로그 닫기"""
            return gr.update(visible=False), gr.update(value=""), _default_deletion_state()

        def confirm_delete(state: Dict[str, Any], page: int):
            """삭제 실행 후 목록 갱신 (10개 고정)"""
            selected_qa_id = state.get("selected_qa_id") if state else None
            if not selected_qa_id:
                gr.Error("삭제할 항목을 찾을 수 없습니다")
                html, page_text, total_text, current = load_list(page, 10)
                return (
                    html,
                    page_text,
                    total_text,
                    current,
                    gr.update(visible=False),
                    gr.update(value=""),
                    _default_deletion_state(),
                )

            gr.Info("삭제 중...")
            request = QADeleteRequest(qa_id=selected_qa_id, admin_user="admin")
            result = delete_service.delete_qa_item(request)

            if result.success:
                gr.Info("✓ 삭제되었습니다")
                refreshed_view = service.list_items(page=page, items_per_page=10)
                target_page = page
                if page > 1 and len(refreshed_view.items) == 0:
                    target_page = 1

                html, page_text, total_text, current = load_list(target_page, 10)
                return (
                    html,
                    page_text,
                    total_text,
                    current,
                    gr.update(visible=False),
                    gr.update(value=""),
                    _default_deletion_state(),
                )

            gr.Error(f"❌ 삭제 실패했습니다 - {result.message}")
            html, page_text, total_text, current = load_list(page, 10)
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
                gr.update(visible=True),
                gr.update(value=f"선택된 항목 ID: `{selected_qa_id}`"),
                failed_state,
            )
        
        # 상태 초기값 설정
        items_per_page.value = 10
        current_page.value = 1
        
        # 탭 활성 시 새로고침
        def on_tab_select():
            """탭 활성화 시 목록 새로고침"""
            return load_list(1, 10)
        
        # 이벤트 핸들러 등록
        # refresh_btn.click (10개 고정)
        def refresh_fixed():
            return load_list(1, 10)
        
        refresh_btn.click(
            fn=refresh_fixed,
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        # go_next (10개 고정)
        def go_next_fixed(page: int):
            next_page = page + 1
            return load_list(next_page, 10)
        
        next_btn.click(
            fn=go_next_fixed,
            inputs=[current_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        # go_prev (10개 고정)
        def go_prev_fixed(page: int):
            prev_page = max(1, page - 1)
            return load_list(prev_page, 10)
        
        prev_btn.click(
            fn=go_prev_fixed,
            inputs=[current_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )

        # 숨겨진 텍스트박스의 change 이벤트에 확인 다이얼로그 열기 연결
        # (HTML 버튼의 onclick에서 hidden_qa_id 값 변경 → Gradio가 자동 감지)
        hidden_qa_id.change(
            fn=open_delete_dialog,
            inputs=[hidden_qa_id, deletion_state],
            outputs=[delete_confirm_dialog, selected_qa_md, deletion_state],
        )

        delete_confirm_no.click(
            fn=cancel_delete_dialog,
            inputs=[deletion_state],
            outputs=[delete_confirm_dialog, selected_qa_md, deletion_state],
        )

        delete_confirm_yes.click(
            fn=confirm_delete,
            inputs=[deletion_state, current_page],
            outputs=[
                qa_list_html,
                page_info,
                total_items_md,
                current_page,
                delete_confirm_dialog,
                selected_qa_md,
                deletion_state,
            ],
        )
        
        return qa_list_html, page_info, total_items_md, current_page, on_tab_select
