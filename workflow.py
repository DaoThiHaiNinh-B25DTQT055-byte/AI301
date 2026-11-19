"""
workflow.py - State Machine for Minh An Company B2B Sales Workflow
Implements the official state machine and transition rules conforming strictly to:
"QUY TRÌNH XỬ LÝ CƠ HỘI BÁN HÀNG B2B - MINH AN COMPANY"

Các bước chuẩn theo sơ đồ:
B1. Bắt đầu: Tiếp nhận yêu cầu (RECEIVED)
B2. Phân loại & Kiểm tra thông tin (CLASSIFY_CHECK)
    -> Điểm rẽ 1: Có đủ thông tin?
       - KHÔNG -> Yêu cầu KH làm rõ / bổ sung (WAIT_CLARIFICATION) -> quay lại B1 (RECEIVED)
       - CÓ -> sang B3
B3. Tạo Hồ sơ Cơ hội & Gán người phụ trách (NVKD) (OPPORTUNITY_CREATED)
B4. Thẩm định tồn kho & giá (NVKD & Bộ phận Vận hành) (VALIDATING_STOCK_PRICE)
B5. Lập Báo giá & Dự thảo đề xuất (QUOTE_DRAFTED)
    -> Điểm rẽ 2: Có vượt thẩm quyền / Cần chiết khấu đặc biệt?
       - CÓ -> Trưởng phòng duyệt (WAIT_MANAGER_APPROVAL) -> B6 (COMPLETED)
       - KHÔNG -> B6 (COMPLETED)
B6. Kết thúc: Cập nhật & Theo dõi (COMPLETED)
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import textwrap

class B2BWorkflowState(str, Enum):
    RECEIVED = "RECEIVED"                                 # B1: Tiếp nhận yêu cầu
    CLASSIFY_CHECK = "CLASSIFY_CHECK"                     # B2: Phân loại & Kiểm tra thông tin
    WAIT_CLARIFICATION = "WAIT_CLARIFICATION"             # Nhánh rẽ 1 (Không): Yêu cầu KH làm rõ / bổ sung
    OPPORTUNITY_CREATED = "OPPORTUNITY_CREATED"           # B3: Tạo Hồ sơ Cơ hội & Gán NVKD
    VALIDATING_STOCK_PRICE = "VALIDATING_STOCK_PRICE"     # B4: Thẩm định tồn kho & giá (NVKD & Vận hành)
    QUOTE_DRAFTED = "QUOTE_DRAFTED"                       # B5: Lập Báo giá & Dự thảo đề xuất
    WAIT_MANAGER_APPROVAL = "WAIT_MANAGER_APPROVAL"       # Nhánh rẽ 2 (Có): Trưởng phòng duyệt
    COMPLETED = "COMPLETED"                               # B6: Kết thúc: Cập nhật & Theo dõi

# Bảng siêu dữ liệu mô tả từng trạng thái
STATE_METADATA: Dict[B2BWorkflowState, Dict[str, Any]] = {
    B2BWorkflowState.RECEIVED: {
        "step_no": 1,
        "name_vi": "Tiếp nhận yêu cầu",
        "name_en": "Receive Request",
        "actor_vi": "Khách hàng & Hệ thống tiếp nhận",
        "actor_en": "Customer & Ingestion System",
        "badge_color": "indigo"
    },
    B2BWorkflowState.CLASSIFY_CHECK: {
        "step_no": 2,
        "name_vi": "Phân loại & Kiểm tra thông tin",
        "name_en": "Classify & Verify Information",
        "actor_vi": "Hệ thống AI & NVKD",
        "actor_en": "AI Engine & Sales Rep",
        "badge_color": "cyan"
    },
    B2BWorkflowState.WAIT_CLARIFICATION: {
        "step_no": 2,
        "name_vi": "Yêu cầu KH làm rõ / bổ sung",
        "name_en": "Clarification Required",
        "actor_vi": "Khách hàng & NVKD",
        "actor_en": "Customer & Sales Rep",
        "badge_color": "amber"
    },
    B2BWorkflowState.OPPORTUNITY_CREATED: {
        "step_no": 3,
        "name_vi": "Tạo Hồ sơ Cơ hội & Gán NVKD",
        "name_en": "Create Opportunity & Assign Owner",
        "actor_vi": "Hệ thống CRM & NVKD",
        "actor_en": "CRM System & Sales Rep",
        "badge_color": "blue"
    },
    B2BWorkflowState.VALIDATING_STOCK_PRICE: {
        "step_no": 4,
        "name_vi": "Thẩm định tồn kho & giá",
        "name_en": "Validate Stock & Price",
        "actor_vi": "NVKD & Bộ phận Vận hành",
        "actor_en": "Sales Rep & Operations Team",
        "badge_color": "teal"
    },
    B2BWorkflowState.QUOTE_DRAFTED: {
        "step_no": 5,
        "name_vi": "Lập Báo giá & Dự thảo đề xuất",
        "name_en": "Prepare Quote & Draft Proposal",
        "actor_vi": "NVKD & AI Copilot",
        "actor_en": "Sales Rep & AI Copilot",
        "badge_color": "emerald"
    },
    B2BWorkflowState.WAIT_MANAGER_APPROVAL: {
        "step_no": 6,
        "name_vi": "Trưởng phòng duyệt",
        "name_en": "Manager Approval",
        "actor_vi": "Trưởng phòng Kinh doanh",
        "actor_en": "Sales Manager",
        "badge_color": "rose"
    },
    B2BWorkflowState.COMPLETED: {
        "step_no": 7,
        "name_vi": "Kết thúc: Cập nhật & Theo dõi",
        "name_en": "Close: Update & Follow-up",
        "actor_vi": "NVKD & Bộ phận Vận hành",
        "actor_en": "Sales Rep & Operations",
        "badge_color": "emerald"
    }
}

# Đồ thị chuyển trạng thái hợp lệ theo đúng sơ đồ luồng
ALLOWED_TRANSITIONS: Dict[B2BWorkflowState, List[B2BWorkflowState]] = {
    B2BWorkflowState.RECEIVED: [B2BWorkflowState.CLASSIFY_CHECK],
    B2BWorkflowState.CLASSIFY_CHECK: [B2BWorkflowState.WAIT_CLARIFICATION, B2BWorkflowState.OPPORTUNITY_CREATED],
    B2BWorkflowState.WAIT_CLARIFICATION: [B2BWorkflowState.RECEIVED],
    B2BWorkflowState.OPPORTUNITY_CREATED: [B2BWorkflowState.VALIDATING_STOCK_PRICE],
    B2BWorkflowState.VALIDATING_STOCK_PRICE: [B2BWorkflowState.QUOTE_DRAFTED],
    B2BWorkflowState.QUOTE_DRAFTED: [B2BWorkflowState.WAIT_MANAGER_APPROVAL, B2BWorkflowState.COMPLETED],
    B2BWorkflowState.WAIT_MANAGER_APPROVAL: [B2BWorkflowState.COMPLETED],
    B2BWorkflowState.COMPLETED: [B2BWorkflowState.RECEIVED],
}


class B2BWorkflowEngine:
    """
    Quản lý phiên thực thi máy trạng thái cho một yêu cầu bán hàng B2B.
    Đảm bảo 100% tuân thủ thứ tự các bước và điểm rẽ nhánh.
    """
    def __init__(self, initial_state: B2BWorkflowState = B2BWorkflowState.RECEIVED):
        self.current_state = initial_state
        self.history: List[Dict[str, Any]] = [{
            "from_state": None,
            "to_state": initial_state.value,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "actor": STATE_METADATA[initial_state]["actor_vi"],
            "note": "Khởi tạo tiếp nhận yêu cầu ban đầu"
        }]
        self.opportunity_record: Optional[Dict[str, Any]] = None

    def can_transition_to(self, target_state: B2BWorkflowState) -> bool:
        """Kiểm tra tính hợp lệ của việc chuyển dịch trạng thái."""
        allowed = ALLOWED_TRANSITIONS.get(self.current_state, [])
        return target_state in allowed

    def transition(self, target_state: B2BWorkflowState, note: str = "", actor: Optional[str] = None) -> bool:
        """
        Thực hiện chuyển dịch trạng thái an toàn.
        Nếu không hợp lệ, ghi log cảnh báo thân thiện thay vì làm đứt đoạn ứng dụng.
        """
        if not self.can_transition_to(target_state):
            print(f"[Workflow Warning] Chuyển trạng thái không hợp lệ: {self.current_state.value} -> {target_state.value}. Bỏ qua.")
            return False

        from_state = self.current_state
        self.current_state = target_state
        assigned_actor = actor or STATE_METADATA[target_state]["actor_vi"]

        self.history.append({
            "from_state": from_state.value,
            "to_state": target_state.value,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "actor": assigned_actor,
            "note": note
        })
        return True

    def create_opportunity_record(
        self, 
        opp_id: str, 
        company_name: str, 
        contact_person: str, 
        sales_rep: Dict[str, Any], 
        items: List[Dict[str, Any]],
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """Tạo bản ghi Hồ sơ Cơ hội tại Bước 3 theo sơ đồ quy trình."""
        self.opportunity_record = {
            "opportunity_id": opp_id,
            "company_name": company_name,
            "contact_person": contact_person,
            "assigned_rep": sales_rep.get("FullName", "Chưa gán") if sales_rep else "Chưa gán",
            "rep_staff_id": sales_rep.get("StaffID", "") if sales_rep else "",
            "rep_specialty": sales_rep.get("Specialty", "") if sales_rep else "",
            "items_count": len(items),
            "budget": budget,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "status": "Đang thẩm định tồn kho & giá"
        }
        return self.opportunity_record
