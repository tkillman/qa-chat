"""관리자 Q&A 목록 조회 UI 컴포넌트

Gradio를 사용하여 관리자가 등록된 Q&A 항목을 페이징하여 조회할 수 있는 UI를 제공합니다.
"""

import gradio as gr
import logging
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
    html = '''
    <div style="display: flex; flex-direction: column; gap: 16px; max-height: 600px; overflow-y: auto; padding-right: 10px;">
    '''
    
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
                            onclick="deleteQA('{item.id}')"
                            title="삭제"
                            style="border: 1px solid #fecaca; background: #fff1f2; color: #be123c;
                                   border-radius: 6px; padding: 6px 10px; font-size: 12px;
                                   font-weight: 600; white-space: nowrap; cursor: pointer;
                                   transition: all 0.2s;">
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
        # 글로벌 deleteQA 함수 정의 (한 번만 로드)
        gr.HTML('''
        <script>
        (function() {
            // 전역 deleteQA 함수 정의
            window.deleteQA = function(qaId) {
                try {
                    console.log('deleteQA called with:', qaId);
                    
                    // 전체 문서에서 숨겨진 입력 필드 찾기
                    let hiddenInput = null;
                    
                    // 방법 1: ID로 직접 검색
                    hiddenInput = document.querySelector('#hidden-qa-id textarea') || 
                                 document.querySelector('#hidden-qa-id input');
                    
                    // 방법 2: 부분 매칭
                    if (!hiddenInput) {
                        const candidates = document.querySelectorAll('[id*="hidden-qa-id"]');
                        for (let elem of candidates) {
                            let input = elem.querySelector('textarea') || elem.querySelector('input');
                            if (input) {
                                hiddenInput = input;
                                break;
                            }
                        }
                    }
                    
                    // 방법 3: 전체 검색
                    if (!hiddenInput) {
                        const allTextareas = document.querySelectorAll('textarea');
                        const allInputs = document.querySelectorAll('input[type="text"]');
                        for (let elem of allTextareas) {
                            if (elem.id && elem.id.includes('hidden-qa-id')) {
                                hiddenInput = elem;
                                break;
                            }
                        }
                        if (!hiddenInput) {
                            for (let elem of allInputs) {
                                if (elem.id && elem.id.includes('hidden-qa-id')) {
                                    hiddenInput = elem;
                                    break;
                                }
                            }
                        }
                    }
                    
                    if (hiddenInput) {
                        console.log('Found hidden input:', hiddenInput);
                        hiddenInput.value = qaId;
                        
                        // 이벤트 트리거
                        hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
                        hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        console.log('Value set to:', hiddenInput.value);
                        
                        // 트리거 버튼 클릭
                        setTimeout(() => {
                            let triggerBtn = document.querySelector('#hidden-delete-trigger button');
                            
                            if (!triggerBtn) {
                                const candidates = document.querySelectorAll('[id*="hidden-delete-trigger"]');
                                for (let elem of candidates) {
                                    let btn = elem.querySelector('button');
                                    if (btn) {
                                        triggerBtn = btn;
                                        break;
                                    }
                                }
                            }
                            
                            if (triggerBtn) {
                                console.log('Clicking trigger button');
                                triggerBtn.click();
                            } else {
                                console.error('Trigger button not found');
                            }
                        }, 250);
                    } else {
                        console.error('Failed to find hidden input element');
                    }
                } catch (e) {
                    console.error('Error in deleteQA:', e);
                }
            };
            console.log('deleteQA function registered globally');
        })();
        </script>
        ''')
        
        with gr.Column(elem_classes="tab-content-padding"):
            gr.Markdown("### 등록된 질문답변 목록")
            gr.Markdown("최신 등록순으로 정렬되며, 페이징을 통해 조회할 수 있습니다.")
            
            # 상태 관리
            current_page = gr.State(1)
            items_per_page = gr.State(10)
            deletion_state = gr.State(_default_deletion_state())
            
            # 숨겨진 컴포넌트 (JavaScript에서 사용)
            hidden_qa_id = gr.Textbox(visible=False, elem_id="hidden-qa-id")
            hidden_delete_trigger = gr.Button(visible=False, elem_id="hidden-delete-trigger")
            
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
            initial_html, initial_page_info, initial_total, initial_page = load_list(1, 50)
            
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
            """삭제 실행 후 목록 갱신 (50개 고정)"""
            selected_qa_id = state.get("selected_qa_id") if state else None
            if not selected_qa_id:
                gr.Error("삭제할 항목을 찾을 수 없습니다")
                html, page_text, total_text, current = load_list(page, 50)
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
                refreshed_view = service.list_items(page=page, items_per_page=50)
                target_page = page
                if page > 1 and len(refreshed_view.items) == 0:
                    target_page = 1

                html, page_text, total_text, current = load_list(target_page, 50)
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
            html, page_text, total_text, current = load_list(page, 50)
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
        items_per_page.value = 50
        current_page.value = 1
        
        # 탭 활성 시 새로고침
        def on_tab_select():
            """탭 활성화 시 목록 새로고침"""
            return load_list(1, 50)
        
        # 이벤트 핸들러 등록
        # refresh_btn.click (50개 고정)
        def refresh_fixed():
            return load_list(1, 50)
        
        refresh_btn.click(
            fn=refresh_fixed,
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        # go_next (50개 고정)
        def go_next_fixed(page: int):
            next_page = page + 1
            return load_list(next_page, 50)
        
        next_btn.click(
            fn=go_next_fixed,
            inputs=[current_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )
        
        # go_prev (50개 고정)
        def go_prev_fixed(page: int):
            prev_page = max(1, page - 1)
            return load_list(prev_page, 50)
        
        prev_btn.click(
            fn=go_prev_fixed,
            inputs=[current_page],
            outputs=[qa_list_html, page_info, total_items_md, current_page]
        )

        # 숨겨진 트리거 버튼이 클릭되면 다이얼로그 열기
        hidden_delete_trigger.click(
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
