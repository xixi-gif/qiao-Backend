from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# 研学主题的模型
class ThemeSchema(BaseModel):
    theme_id: str
    name: str
    goal: str
    duration: str

# 路径规划请求的模型
class PlanRequest(BaseModel):
    theme_id: str = Field(..., description="研学主题的ID")
    start_uid: str = Field(..., description="起点资源的唯一ID (例如: CoreResource_1)")
    num_points: int = Field(5, ge=3, le=10, description="规划点数，建议3-10个")

# 路径规划响应的模型（简化版，你可以根据需要扩展）
class PlanResponse(BaseModel):
    status: str = "success"
    theme_name: str
    total_distance: float
    point_count: int
    route: List[Dict[str, Any]]  # 包含资源详情的列表
    evaluation: Dict[str, Any]    # 科学评估报告
    algorithm_used: str