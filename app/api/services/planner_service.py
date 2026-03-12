import math
import random
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from app.api.db.neo4j_db import Neo4jConnection
from app.api.db.neo4j_db import neo4j_conn

class ScientificRouteEvaluator:
    """
    基于文献评价指标体系的研学路径科学评估器

    一级指标（4个核心维度）：
    1. 内容设计质量 (A) - 主题契合与教育价值
    2. 资源适配程度 (B) - 资源配置与匹配度
    3. 时空合理布局 (C) - 时间空间优化
    4. 实践可行保障 (D) - 安全成本与可持续
    """

    def __init__(self):
        # 一级指标权重（总和为1.0）
        self.level1_weights = {
            'A': 0.35,  # 内容设计质量 - 最重要
            'B': 0.30,  # 资源适配程度
            'C': 0.20,  # 时空合理布局
            'D': 0.15,  # 实践可行保障
        }

        # 二级指标定义及权重（相对一级指标）
        self.level2_indicators = {
            'A': {  # 内容设计质量
                'A1': {'name': '目标导向性', 'weight': 0.30, 'description': '路径与研学目标契合度'},
                'A2': {'name': '主题完整性', 'weight': 0.25, 'description': '主题内容全面覆盖度'},
                'A3': {'name': '教育价值度', 'weight': 0.25, 'description': '教育意义与价值体现'},
                'A4': {'name': '文化契合度', 'weight': 0.20, 'description': '地域文化特色融合'},
            },
            'B': {  # 资源适配程度
                'B1': {'name': '资源匹配度', 'weight': 0.30, 'description': '资源与主题匹配程度'},
                'B2': {'name': '类型多样性', 'weight': 0.25, 'description': '资源类型多样均衡'},
                'B3': {'name': '等级适宜性', 'weight': 0.25, 'description': '资源等级结构合理'},
                'B4': {'name': '容量适配性', 'weight': 0.20, 'description': '资源容量满足需求'},
            },
            'C': {  # 时空合理布局
                'C1': {'name': '时间分配合理', 'weight': 0.35, 'description': '各环节时间科学分配'},
                'C2': {'name': '空间布局优化', 'weight': 0.35, 'description': '空间分布高效优化'},
                'C3': {'name': '节奏适宜性', 'weight': 0.30, 'description': '活动节奏张弛有度'},
            },
            'D': {  # 实践可行保障
                'D1': {'name': '安全保障度', 'weight': 0.35, 'description': '安全风险可控程度'},
                'D2': {'name': '成本效益比', 'weight': 0.30, 'description': '成本与效益平衡度'},
                'D3': {'name': '环境友好性', 'weight': 0.20, 'description': '生态环境友好程度'},
                'D4': {'name': '实施可行性', 'weight': 0.15, 'description': '实际实施便利程度'},
            }
        }

    def evaluate_route(self, route_data: Dict, theme: Dict) -> Dict:
        """
        执行全面评估

        参数:
            route_data: 路径数据 {route: List[Dict], total_distance: float, ...}
            theme: 主题数据 {name: str, goal: str, ...}

        返回:
            完整的科学评估报告
        """
        route = route_data.get('route', [])
        total_distance = route_data.get('total_distance', 0)

        print(f"\n 开始科学评估研学路径...")
        print(f"  评估路径包含 {len(route)} 个资源点")
        print(f"  路径总距离: {total_distance:.1f}km")

        # 执行四个维度的评估
        evaluation_results = {
            'A': self._evaluate_content_design(route, theme),  # 内容设计质量
            'B': self._evaluate_resource_adaptation(route, theme),  # 资源适配程度
            'C': self._evaluate_spatiotemporal_layout(route, total_distance),  # 时空合理布局
            'D': self._evaluate_practical_feasibility(route),  # 实践可行保障
        }

        # 计算综合评分和等级
        comprehensive_result = self._calculate_comprehensive_result(evaluation_results)

        # 生成详细评估报告
        final_report = self._generate_final_report(evaluation_results, comprehensive_result,
                                                   route_data, theme)

        return final_report

    def _evaluate_content_design(self, route: List[Dict], theme: Dict) -> Dict:
        """
        一级指标A：内容设计质量评估
        """
        results = {}

        # A1: 目标导向性
        goal_score = self._calculate_goal_alignment(route, theme)
        results['A1'] = {
            'score': goal_score,
            'name': '目标导向性',
            'details': f"路径与主题目标'{theme.get('goal', '')}'的契合程度",
        }

        # A2: 主题完整性
        completeness_score = self._calculate_theme_completeness(route, theme)
        results['A2'] = {
            'score': completeness_score,
            'name': '主题完整性',
            'details': f"对主题'{theme.get('name', '')}'的全面覆盖程度",
        }

        # A3: 教育价值度
        education_score = self._calculate_educational_value(route, theme)
        results['A3'] = {
            'score': education_score,
            'name': '教育价值度',
            'details': '知识传授、能力培养、价值观引导的综合体现',
        }

        # A4: 文化契合度
        culture_score = self._calculate_cultural_fit(route, theme)
        results['A4'] = {
            'score': culture_score,
            'name': '文化契合度',
            'details': '与侨乡文化、地域特色的融合程度',
        }

        # 计算维度总分
        total_score = sum(
            results[key]['score'] * self.level2_indicators['A'][key]['weight']
            for key in results
        )

        return {
            'level2_results': results,
            'total_score': round(total_score, 2),
            'weighted_score': round(total_score * self.level1_weights['A'], 2),
        }

    def _evaluate_resource_adaptation(self, route: List[Dict], theme: Dict) -> Dict:
        """
        一级指标B：资源适配程度评估
        """
        results = {}

        # B1: 资源匹配度
        match_score = self._calculate_resource_match(route, theme)
        results['B1'] = {
            'score': match_score,
            'name': '资源匹配度',
            'details': '资源与研学主题的相关性和匹配程度',
        }

        # B2: 类型多样性
        diversity_score = self._calculate_type_diversity(route)
        results['B2'] = {
            'score': diversity_score,
            'name': '类型多样性',
            'details': f"资源类型分布情况",
        }

        # B3: 等级适宜性
        level_score = self._calculate_level_suitability(route)
        results['B3'] = {
            'score': level_score,
            'name': '等级适宜性',
            'details': '资源等级结构的合理性',
        }

        # B4: 容量适配性
        capacity_score = self._calculate_capacity_suitability(route)
        results['B4'] = {
            'score': capacity_score,
            'name': '容量适配性',
            'details': '资源容量与团队规模的匹配程度',
        }

        # 计算维度总分
        total_score = sum(
            results[key]['score'] * self.level2_indicators['B'][key]['weight']
            for key in results
        )

        return {
            'level2_results': results,
            'total_score': round(total_score, 2),
            'weighted_score': round(total_score * self.level1_weights['B'], 2),
        }

    def _evaluate_spatiotemporal_layout(self, route: List[Dict], total_distance: float) -> Dict:
        """
        一级指标C：时空合理布局评估
        """
        results = {}

        # C1: 时间分配合理
        time_score = self._calculate_time_allocation(route)
        results['C1'] = {
            'score': time_score,
            'name': '时间分配合理',
            'details': '各环节时间分配的科学性和合理性',
        }

        # C2: 空间布局优化
        space_score = self._calculate_spatial_layout(route, total_distance)
        results['C2'] = {
            'score': space_score,
            'name': '空间布局优化',
            'details': f"空间分布的最优化程度",
        }

        # C3: 节奏适宜性
        rhythm_score = self._calculate_activity_rhythm(route)
        results['C3'] = {
            'score': rhythm_score,
            'name': '节奏适宜性',
            'details': '活动节奏的张弛度和适宜性',
        }

        # 计算维度总分
        total_score = sum(
            results[key]['score'] * self.level2_indicators['C'][key]['weight']
            for key in results
        )

        return {
            'level2_results': results,
            'total_score': round(total_score, 2),
            'weighted_score': round(total_score * self.level1_weights['C'], 2),
        }

    def _evaluate_practical_feasibility(self, route: List[Dict]) -> Dict:
        """
        一级指标D：实践可行保障评估
        """
        results = {}

        # D1: 安全保障度
        safety_score = self._calculate_safety_assurance(route)
        results['D1'] = {
            'score': safety_score,
            'name': '安全保障度',
            'details': '安全风险评估和保障措施的完备性',
        }

        # D2: 成本效益比
        cost_score = self._calculate_cost_effectiveness(route)
        results['D2'] = {
            'score': cost_score,
            'name': '成本效益比',
            'details': '成本控制与教育效益的平衡',
        }

        # D3: 环境友好性
        environment_score = self._calculate_environmental_friendliness(route)
        results['D3'] = {
            'score': environment_score,
            'name': '环境友好性',
            'details': '对生态环境的保护和友好程度',
        }

        # D4: 实施可行性
        feasibility_score = self._calculate_implementation_feasibility(route)
        results['D4'] = {
            'score': feasibility_score,
            'name': '实施可行性',
            'details': '实际操作的便利性和可行性',
        }

        # 计算维度总分
        total_score = sum(
            results[key]['score'] * self.level2_indicators['D'][key]['weight']
            for key in results
        )

        return {
            'level2_results': results,
            'total_score': round(total_score, 2),
            'weighted_score': round(total_score * self.level1_weights['D'], 2),
        }

    # ================= 二级指标计算函数 =================

    def _calculate_goal_alignment(self, route: List[Dict], theme: Dict) -> float:
        """A1: 目标导向性评分"""
        theme_goal = theme.get('goal', '')
        if not theme_goal or not route:
            return 60.0

        # 分析目标关键词
        goal_keywords = ['文化', '历史', '实践', '体验', '了解', '学习', '认识', '传承', '创新']
        keyword_matches = sum(1 for keyword in goal_keywords if keyword in theme_goal)

        # 根据关键词匹配度评分
        if keyword_matches >= 4:
            return 90.0
        elif keyword_matches >= 3:
            return 85.0
        elif keyword_matches >= 2:
            return 75.0
        else:
            return 65.0

    def _calculate_theme_completeness(self, route: List[Dict], theme: Dict) -> float:
        """A2: 主题完整性评分"""
        resource_count = len(route)

        # 根据资源数量评分
        if resource_count >= 6:
            return 92.0
        elif resource_count >= 5:
            return 85.0
        elif resource_count >= 4:
            return 78.0
        elif resource_count >= 3:
            return 70.0
        else:
            return 60.0

    def _calculate_educational_value(self, route: List[Dict], theme: Dict) -> float:
        """A3: 教育价值度评分"""
        if not route:
            return 60.0

        # 根据资源类型多样性评估教育价值
        resource_types = set(res.get('type', '') for res in route)
        type_count = len(resource_types)

        # 不同类型资源的教育价值不同
        education_score = 70.0  # 基础分

        # 资源类型加分
        type_bonus = {
            'CoreResource': 8,  # 核心资源教育价值高
            'IntangibleResource': 6,  # 非物质文化资源
            'TourismResource': 4,  # 旅游资源
        }

        for res in route:
            res_type = res.get('type', '')
            if res_type in type_bonus:
                education_score += type_bonus[res_type] * 0.5

        # 多样性加分
        education_score += min(type_count * 5, 15)

        return min(education_score, 95.0)

    def _calculate_cultural_fit(self, route: List[Dict], theme: Dict) -> float:
        """A4: 文化契合度评分"""
        if not route:
            return 60.0

        # 检查资源是否与侨乡文化相关
        cultural_keywords = ['侨', '华侨', '潮汕', '潮州', '汕头', '文化', '传统', '民俗']
        cultural_count = 0

        for res in route:
            res_name = res.get('name', '').lower()
            res_desc = res.get('description', '').lower()

            # 检查是否包含文化关键词
            if any(keyword in res_name or keyword in res_desc for keyword in cultural_keywords):
                cultural_count += 1

        cultural_ratio = cultural_count / len(route)

        if cultural_ratio >= 0.8:
            return 95.0
        elif cultural_ratio >= 0.6:
            return 85.0
        elif cultural_ratio >= 0.4:
            return 75.0
        elif cultural_ratio >= 0.2:
            return 65.0
        else:
            return 55.0

    def _calculate_resource_match(self, route: List[Dict], theme: Dict) -> float:
        """B1: 资源匹配度评分"""
        if not route:
            return 50.0

        # 计算直接关联资源比例
        direct_count = sum(1 for res in route if res.get('relation_type') == 'direct')
        match_ratio = direct_count / len(route)

        if match_ratio >= 0.8:
            return 95.0
        elif match_ratio >= 0.6:
            return 85.0
        elif match_ratio >= 0.4:
            return 75.0
        elif match_ratio >= 0.2:
            return 65.0
        else:
            return 55.0

    def _calculate_type_diversity(self, route: List[Dict]) -> float:
        """B2: 类型多样性评分"""
        if not route:
            return 50.0

        resource_types = set(res.get('type', '') for res in route)
        type_count = len(resource_types)

        if type_count >= 3:
            return 92.0
        elif type_count == 2:
            # 检查两种类型的平衡性
            type_counts = {}
            for res in route:
                res_type = res.get('type', '')
                type_counts[res_type] = type_counts.get(res_type, 0) + 1

            max_count = max(type_counts.values())
            min_count = min(type_counts.values())
            balance_ratio = min_count / max_count if max_count > 0 else 0

            if balance_ratio >= 0.5:
                return 85.0
            else:
                return 75.0
        else:
            return 65.0

    def _calculate_level_suitability(self, route: List[Dict]) -> float:
        """B3: 等级适宜性评分"""
        if not route:
            return 60.0

        # 假设资源有等级信息（这里简化为随机分布）
        # 实际应用中应从数据库获取资源等级
        resource_count = len(route)

        # 模拟等级分布：理想情况是多种等级混合
        if resource_count >= 4:
            return 85.0  # 资源多，容易形成等级结构
        elif resource_count >= 3:
            return 75.0
        else:
            return 65.0

    def _calculate_capacity_suitability(self, route: List[Dict]) -> float:
        """B4: 容量适配性评分"""
        if not route:
            return 60.0

        # 检查资源是否有容量信息
        has_capacity_count = sum(1 for res in route if res.get('capacity'))

        if has_capacity_count == len(route):
            return 90.0  # 所有资源都有容量信息
        elif has_capacity_count >= len(route) * 0.7:
            return 80.0
        elif has_capacity_count >= len(route) * 0.5:
            return 70.0
        else:
            return 60.0

    def _calculate_time_allocation(self, route: List[Dict]) -> float:
        """C1: 时间分配合理评分"""
        if not route:
            return 60.0

        total_duration = 0
        valid_duration_count = 0

        for res in route:
            duration_str = res.get('duration', '60')
            try:
                duration = int(str(duration_str).replace('分钟', '').replace('min', '').strip())
                total_duration += duration
                valid_duration_count += 1
            except:
                total_duration += 60  # 默认60分钟

        # 检查所有资源是否有有效时长
        if valid_duration_count == len(route):
            time_info_score = 20  # 全部有时长信息
        elif valid_duration_count >= len(route) * 0.7:
            time_info_score = 15
        elif valid_duration_count >= len(route) * 0.5:
            time_info_score = 10
        else:
            time_info_score = 5

        # 按每天6小时计算总天数
        total_days = total_duration / 60 / 6

        if 0.8 <= total_days <= 1.2:
            time_distribution_score = 75  # 一天左右最合适
        elif 0.5 <= total_days < 0.8 or 1.2 < total_days <= 1.5:
            time_distribution_score = 65
        elif total_days > 1.5:
            time_distribution_score = 55  # 时间太长
        else:
            time_distribution_score = 60  # 时间太短

        return min(time_info_score + time_distribution_score, 100.0)

    def _calculate_spatial_layout(self, route: List[Dict], total_distance: float) -> float:
        """C2: 空间布局优化评分"""
        if len(route) < 2:
            return 70.0

        # 根据距离评分
        avg_distance = total_distance / max(len(route) - 1, 1)

        if avg_distance <= 3:
            return 95.0  # 距离很近，布局优秀
        elif avg_distance <= 6:
            return 85.0
        elif avg_distance <= 10:
            return 75.0
        elif avg_distance <= 15:
            return 65.0
        else:
            return 55.0  # 距离太远

    def _calculate_activity_rhythm(self, route: List[Dict]) -> float:
        """C3: 节奏适宜性评分"""
        if len(route) < 3:
            return 70.0

        # 检查资源类型交替变化（避免同类资源连续出现）
        rhythm_score = 70.0
        consecutive_same_type = 0

        for i in range(1, len(route)):
            if route[i].get('type') == route[i - 1].get('type'):
                consecutive_same_type += 1
            else:
                consecutive_same_type = 0

            # 连续出现同类资源扣分
            if consecutive_same_type >= 2:
                rhythm_score -= 5

        # 检查活动时长变化（避免所有活动时长相同）
        durations = []
        for res in route:
            duration_str = res.get('duration', '60')
            try:
                duration = int(str(duration_str).replace('分钟', '').replace('min', '').strip())
                durations.append(duration)
            except:
                durations.append(60)

        if len(set(durations)) >= 3:
            rhythm_score += 10  # 时长变化丰富
        elif len(set(durations)) >= 2:
            rhythm_score += 5

        return min(max(rhythm_score, 50.0), 95.0)

    def _calculate_safety_assurance(self, route: List[Dict]) -> float:
        """D1: 安全保障度评分"""
        if not route:
            return 70.0

        # 安全检查
        safety_indicators = 0
        total_resources = len(route)

        for res in route:
            res_type = res.get('type', '')
            # 不同类型资源有不同的安全考量
            if 'Tourism' in res_type:
                safety_indicators += 1  # 旅游景点通常有安全管理
            elif 'Core' in res_type:
                safety_indicators += 0.8  # 核心资源可能有较好管理
            else:
                safety_indicators += 0.5

        safety_ratio = safety_indicators / total_resources
        safety_score = 60.0 + (safety_ratio * 40)

        return min(safety_score, 95.0)

    def _calculate_cost_effectiveness(self, route: List[Dict]) -> float:
        """D2: 成本效益比评分"""
        resource_count = len(route)
        if resource_count == 0:
            return 60.0

        # 基于资源类型评估成本效益
        cost_score = 70.0  # 基础分

        type_costs = {
            'CoreResource': 1.2,  # 核心资源成本可能较高
            'IntangibleResource': 1.0,  # 中等成本
            'TourismResource': 0.8,  # 旅游资源成本较低
        }

        type_benefits = {
            'CoreResource': 1.5,  # 教育效益高
            'IntangibleResource': 1.3,  # 文化效益高
            'TourismResource': 1.0,  # 中等效益
        }

        total_cost_ratio = 0
        total_benefit_ratio = 0

        for res in route:
            res_type = res.get('type', '')
            if res_type in type_costs:
                total_cost_ratio += type_costs[res_type]
                total_benefit_ratio += type_benefits[res_type]
            else:
                total_cost_ratio += 1.0
                total_benefit_ratio += 1.0

        if total_resources := len(route):
            avg_cost = total_cost_ratio / total_resources
            avg_benefit = total_benefit_ratio / total_resources

            # 成本效益比 = 效益/成本
            cost_benefit_ratio = avg_benefit / avg_cost if avg_cost > 0 else 1.0

            if cost_benefit_ratio >= 1.3:
                cost_score = 90.0
            elif cost_benefit_ratio >= 1.1:
                cost_score = 80.0
            elif cost_benefit_ratio >= 0.9:
                cost_score = 70.0
            else:
                cost_score = 60.0

        return cost_score

    def _calculate_environmental_friendliness(self, route: List[Dict]) -> float:
        """D3: 环境友好性评分"""
        if not route:
            return 70.0

        # 检查资源是否涉及自然环境
        environmental_keywords = ['公园', '自然', '生态', '保护区', '森林', '湿地']
        environmental_count = 0

        for res in route:
            res_name = res.get('name', '')
            res_desc = res.get('description', '')

            # 检查是否包含环境相关关键词
            if any(keyword in res_name or keyword in res_desc for keyword in environmental_keywords):
                environmental_count += 2  # 环境友好资源加分
            else:
                environmental_count += 1  # 普通资源

        environmental_ratio = environmental_count / (len(route) * 2)
        environment_score = 60.0 + (environmental_ratio * 40)

        return min(environment_score, 95.0)

    def _calculate_implementation_feasibility(self, route: List[Dict]) -> float:
        """D4: 实施可行性评分"""
        if not route:
            return 60.0

        feasibility_score = 70.0  # 基础分

        # 检查必要信息完整性
        info_completeness = 0
        for res in route:
            has_coords = res.get('lon_parsed') and res.get('lat_parsed')
            has_duration = res.get('duration')
            has_district = res.get('district') and res.get('district') != '未知'

            if has_coords and has_duration and has_district:
                info_completeness += 1
            elif has_coords and (has_duration or has_district):
                info_completeness += 0.5

        info_ratio = info_completeness / len(route)

        if info_ratio >= 0.9:
            feasibility_score += 20
        elif info_ratio >= 0.7:
            feasibility_score += 10
        elif info_ratio >= 0.5:
            feasibility_score += 5

        return min(feasibility_score, 95.0)

    def _calculate_comprehensive_result(self, evaluation_results: Dict) -> Dict:
        """
        计算综合评分和等级
        """
        # 计算加权总分
        total_weighted_score = sum(
            eval_data['weighted_score'] for eval_data in evaluation_results.values()
        )

        # 确定等级
        grade = self._determine_grade(total_weighted_score)

        # 各维度贡献分析
        dimension_contributions = {}
        for dim_key, dim_data in evaluation_results.items():
            contribution = dim_data['weighted_score'] / total_weighted_score * 100 if total_weighted_score > 0 else 0
            dimension_contributions[dim_key] = round(contribution, 1)

        return {
            'total_score': round(total_weighted_score, 2),
            'grade': grade['name'],
            'grade_description': grade['description'],
            'dimension_contributions': dimension_contributions,
            'recommendation': self._generate_recommendation(grade, evaluation_results)
        }

    def _determine_grade(self, score: float) -> Dict:
        """确定评估等级"""
        if score >= 90:
            return {'name': '优秀', 'description': '完全符合标准，可立即实施'}
        elif score >= 80:
            return {'name': '良好', 'description': '大部分符合，少量优化即可'}
        elif score >= 70:
            return {'name': '中等', 'description': '基本符合，需要一定改进'}
        elif score >= 60:
            return {'name': '合格', 'description': '达到最低要求，需较多改进'}
        else:
            return {'name': '不合格', 'description': '未达标，需要重新设计'}

    def _generate_recommendation(self, grade: Dict, eval_results: Dict) -> str:
        """生成推荐意见"""
        if grade['name'] == '优秀':
            return "强烈推荐实施，当前路径设计科学合理"
        elif grade['name'] == '良好':
            # 找出需要改进的维度
            weak_dims = []
            for dim_key, dim_data in eval_results.items():
                if dim_data['total_score'] < 80:
                    dim_name = self._get_dimension_name(dim_key)
                    weak_dims.append(dim_name)

            if weak_dims:
                return f"推荐实施，建议加强{'、'.join(weak_dims)}的优化"
            else:
                return "推荐实施，当前路径设计良好"
        elif grade['name'] == '中等':
            return "建议实施，但需要按照评估建议进行改进"
        elif grade['name'] == '合格':
            return "可以实施，但需要较多改进才能达到良好效果"
        else:
            return "不建议实施，需要重新规划设计"

    def _generate_final_report(self, evaluation_results: Dict, comprehensive_result: Dict,
                               route_data: Dict, theme: Dict) -> Dict:
        """
        生成最终评估报告
        """
        report = {
            'metadata': {
                'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'theme': theme.get('name'),
                'theme_goal': theme.get('goal'),
                'route_points': len(route_data.get('route', [])),
                'total_distance': route_data.get('total_distance'),
            },
            'comprehensive_assessment': comprehensive_result,
            'dimension_details': evaluation_results,
            'summary': self._generate_summary(evaluation_results, comprehensive_result),
            'recommendations': self._generate_actionable_recommendations(evaluation_results)
        }

        return report

    def _generate_summary(self, eval_results: Dict, comp_result: Dict) -> str:
        """生成评估摘要"""
        strengths = []
        for dim_key, dim_data in eval_results.items():
            if dim_data['total_score'] >= 85:
                dim_name = self._get_dimension_name(dim_key)
                strengths.append(dim_name)

        if strengths:
            strength_text = f"优势维度：{'、'.join(strengths)}"
        else:
            strength_text = "无明显优势维度"

        return f"{strength_text}，综合评估{comp_result['grade']}级，{comp_result['grade_description']}"

    def _generate_actionable_recommendations(self, eval_results: Dict) -> List[str]:
        """生成可操作的改进建议"""
        recommendations = []

        # 分析各维度弱点，生成针对性建议
        for dim_key, dim_data in eval_results.items():
            dim_name = self._get_dimension_name(dim_key)

            # 找出该维度中评分最低的二级指标
            min_l2_score = 100
            min_l2_key = None
            for l2_key, l2_data in dim_data['level2_results'].items():
                if l2_data['score'] < min_l2_score:
                    min_l2_score = l2_data['score']
                    min_l2_key = l2_key

            if min_l2_key and min_l2_score < 75:
                l2_name = self.level2_indicators[dim_key][min_l2_key]['name']
                rec = f"加强{l2_name}建设，提高{dim_name}水平（当前评分：{min_l2_score:.1f}）"
                recommendations.append(rec)

        # 添加通用建议
        if not recommendations:
            recommendations.append("路径设计良好，继续保持当前设计理念")

        return recommendations[:5]  # 最多返回5条建议

    def _get_dimension_name(self, dim_key: str) -> str:
        """获取维度名称"""
        dim_names = {
            'A': '内容设计质量',
            'B': '资源适配程度',
            'C': '时空合理布局',
            'D': '实践可行保障'
        }
        return dim_names.get(dim_key, '未知维度')

    def print_assessment_report(self, report: Dict, detailed: bool = True):
        """
        打印评估报告

        参数:
            report: 评估报告
            detailed: 是否显示详细评估
        """
        print("\n" + "=" * 70)
        print("📊 研学路径科学评估报告")
        print("=" * 70)

        # 基本信息
        meta = report['metadata']
        print(f"主题: {meta['theme']}")
        print(f"评估时间: {meta['evaluation_time']}")
        print(f"路径点数: {meta['route_points']}个")
        print(f"总距离: {meta.get('total_distance', 0):.1f}km")

        # 综合评估结果
        assessment = report['comprehensive_assessment']
        print(f"\n🏆 综合评估结果")
        print(f"  综合评分: {assessment['total_score']:.1f}/100")
        print(f"  评估等级: {assessment['grade']}")
        print(f"  等级描述: {assessment['grade_description']}")
        print(f"  推荐意见: {assessment['recommendation']}")

        # 各维度评分
        print(f"\n📈 各维度评分（权重贡献）")
        dim_details = report['dimension_details']
        for dim_key, dim_data in dim_details.items():
            dim_name = self._get_dimension_name(dim_key)
            contribution = assessment['dimension_contributions'][dim_key]
            print(f"  {dim_name}: {dim_data['total_score']:.1f}分 (贡献度: {contribution}%)")

        # 详细评估
        if detailed:
            print(f"\n📋 详细评估结果")
            for dim_key, dim_data in dim_details.items():
                dim_name = self._get_dimension_name(dim_key)
                print(f"\n  【{dim_name}】评分: {dim_data['total_score']:.1f}")

                for l2_key, l2_data in dim_data['level2_results'].items():
                    indicator_name = l2_data['name']
                    print(f"    {indicator_name}: {l2_data['score']:.1f} - {l2_data['details']}")

        # 改进建议
        print(f"\n💡 改进建议")
        recommendations = report.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 70)
        print("评估完成！")


class TSPPathPlanner:
    """TSP路径规划器"""

    def __init__(self):
        self.db = neo4j_conn
        self.distance_cache = {}
        self.evaluator = ScientificRouteEvaluator()

    def get_all_themes(self) -> List[Dict]:
        """获取所有研学主题"""
        query = """
        MATCH (th:StudyTheme)
        RETURN th.theme_id as theme_id, th.name as name,
               th.study_goal as goal, th.suitable_duration as duration
        ORDER BY th.name
        """
        results = self.db.execute_query(query)
        return [dict(record) for record in results]

    def get_resources_by_theme(self, theme_id: str,
                               resource_types: List[str] = None,
                               include_indirect: bool = True) -> List[Dict]:
        """
        获取指定主题下的资源
        包括直接关联和间接关联的资源

        参数:
            theme_id: 主题ID
            resource_types: 资源类型列表
            include_indirect: 是否包含通过活动间接关联的资源
        """
        if resource_types is None:
            resource_types = ['CoreResource', 'IntangibleResource', 'TourismResource']

        all_resources = []

        # 首先获取主题信息
        theme_query = """
        MATCH (th:StudyTheme {theme_id: $theme_id})
        RETURN th.name as theme_name, th.study_goal as goal
        """
        theme_info = self.db.execute_query(theme_query, {'theme_id': theme_id})
        theme_name = theme_info[0]['theme_name'] if theme_info else "未知主题"

        print(f"主题: {theme_name}")

        for resource_type in resource_types:
            print(f"  查找 {resource_type} 资源...")

            # 1. 查找直接关联主题的资源
            direct_query = f"""
            MATCH (r:{resource_type})-[:`关联主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            WHERE r.longitude IS NOT NULL AND r.latitude IS NOT NULL
            RETURN r.resource_id as id, r.name as name, 
                   '{resource_type}' as type,
                   COALESCE(r.district, '未知') as district,
                   COALESCE(r.activity_duration, '60') as duration,
                   r.longitude as lon,
                   r.latitude as lat,
                   COALESCE(r.description, '') as description,
                   COALESCE(r.capacity, '') as capacity,
                   'direct' as relation_type
            """

            # 2. 查找通过研学活动间接关联的资源
            indirect_query = f"""
            MATCH (r:{resource_type})-[:`包含活动`]->(a:StudyActivity)
            MATCH (a)-[:`适配主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            WHERE r.longitude IS NOT NULL AND r.latitude IS NOT NULL
            RETURN DISTINCT r.resource_id as id, r.name as name, 
                   '{resource_type}' as type,
                   COALESCE(r.district, '未知') as district,
                   COALESCE(r.activity_duration, '60') as duration,
                   r.longitude as lon,
                   r.latitude as lat,
                   COALESCE(r.description, '') as description,
                   COALESCE(r.capacity, '') as capacity,
                   'indirect' as relation_type
            """

            # 3. 查找通过主题活动间接关联的资源
            # 有些资源可能通过"适配主题"关系连接
            theme_related_query = f"""
            MATCH (r:{resource_type})-[:`适配主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            WHERE r.longitude IS NOT NULL AND r.latitude IS NOT NULL
            RETURN DISTINCT r.resource_id as id, r.name as name, 
                   '{resource_type}' as type,
                   COALESCE(r.district, '未知') as district,
                   COALESCE(r.activity_duration, '60') as duration,
                   r.longitude as lon,
                   r.latitude as lat,
                   COALESCE(r.description, '') as description,
                   COALESCE(r.capacity, '') as capacity,
                   'theme_related' as relation_type
            """

            # 执行查询
            direct_results = self.db.execute_query(direct_query, {'theme_id': theme_id})
            indirect_results = [] if not include_indirect else self.db.execute_query(indirect_query,
                                                                                     {'theme_id': theme_id})
            theme_related_results = self.db.execute_query(theme_related_query, {'theme_id': theme_id})

            # 合并结果
            all_results = list(direct_results) + list(indirect_results) + list(theme_related_results)

            direct_count = len(direct_results)
            indirect_count = len(indirect_results)
            theme_related_count = len(theme_related_results)

            print(f"    直接关联: {direct_count}个")
            print(f"    通过活动关联: {indirect_count}个")
            print(f"    适配主题关联: {theme_related_count}个")

            for record in all_results:
                # 确保有坐标信息
                if record['lon'] and record['lat']:
                    resource = dict(record)
                    # 解析坐标
                    resource['lon_parsed'], resource['lat_parsed'] = self.parse_coordinates(
                        f"{record['lon']},{record['lat']}"
                    )
                    if resource['lon_parsed'] and resource['lat_parsed']:
                        # 添加唯一标识
                        resource['uid'] = f"{resource['type']}_{resource['id']}"
                        # 添加主题关联信息
                        resource['theme_name'] = theme_name
                        resource['theme_goal'] = theme_info[0]['goal'] if theme_info else ""
                        all_resources.append(resource)

        # 去重
        unique_resources = []
        seen_uids = set()

        for resource in all_resources:
            if resource['uid'] not in seen_uids:
                seen_uids.add(resource['uid'])
                unique_resources.append(resource)

        print(f"  总计: {len(unique_resources)}个相关资源")

        return unique_resources

    def analyze_theme_resources(self, theme_id: str) -> Dict:
        """分析主题下的资源分布"""
        print(f"\n🔍 分析主题资源分布...")

        analysis = {
            'total_resources': 0,
            'by_type': {},
            'by_relation': {},
            'by_district': {},
            'has_coordinates': 0,
            'no_coordinates': 0
        }

        # 获取所有资源类型
        resource_types = ['CoreResource', 'IntangibleResource', 'TourismResource']

        for rtype in resource_types:
            # 统计直接关联
            direct_query = f"""
            MATCH (r:{rtype})-[:`关联主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            RETURN count(r) as count
            """

            # 统计通过活动关联
            indirect_query = f"""
            MATCH (r:{rtype})-[:`包含活动`]->(a:StudyActivity)-[:`适配主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            RETURN count(DISTINCT r) as count
            """

            # 统计适配主题关联
            theme_related_query = f"""
            MATCH (r:{rtype})-[:`适配主题`]->(th:StudyTheme {{theme_id: $theme_id}})
            RETURN count(DISTINCT r) as count
            """

            direct_result = self.db.execute_query(direct_query, {'theme_id': theme_id})
            indirect_result = self.db.execute_query(indirect_query, {'theme_id': theme_id})
            theme_related_result = self.db.execute_query(theme_related_query, {'theme_id': theme_id})

            direct_count = direct_result[0]['count'] if direct_result else 0
            indirect_count = indirect_result[0]['count'] if indirect_result else 0
            theme_related_count = theme_related_result[0]['count'] if theme_related_result else 0

            total_count = direct_count + indirect_count + theme_related_count

            if total_count > 0:
                analysis['by_type'][rtype] = total_count
                analysis['total_resources'] += total_count
        # 统计有坐标的资源
        coord_query = """
        MATCH (r)-[:`关联主题`]->(th:StudyTheme {theme_id: $theme_id})
        WHERE (r:CoreResource OR r:IntangibleResource OR r:TourismResource)
        RETURN 
            sum(CASE WHEN r.longitude IS NOT NULL AND r.latitude IS NOT NULL THEN 1 ELSE 0 END) as has_coords,
            sum(CASE WHEN r.longitude IS NULL OR r.latitude IS NULL THEN 1 ELSE 0 END) as no_coords
        """

        coord_result = self.db.execute_query(coord_query, {'theme_id': theme_id})
        if coord_result:
            analysis['has_coordinates'] = coord_result[0]['has_coords']
            analysis['no_coordinates'] = coord_result[0]['no_coords']

        print(f"  资源总数: {analysis['total_resources']}")
        print(f"  资源类型分布: {analysis['by_type']}")
        print(f"  有坐标资源: {analysis['has_coordinates']}个")
        print(f"  无坐标资源: {analysis['no_coordinates']}个")

        return analysis

    def parse_coordinates(self, coord_str: str) -> Tuple[Optional[float], Optional[float]]:
        """解析坐标字符串"""
        try:
            coords = str(coord_str).replace(' ', '').split(',')
            if len(coords) < 2:
                return None, None

            lon_str = coords[0].replace('°E', '').replace('°W', '')
            lat_str = coords[1].replace('°N', '').replace('°S', '')

            lon = float(lon_str)
            lat = float(lat_str)

            if 'W' in coords[0]:
                lon = -lon
            if 'S' in coords[1]:
                lat = -lat

            return lon, lat
        except:
            return None, None

    def haversine_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """Haversine距离计算"""
        EARTH_RADIUS_KM = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return EARTH_RADIUS_KM * c

    def get_distance_between_resources(self, resource1: Dict, resource2: Dict) -> float:
        """
        获取两个资源间的距离
        优先使用知识图谱中的邻近关系，其次计算
        """
        # 检查缓存
        cache_key1 = f"{resource1['uid']}_{resource2['uid']}"
        cache_key2 = f"{resource2['uid']}_{resource1['uid']}"

        if cache_key1 in self.distance_cache:
            return self.distance_cache[cache_key1]
        if cache_key2 in self.distance_cache:
            return self.distance_cache[cache_key2]

        # 1. 首先从知识图谱中查询邻近关系
        query = """
        MATCH (a)-[r:`邻近`]-(b)
        WHERE 
            ((a:CoreResource AND a.resource_id = $id1) OR
             (a:IntangibleResource AND a.resource_id = $id1) OR
             (a:TourismResource AND a.resource_id = $id1)) AND
            ((b:CoreResource AND b.resource_id = $id2) OR
             (b:IntangibleResource AND b.resource_id = $id2) OR
             (b:TourismResource AND b.resource_id = $id2))
        RETURN r.distance_km as distance
        LIMIT 1
        """

        results = self.db.execute_query(query, {
            'id1': resource1['id'],
            'id2': resource2['id']
        })

        if results and len(results) > 0:
            distance = float(results[0]['distance'])
            self.distance_cache[cache_key1] = distance
            return distance

        # 2. 如果没有邻近关系，直接计算距离
        if (resource1['lon_parsed'] and resource1['lat_parsed'] and
                resource2['lon_parsed'] and resource2['lat_parsed']):
            distance = self.haversine_distance(
                resource1['lat_parsed'], resource1['lon_parsed'],
                resource2['lat_parsed'], resource2['lon_parsed']
            )
        else:
            # 3. 如果没有坐标信息，使用默认距离
            distance = 10.0

        self.distance_cache[cache_key1] = distance
        return distance

    def build_distance_matrix(self, resources: List[Dict]) -> List[List[float]]:
        """
        构建资源间的距离矩阵
        返回二维矩阵
        """
        n = len(resources)
        print(f"构建 {n}×{n} 距离矩阵...")

        # 初始化矩阵
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 0.0
                else:
                    distance = self.get_distance_between_resources(resources[i], resources[j])
                    matrix[i][j] = round(distance, 2)

            # 进度显示
            if (i + 1) % 5 == 0 or i == n - 1:
                print(f"  进度: {i + 1}/{n}")

        return matrix

    def find_optimal_route_fixed_points(self, resources: List[Dict], start_index: int,
                                        num_points: int, algorithm: str = 'auto') -> Dict:
        """
        找到从起点开始的最优环路路线（固定点数）
        算法：基于最短路径优先 + 多样性优化
        """
        n = len(resources)
        if n < 2 or num_points < 2:
            return {'route': resources, 'total_distance': 0.0, 'algorithm': 'trivial'}

        # 限制最大点数
        num_points = min(num_points, n)

        # 构建距离矩阵
        distance_matrix = self.build_distance_matrix(resources)

        # 算法选择（去掉了最近邻算法）
        if algorithm == 'auto':
            if num_points <= 10:  # 放宽精确算法的点数限制
                algorithm = 'exact_tsp'  # 精确TSP算法
            else:
                algorithm = 'genetic_tsp'  # 遗传算法

        print(f"使用{algorithm}规划{num_points}个点的最优路线...")

        if algorithm == 'exact_tsp':
            result = self.find_optimal_route_exact(resources, distance_matrix, start_index, num_points)
        elif algorithm == 'genetic_tsp':
            result = self.find_optimal_route_genetic(resources, distance_matrix, start_index, num_points)
        else:
            # 如果指定了其他算法，默认使用精确TSP
            print(f"算法{algorithm}不可用，使用精确TSP算法")
            result = self.find_optimal_route_exact(resources, distance_matrix, start_index, num_points)

        return result

    def find_optimal_route_exact(self, resources: List[Dict], distance_matrix: List[List[float]],
                                 start_index: int, num_points: int) -> Dict:
        """
        精确TSP算法：穷举所有可能（点数少时使用）
        修改：根据组合数量动态选择评估路径数
        """
        n = len(resources)

        # 生成所有可能的组合
        other_indices = [i for i in range(n) if i != start_index]

        # 存储所有路径及其距离
        all_paths = []

        # 计算组合数
        total_combinations = math.comb(n - 1, num_points - 1) if n - 1 >= num_points - 1 else 0
        max_combinations = min(20000, total_combinations)  # 限制最大计算量

        print(f"精确TSP算法搜索最优路线（共{total_combinations}种组合，计算最多{max_combinations}种）...")

        # 使用组合生成器
        from itertools import combinations, permutations

        combination_count = 0
        path_count = 0

        for combo in combinations(other_indices, num_points - 1):
            combination_count += 1
            if combination_count > max_combinations:
                break

            # 生成所有可能的排列（TSP问题的经典解法）
            for perm in permutations(combo):
                # 创建完整的环路：起点 + 中间点 + 返回起点
                current_route_indices = [start_index] + list(perm) + [start_index]

                # 计算总距离（标准的TSP距离计算）
                total_distance = 0
                for i in range(len(current_route_indices) - 1):
                    idx1 = current_route_indices[i]
                    idx2 = current_route_indices[i + 1]
                    total_distance += distance_matrix[idx1][idx2]

                # 记录路径
                path_data = {
                    'indices': current_route_indices,
                    'distance': total_distance,
                    'resources': [resources[i] for i in current_route_indices[:-1]]
                }
                all_paths.append(path_data)

                path_count += 1

            # 进度显示
            if combination_count % 500 == 0:
                print(f"  已计算{combination_count}/{max_combinations}种组合，生成{path_count}条路径...")

        if not all_paths:
            print("未找到有效路径，使用遗传算法")
            return self.find_optimal_route_genetic(resources, distance_matrix, start_index, num_points)

        print(f"共生成{path_count}条候选路径，按距离排序...")

        # 按距离排序
        all_paths.sort(key=lambda x: x['distance'])

        # 动态选择评估路径数量
        if path_count > 20:
            eval_paths_count = 20
            print(f"路径总数{path_count}>20，筛选前20条最短路径进行评估...")
        else:
            eval_paths_count = min(10, path_count)  # 至少评估前10条或全部
            print(f"路径总数{path_count}≤20，筛选前{eval_paths_count}条最短路径进行评估...")

        top_paths = all_paths[:eval_paths_count]

        # 显示筛选出的路径
        print(f"\n 筛选出的前{eval_paths_count}条最短路径:")
        for i, path in enumerate(top_paths, 1):
            print(f"  第{i}名: 距离={path['distance']:.2f}km")

        # 对筛选出的路径进行科学评估
        print(f"\n 开始对前{eval_paths_count}条路径进行科学评估...")
        evaluated_paths = []

        # 需要主题信息进行科学评估（这里使用第一个资源的主题信息）
        theme = {
            'name': resources[0].get('theme_name', '未知主题'),
            'goal': resources[0].get('theme_goal', '')
        }

        for i, path in enumerate(top_paths, 1):
            print(f"\n · 评估第{i}条路径（距离={path['distance']:.2f}km）...")

            # 准备路径数据
            route_data = {
                'route': path['resources'],
                'total_distance': path['distance']
            }

            # 进行科学评估
            evaluation_report = self.evaluator.evaluate_route(route_data, theme)
            total_score = evaluation_report['comprehensive_assessment']['total_score']

            # 计算综合分数（距离分数 + 评估分数）
            distance_score = 100.0 / (1 + path['distance']) if path['distance'] > 0 else 100.0
            # 权重：评估分数70%，距离分数30%
            combined_score = total_score * 0.7 + distance_score * 0.3

            evaluated_paths.append({
                **path,
                'evaluation_report': evaluation_report,
                'total_score': total_score,
                'combined_score': combined_score,
                'distance_score': distance_score,
                'rank_by_distance': i  # 按距离的排名
            })

            print(f"    评估结果: 综合评分={total_score:.1f}/100, 综合分数={combined_score:.1f}")

        # 按综合分数排序，选择最佳路径
        evaluated_paths.sort(key=lambda x: x['combined_score'], reverse=True)
        best_path = evaluated_paths[0]

        print(f"\n 最佳路径选择结果:")
        print(f"  选择标准: 综合分数最高（评估分数70% + 距离分数30%）")
        print(f"  最佳路径原始距离排名: 第{best_path['rank_by_distance']}名")
        print(f"  最佳路径距离: {best_path['distance']:.2f}km")
        print(f"  最佳路径评估分数: {best_path['total_score']:.1f}/100")
        print(f"  最佳路径综合分数: {best_path['combined_score']:.1f}")

        # 生成路径选择详细信息
        top_paths_info = []
        for i, p in enumerate(evaluated_paths, 1):
            top_paths_info.append({
                'rank_by_score': i,  # 按综合分数排名
                'rank_by_distance': p['rank_by_distance'],  # 按距离排名
                'distance': round(p['distance'], 2),
                'total_score': p['total_score'],
                'combined_score': p['combined_score']
            })

        # 返回最佳路径
        return {
            'route': best_path['resources'],
            'total_distance': round(best_path['distance'], 2),
            'indices': best_path['indices'],
            'score': best_path['combined_score'],
            'algorithm': 'exact_tsp_with_dynamic_evaluation',
            'evaluation_report': best_path['evaluation_report'],
            'top_paths_info': top_paths_info,
            'total_paths_generated': path_count,
            'paths_evaluated': eval_paths_count,
            'selection_criteria': 'combined_score (evaluation_70% + distance_30%)'
        }

    def find_optimal_route_genetic(self, resources: List[Dict], distance_matrix: List[List[float]],
                                   start_index: int, num_points: int) -> Dict:
        """
        遗传算法TSP：近似最优解（点数多时使用）
        """
        n = len(resources)

        # 遗传算法TSP实现
        def create_tsp_individual():
            """创建TSP个体（随机路径）"""
            # 除了起点外的其他点
            other_indices = [i for i in range(n) if i != start_index]
            # 随机选择 num_points-1 个点
            selected = random.sample(other_indices, min(num_points - 1, len(other_indices)))
            # 随机排列（TSP的标准表示）
            random.shuffle(selected)
            # 加上起点和返回起点（形成环路）
            individual = [start_index] + selected + [start_index]
            return individual

        def calculate_tsp_fitness(individual):
            """计算TSP适应度（总距离的倒数）"""
            total_dist = 0
            for i in range(len(individual) - 1):
                total_dist += distance_matrix[individual[i]][individual[i + 1]]

            # 标准TSP适应度函数：距离越短适应度越高
            return 1.0 / (total_dist + 1)

        def tsp_crossover(parent1, parent2):
            """TSP顺序交叉（OX crossover）"""
            n_genes = len(parent1) - 1

            # 随机选择交叉点
            start, end = sorted(random.sample(range(1, n_genes - 1), 2))

            child = [-1] * n_genes

            # 复制父代1的片段
            child[start:end] = parent1[start:end]

            # 从父代2填充剩余位置（保持顺序）
            pos = 1
            for i in range(1, n_genes):
                if child[i] == -1:
                    while parent2[pos] in child or parent2[pos] == parent1[0]:
                        pos += 1
                        if pos >= n_genes:
                            pos = 1
                    child[i] = parent2[pos]

            child[0] = parent1[0]
            child.append(parent1[0])
            return child

        def tsp_mutate(individual):
            """TSP突变：交换或反转"""
            if random.random() < 0.1:
                n_genes = len(individual) - 1
                # 交换两个非起点位置
                i, j = random.sample(range(1, n_genes), 2)
                individual[i], individual[j] = individual[j], individual[i]
                individual[-1] = individual[0]
            return individual

        # 遗传算法参数
        population_size = 100
        generations = 200

        # 初始化种群
        population = [create_tsp_individual() for _ in range(population_size)]

        best_individual = None
        best_fitness = -1

        print(f"遗传算法TSP搜索最优路线（{generations}代）...")

        for gen in range(generations):
            # 计算适应度
            fitnesses = [calculate_tsp_fitness(ind) for ind in population]

            # 记录最佳个体
            current_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
            if fitnesses[current_best_idx] > best_fitness:
                best_fitness = fitnesses[current_best_idx]
                best_individual = population[current_best_idx].copy()

            # 选择（轮盘赌选择）
            selected = random.choices(
                population,
                weights=fitnesses,
                k=population_size
            )

            # 交叉和突变
            new_population = []
            for i in range(0, population_size, 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < population_size else selected[0]

                child1 = tsp_crossover(parent1, parent2)
                child2 = tsp_crossover(parent2, parent1)

                child1 = tsp_mutate(child1)
                child2 = tsp_mutate(child2)

                new_population.extend([child1, child2])

            population = new_population[:population_size]

            # 显示进度
            if gen % 40 == 0:
                total_dist = 1.0 / best_fitness - 1
                print(f"  代数 {gen}: 最佳距离 = {total_dist:.2f}km")

        # 计算最佳路径的总距离
        total_distance = 0
        for i in range(len(best_individual) - 1):
            total_distance += distance_matrix[best_individual[i]][best_individual[i + 1]]

        # 计算多样性分数
        route_resources = [resources[i] for i in best_individual[:-1]]
        diversity_score = self.calculate_diversity_score(route_resources)

        return {
            'route': route_resources,
            'total_distance': round(total_distance, 2),
            'indices': best_individual,
            'score': best_fitness,
            'algorithm': 'genetic_tsp'
        }

    def calculate_diversity_score(self, resources: List[Dict]) -> float:
        """计算资源多样性分数"""
        if len(resources) <= 1:
            return 0.0

        # 1. 类型多样性
        resource_types = set(res['type'] for res in resources)
        type_score = min(len(resource_types) * 30, 60)  # 最多60分

        # 2. 区域集中度
        districts = set(res.get('district', '') for res in resources)
        valid_districts = [d for d in districts if d and d != '未知']

        if len(valid_districts) == 1:
            region_score = 40  # 同一区域，主题集中
        elif len(valid_districts) == 2:
            region_score = 30  # 跨2个区域
        elif len(valid_districts) == 3:
            region_score = 20  # 跨3个区域
        else:
            region_score = 10  # 太分散

        return type_score + region_score

    def score_route(self, route_data: Dict, theme: Dict) -> Dict[str, float]:
        """
        使用科学评估器进行多维度路径评分
        """
        print(f"开始对路径进行科学评估...")

        # 使用科学评估器
        evaluation_report = self.evaluator.evaluate_route(route_data, theme)

        # 打印评估报告
        self.evaluator.print_assessment_report(evaluation_report, detailed=True)

        # 返回结构化评分结果
        scores = {
            'total_score': evaluation_report['comprehensive_assessment']['total_score'],
            'grade': evaluation_report['comprehensive_assessment']['grade'],
            'dimension_scores': {
                'content_quality': evaluation_report['dimension_details']['A']['total_score'],
                'resource_adaptation': evaluation_report['dimension_details']['B']['total_score'],
                'spatiotemporal': evaluation_report['dimension_details']['C']['total_score'],
                'practicality': evaluation_report['dimension_details']['D']['total_score']
            },
            'recommendations': evaluation_report.get('recommendations', []),
            'assessment_report': evaluation_report  # 包含完整评估报告
        }

        return scores

    def generate_optimal_route(self, resources: List[Dict], start_index: int,
                               num_points: int, algorithm: str = 'auto') -> Dict:
        """
        生成最优路线（固定点数）
        """
        print(f"使用TSP算法生成{num_points}个点的最优环路路线...")

        try:
            # 自动算法选择逻辑（简化版）
            if algorithm == 'auto':
                if num_points <= 10:
                    algorithm = 'exact_tsp'
                    print(f"点数{num_points}≤10，使用精确TSP算法")
                else:
                    algorithm = 'genetic_tsp'
                    print(f"点数{num_points}>10，使用遗传算法TSP")

            route = self.find_optimal_route_fixed_points(resources, start_index, num_points, algorithm)
            route['point_count'] = num_points

            # 算法显示名称
            algorithm_names = {
                'exact_tsp': '精确TSP算法',
                'genetic_tsp': '遗传算法TSP',
            }
            route['algorithm_name'] = algorithm_names.get(route.get('algorithm', ''), 'TSP算法')

            return route

        except Exception as e:
            print(f"生成路线失败: {e}")
            import traceback
            traceback.print_exc()
            return None


class InteractivePathPlanner:
    """交互式路径规划器"""

    def __init__(self, db_connection: Neo4jConnection):
        self.db = db_connection
        self.planner = TSPPathPlanner(db_connection)

    def run_interactive(self):
        """运行交互式路径规划"""
        print("=" * 70)
        print(" 研学路径智能规划系统")
        print("基于TSP算法 + 多维度评分")
        print("=" * 70)

        # 显示算法策略
        print(f"\n  系统算法策略:")
        print(f"  • 路线点数 ≤ 10：使用精确TSP算法（保证数学最优解）")
        print(f"  • 路线点数 > 10：使用遗传算法TSP（高效近似最优解）")
        print(f"  • 自动动态筛选：根据候选路径数量智能选择评估范围")
        print(f"  • 综合评分选择：评估分数70% + 距离分数30%")
        print()

        # 1. 显示所有研学主题
        print(" 可选的研学主题:")
        themes = self.planner.get_all_themes()

        for i, theme in enumerate(themes):
            print(f"  {i + 1}. {theme['name']}")
            print(f"     目标: {theme['goal']}")
            print(f"     建议时长: {theme['duration']}")
            print()

        # 2. 选择主题
        theme_choice = input(f"\n请选择研学主题 (1-{len(themes)}): ").strip()
        try:
            theme_index = int(theme_choice) - 1
            selected_theme = themes[theme_index]
            print(f"✓ 已选择主题: {selected_theme['name']}")
        except:
            print("⚠️ 选择无效，使用第一个主题")
            selected_theme = themes[0]

        # 3. 分析主题资源
        print(f"\n 正在分析'{selected_theme['name']}'主题资源...")
        resource_analysis = self.planner.analyze_theme_resources(selected_theme['theme_id'])

        if resource_analysis['total_resources'] == 0:
            print(f"⚠️  该主题下没有找到任何资源，请选择其他主题")
            return

        # 4. 获取主题下的所有资源
        print(f"\n 获取'{selected_theme['name']}'主题下的所有资源...")
        resources = self.planner.get_resources_by_theme(
            selected_theme['theme_id'],
            include_indirect=True
        )

        if len(resources) == 0:
            print(f"⚠️  该主题下没有找到有坐标信息的资源，无法规划路线")
            print(f"    提示: 请确保资源有经度(longitude)和纬度(latitude)信息")
            return

        print(f"找到 {len(resources)} 个有坐标的相关资源:")

        # 分组显示，便于查看
        resources_by_type = {}
        for resource in resources:
            rtype = resource['type']
            if rtype not in resources_by_type:
                resources_by_type[rtype] = []
            resources_by_type[rtype].append(resource)

        for rtype, type_resources in resources_by_type.items():
            print(f"\n{rtype} ({len(type_resources)}个):")
            for i, resource in enumerate(type_resources[:10]):  # 每个类型最多显示10个
                idx = i + 1
                district = resource.get('district', '未知')
                print(f"  {idx}. {resource['name'][:30]:<30} - {district}")
            if len(type_resources) > 10:
                print(f"    ... 还有{len(type_resources) - 10}个")

        # 5. 选择起点（只需要选择一个起点）
        print(f"\n📍 请选择路线起点 (只需选择1个):")
        print(f"  提示: 系统将从起点开始，使用TSP算法自动推荐最优环路路线")
        print(f"  当前主题: {selected_theme['name']}")
        print(f"  主题目标: {selected_theme['goal']}")

        # 显示所有资源供选择起点
        all_resources_display = []
        resource_index_map = {}  # 映射显示编号到实际索引

        idx = 1
        for rtype, type_resources in resources_by_type.items():
            for resource in type_resources:
                all_resources_display.append({
                    'display_idx': idx,
                    'resource': resource,
                    'type': rtype
                })
                resource_index_map[idx] = len(all_resources_display) - 1
                idx += 1

        # 分页显示
        page_size = 20
        total_pages = (len(all_resources_display) + page_size - 1) // page_size
        current_page = 0

        while True:
            start_idx = current_page * page_size
            end_idx = min((current_page + 1) * page_size, len(all_resources_display))

            print(f"\n📄 第 {current_page + 1}/{total_pages} 页:")
            for i in range(start_idx, end_idx):
                item = all_resources_display[i]
                resource = item['resource']
                print(f"  {item['display_idx']}. {resource['name'][:35]:<35} ({resource['type']})")
                print(f"       区域: {resource.get('district', '未知')}")

            if current_page > 0:
                print(f"\n  输入 'p' 查看上一页")
            if current_page < total_pages - 1:
                print(f"  输入 'n' 查看下一页")
            print(f"  输入资源编号选择起点")
            print(f"  输入 'r' 随机推荐起点")

            choice = input(f"\n请选择 (1-{len(all_resources_display)}): ").strip().lower()

            if choice == 'p' and current_page > 0:
                current_page -= 1
                continue
            elif choice == 'n' and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice == 'r':
                # 随机推荐
                import random
                start_idx = random.choice(list(resource_index_map.keys()))
                print(f" 随机推荐起点: {start_idx}")
                break
            else:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(all_resources_display):
                        start_idx = choice_num
                        break
                    else:
                        print("编号超出范围，请重新选择")
                except:
                    print("输入无效，请重新选择")

        # 获取起点资源
        start_resource_idx = resource_index_map[start_idx]
        start_resource = all_resources_display[start_resource_idx]['resource']

        # 在实际资源列表中找到起点的索引
        start_index_in_resources = -1
        for i, res in enumerate(resources):
            if res['uid'] == start_resource['uid']:
                start_index_in_resources = i
                break

        if start_index_in_resources == -1:
            print("错误：找不到起点资源")
            return

        print(f"\n✓ 已选择起点: {start_resource['name']}")
        print(f"  类型: {start_resource['type']}, 区域: {start_resource.get('district', '未知')}")

        # 6. 选择路线点数
        max_points = min(10, len(resources))
        print(f"\n 请选择路线点数:")
        print(f"  提示: 最少3个点，最多{max_points}个点")
        print(f"  建议: 3-4个点（半天），5-6个点（一天），7-8个点（一天半）")

        try:
            num_points = int(input(f"请输入点数 (3-{max_points}): "))
            num_points = min(max(3, num_points), max_points)
        except:
            num_points = min(6, len(resources))
            print(f"使用默认值: {num_points}个点")

        # 7. 算法策略说明
        print(f"\n  算法策略:")
        print(f"  系统将自动选择最优算法：")
        print(f"  • 路线点数 ≤ 10：使用精确TSP算法（保证最优解）")
        print(f"  • 路线点数 > 10：使用遗传算法TSP（近似最优解）")

        # 直接使用自动选择
        algorithm = 'auto'
        print("已启用自动算法选择")

        # 8. 生成最优路线
        print(f"\n🔧 正在使用TSP算法生成{num_points}个点的最优环路路线...")

        # 生成路线
        best_route = self.planner.generate_optimal_route(
            resources,
            start_index_in_resources,
            num_points=num_points,
            algorithm=algorithm
        )

        if not best_route:
            print("无法生成有效路线，请尝试其他起点或主题")
            return

        # 9. 显示路线详情
        self.display_best_route(best_route, selected_theme, start_resource)

        print(f"\n{'=' * 70}")
        print(" 路线规划完成!")
        print(f"{'=' * 70}")

    def display_best_route(self, best_route: Dict, theme: Dict, start_resource: Dict):
        """显示最佳路线详情 - 集成科学评估"""
        print(f"\n{'=' * 60}")
        print(f"  研学路线详情")
        print(f"{'=' * 60}")
        print(f"主题: {theme['name']}")
        print(f"主题目标: {theme['goal']}")
        print(f"起点: {start_resource['name']}")
        print(f"路线点数: {best_route['point_count']}个")
        print(f"路线总距离: {best_route['total_distance']}km")

        # 显示路径选择过程（如果存在）
        if best_route.get('top_paths_info'):
            total_paths = best_route.get('total_paths_generated', 0)
            eval_paths = best_route.get('paths_evaluated', 0)

            print(f"\n 路径选择过程:")
            print(f"  从{total_paths}条候选路径中，筛选出{eval_paths}条最短路径进行评估")
            print(f"  选择标准: {best_route.get('selection_criteria', '综合评分最高')}")

            # 显示最佳路径的排名信息
            if best_route.get('top_paths_info'):
                best_info = best_route['top_paths_info'][0]
                distance_rank = best_info.get('rank_by_distance', '未知')
                print(f"  最佳路径按距离排名: 第{distance_rank}名")

            # 显示前5名对比
            print(f"\n  前5名路径对比（按综合分数）:")
            for i, path_info in enumerate(best_route['top_paths_info'][:5], 1):
                rank_marker = "🥇" if i == 1 else f"{i}."
                distance_rank = path_info.get('rank_by_distance', '未知')
                print(f"  {rank_marker} 距离排名={distance_rank}, "
                      f"距离={path_info['distance']}km, "
                      f"评估={path_info['total_score']:.1f}, "
                      f"综合={path_info['combined_score']:.1f}")

        # 显示使用的算法
        algorithm_name = best_route.get('algorithm_name', 'TSP算法')
        point_count = best_route['point_count']

        print(f"\n  使用的算法: {algorithm_name}")
        if '精确' in algorithm_name:
            print(f"  算法说明: 路线点数{point_count}≤10，使用精确算法保证最优解")
        elif '遗传' in algorithm_name:
            print(f"  算法说明: 路线点数{point_count}>10，使用遗传算法高效搜索")

        # 如果已经有评估报告，直接使用
        if best_route.get('evaluation_report'):
            print(f"\n 科学评估结果:")
            self.planner.evaluator.print_assessment_report(
                best_route['evaluation_report'],
                detailed=True
            )
        else:
            # 否则执行科学评估
            print(f"\n 开始科学评估...")
            scores = self.planner.score_route(best_route, theme)

            print(f"\n 评估结果摘要")
            print(f"  综合评分: {scores['total_score']:.1f}/100")
            print(f"  评估等级: {scores['grade']}")

        # 显示路线顺序
        print(f"\n 路线顺序:")
        for i, resource in enumerate(best_route['route']):
            is_start = (resource['uid'] == start_resource['uid'])
            marker = "1." if is_start else f"{i + 1}."

            print(f"  {marker} {resource['name']}")
            print(f"     类型: {resource['type']}")
            print(f"     区域: {resource.get('district', '未知')}")

            duration_str = resource.get('duration', '60')
            try:
                duration = int(str(duration_str).strip().replace('分钟', '').replace('min', ''))
            except:
                duration = 60
            print(f"     建议时长: {duration}分钟")

            # 显示描述（如果有）
            if resource.get('description'):
                desc = resource['description'][:80]
                if len(resource['description']) > 80:
                    desc += "..."
                print(f"     简介: {desc}")

        # 路线统计数据
        print(f"\n 路线统计:")
        if len(best_route['route']) > 1:
            avg_distance = best_route['total_distance'] / len(best_route['route'])
            print(f"  平均每段距离: {avg_distance:.1f}km")

        # 资源类型分布
        type_counts = {}
        for res in best_route['route']:
            type_counts[res['type']] = type_counts.get(res['type'], 0) + 1

        print(f"  资源类型分布:")
        for res_type, count in type_counts.items():
            percentage = count / len(best_route['route']) * 100
            print(f"    {res_type}: {count}个 ({percentage:.0f}%)")

        # 区域分布
        districts = set(res.get('district', '') for res in best_route['route'])
        valid_districts = [d for d in districts if d and d != '未知']
        print(f"  涉及区域: {', '.join(valid_districts) if valid_districts else '未知'}")

        # 时间估算
        total_duration = 0
        for res in best_route['route']:
            duration_str = res.get('duration', '60')
            try:
                duration = int(str(duration_str).strip().replace('分钟', '').replace('min', ''))
            except:
                duration = 60
            total_duration += duration

        # 加上交通时间（假设每公里2分钟）
        travel_time = best_route['total_distance'] * 2  # 分钟
        total_time = total_duration + travel_time

        print(f"\n 时间估算:")
        print(f"    - 参观时间: {total_duration}分钟")
        print(f"    - 交通时间: {travel_time:.0f}分钟")
        print(f"    - 总计: {total_time:.0f}分钟 ({total_time / 60:.1f}小时)")

        # 显示改进建议
        recommendations = best_route.get('evaluation_report', {}).get('recommendations', [])
        if not recommendations and scores:
            recommendations = scores.get('recommendations', [])

        if recommendations:
            print(f"\n 改进建议:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec}")

    def assess_theme_relevance(self, route_resources: List[Dict], theme: Dict) -> Dict:
        """评估路线与主题的相关性"""
        relevance = {
            '资源数量': len(route_resources),
            '类型多样性': 0,
            '区域集中度': 0,
            '主题匹配度': '中等'
        }

        # 类型多样性
        resource_types = set(res['type'] for res in route_resources)
        relevance['类型多样性'] = len(resource_types)

        # 区域集中度
        districts = set(res.get('district', '') for res in route_resources)
        valid_districts = [d for d in districts if d and d != '未知']
        relevance['区域集中度'] = len(valid_districts)

        # 简单的主题匹配度评估
        if len(route_resources) >= 5 and relevance['类型多样性'] >= 2:
            relevance['主题匹配度'] = '高'
        elif len(route_resources) >= 3:
            relevance['主题匹配度'] = '中等'
        else:
            relevance['主题匹配度'] = '低'

        return relevance
