from fastapi import APIRouter, HTTPException, Query
from app.api.services.planner_service import TSPPathPlanner
from app.api.schemas.planner import ThemeSchema, PlanRequest, PlanResponse
from typing import List, Dict, Any

router = APIRouter()

# 实例化规划器（它会自动使用我们在 services 里配置好的 neo4j_conn）
planner = TSPPathPlanner()


@router.get("/themes", response_model=List[ThemeSchema], summary="获取所有研学主题")
async def get_all_themes():
    """
    从 Neo4j 获取所有定义的研学主题列表
    """
    try:
        themes = planner.get_all_themes()
        return themes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取主题失败: {str(e)}")


@router.get("/theme-resources/{theme_id}", summary="获取主题下的所有资源点（测试辅助）")
async def get_theme_resources(theme_id: str):
    try:
        resources = planner.get_resources_by_theme(theme_id)
        if not resources:
            raise HTTPException(status_code=404, detail="该主题下未找到有效资源")

        formatted_resources = []
        for r in resources:
            lat_str = r.get("lat", "")
            lon_str = r.get("lon", "")
            try:
                clean_lat = ''.join([c for c in lat_str if c.isdigit() or c == '.'])
                latitude = float(clean_lat) if clean_lat else 0.0
            except:
                latitude = 0.0
            try:
                clean_lon = ''.join([c for c in lon_str if c.isdigit() or c == '.'])
                longitude = float(clean_lon) if clean_lon else 0.0
            except:
                longitude = 0.0

            formatted_resources.append({
                "id": r.get("id", ""),
                "activity_duration": r.get("duration", ""),
                "capacity": r.get("capacity", ""),
                "description": r.get("description", ""),
                "district": r.get("district", ""),
                "latitude": latitude,
                "longitude": longitude,
                "name": r.get("name", ""),
                "opening_hours": r.get("opening_hours", ""),
                "related_resources": r.get("related_resources", ""),
                "resource_id": r.get("resource_id", ""),
                "uid": r.get("uid", ""),
                "type": r.get("type", "")
            })
        return formatted_resources
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询资源失败: {str(e)}")

@router.post("/plan", response_model=PlanResponse, summary="生成最优研学路径")
async def generate_study_route(request: PlanRequest):
    """
    核心接口：基于TSP算法生成最优路径，并返回详细的科学评估报告
    """
    # 1. 获取该主题下的所有资源
    try:
        resources = planner.get_resources_by_theme(request.theme_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"从数据库读取资源出错: {str(e)}")

    if not resources:
        raise HTTPException(status_code=404, detail="该主题下未找到有效资源")

    # 2. 查找起点的索引
    start_index = -1
    for i, res in enumerate(resources):
        if res['uid'] == request.start_uid:
            start_index = i
            break

    if start_index == -1:
        raise HTTPException(
            status_code=400,
            detail=f"在主题 {request.theme_id} 中未找到 ID 为 {request.start_uid} 的起点资源。请先通过获取资源接口确认 UID。"
        )

    # 3. 执行算法生成最优路线
    try:
        result = planner.generate_optimal_route(
            resources=resources,
            start_index=start_index,
            num_points=request.num_points
        )

        if not result:
            raise HTTPException(status_code=500, detail="规划算法未能生成有效路线")

        # 4. 组装符合 PlanResponse Schema 的返回数据
        return {
            "status": "success",
            "theme_name": resources[0].get('theme_name', '未知主题'),
            "total_distance": float(result['total_distance']),
            "point_count": int(result['point_count']),
            "route": result['route'],
            "evaluation": result.get('evaluation_report', {}),
            "algorithm_used": result.get('algorithm_name', 'TSP算法')
        }
    except Exception as e:
        # 打印详细错误方便后端调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"规划过程发生内部错误: {str(e)}")