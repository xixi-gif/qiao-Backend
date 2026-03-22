import math
import random
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from itertools import combinations  # 必须导入这个
from app.api.db.neo4j_db import Neo4jConnection, neo4j_conn


class ScientificRouteEvaluator:
    """
    最新优化版 - 3维度科学评估器 (A/B/C)
    """

    def __init__(self):
        self.level1_weights = {'A': 0.40, 'B': 0.35, 'C': 0.25}
        self.level2_indicators = {
            'A': {'A1': {'name': '主题契合度', 'weight': 0.35}, 'A2': {'name': '教育价值度', 'weight': 0.20},
                  'A3': {'name': '文化传承性', 'weight': 0.20}, 'A4': {'name': '目标导向性', 'weight': 0.25}},
            'B': {'B1': {'name': '资源匹配度', 'weight': 0.40}, 'B2': {'name': '类型多样性', 'weight': 0.35},
                  'B3': {'name': '活动丰富度', 'weight': 0.25}},
            'C': {'C1': {'name': '空间紧凑度', 'weight': 0.45}, 'C2': {'name': '时间合理性', 'weight': 0.35},
                  'C3': {'name': '区域集中度', 'weight': 0.20}}
        }

    def evaluate_route(self, route_data: Dict, theme: Dict) -> Dict:
        route = route_data.get('route', [])
        total_distance = route_data.get('total_distance', 0)
        evaluation_results = {
            'A': self._evaluate_content_design(route, theme),
            'B': self._evaluate_resource_adaptation(route, theme),
            'C': self._evaluate_spatiotemporal_layout(route, total_distance),
        }
        comprehensive_result = self._calculate_comprehensive_result(evaluation_results)
        return self._generate_final_report(evaluation_results, comprehensive_result, route_data, theme)

    # --- 评分私有方法 (精简合并版) ---
    def _evaluate_content_design(self, route, theme):
        res = {
            'A1': {'score': self._calc_a1(route, theme), 'name': '主题契合度'},
            'A2': {'score': self._calc_a2(route), 'name': '教育价值度'},
            'A3': {'score': self._calc_a3(route), 'name': '文化传承性'},
            'A4': {'score': self._calc_a4(route, theme), 'name': '目标导向性'}
        }
        score = sum(res[k]['score'] * self.level2_indicators['A'][k]['weight'] for k in res)
        return {'total_score': round(score, 2), 'weighted_score': round(score * 0.4, 2), 'details': res}

    def _calc_a1(self, route, theme):
        w = [r.get('relevance_weight', 0.5) for r in route]
        avg = sum(w) / len(w) if w else 0
        return 92.0 if avg >= 0.85 else 85.0 if avg >= 0.7 else 78.0

    def _calc_a2(self, route):
        s = 70.0
        kw = {'博物馆': 5, '纪念馆': 5, '研学': 6, '非遗': 5}
        for r in route:
            t = f"{r.get('name', '')}{r.get('description', '')}"
            for k, v in kw.items():
                if k in t: s += v; break
        return min(s, 100.0)

    def _calc_a3(self, route):
        s = 70.0
        kw = {'潮汕': 5, '工夫茶': 5, '英歌': 7, '侨批': 8, '下南洋': 8}
        for r in route:
            t = f"{r.get('name', '')}{r.get('description', '')}"
            for k, v in kw.items():
                if k in t: s += v; break
        return min(s, 100.0)

    def _calc_a4(self, route, theme):
        goal = theme.get('goal', '')
        s = 75.0
        for r in route:
            t = f"{r.get('name', '')}{r.get('description', '')}"
            if any(k in t for k in ['非遗', '侨乡', '革命', '美食'] if k in goal): s += 5
        return min(s, 100.0)

    def _evaluate_resource_adaptation(self, route, theme):
        res = {
            'B1': {'score': self._calc_b1(route), 'name': '资源匹配度'},
            'B2': {'score': self._calc_b2(route), 'name': '类型多样性'},
            'B3': {'score': self._calc_b3(route), 'name': '活动丰富度'}
        }
        score = sum(res[k]['score'] * self.level2_indicators['B'][k]['weight'] for k in res)
        return {'total_score': round(score, 2), 'weighted_score': round(score * 0.35, 2), 'details': res}

    def _calc_b1(self, route):
        ratio = sum(1 for r in route if r.get('relevance_weight', 0) >= 0.9) / len(route) if route else 0
        return 98.0 if ratio >= 0.8 else 82.0 if ratio >= 0.4 else 70.0

    def _calc_b2(self, route):
        types = {r.get('type', '') for r in route}
        return 95.0 if len(types) >= 3 else 85.0 if len(types) == 2 else 75.0

    def _calc_b3(self, route):
        found = set()
        kw = {'讲解': 1, '体验': 1, '手作': 1, '参观': 1}
        for r in route:
            t = f"{r.get('name', '')}{r.get('description', '')}"
            for k in kw:
                if k in t: found.add(k)
        return 95.0 if len(found) >= 3 else 80.0 if len(found) >= 1 else 65.0

    def _evaluate_spatiotemporal_layout(self, route, total_distance):
        res = {
            'C1': {'score': self._calc_c1(route, total_distance), 'name': '空间紧凑度'},
            'C2': {'score': self._calc_c2(route, total_distance), 'name': '时间合理性'},
            'C3': {'score': self._calc_c3(route), 'name': '区域集中度'}
        }
        score = sum(res[k]['score'] * self.level2_indicators['C'][k]['weight'] for k in res)
        return {'total_score': round(score, 2), 'weighted_score': round(score * 0.25, 2), 'details': res}

    def _calc_c1(self, route, dist):
        if len(route) < 2: return 80.0
        avg = dist / (len(route) - 1)
        return 98.0 if avg <= 5 else 85.0 if avg <= 15 else 70.0

    def _calc_c2(self, route, dist):
        v_time = 0
        for r in route:
            try:
                v_time += int(str(r.get('duration', '60')).replace('分钟', ''))
            except:
                v_time += 60
        hrs = (v_time + dist * 2) / 60
        return 98.0 if 3 <= hrs <= 6 else 85.0 if 2 <= hrs <= 8 else 70.0

    def _calc_c3(self, route):
        dis = {r.get('district', '') for r in route if r.get('district')}
        return 98.0 if len(dis) <= 1 else 88.0 if len(dis) == 2 else 75.0

    def _calculate_comprehensive_result(self, results):
        total = sum(e['weighted_score'] for e in results.values())
        if total >= 82:
            grade, desc = '优秀', '路线设计优秀，完全符合标准'
        elif total >= 74:
            grade, desc = '良好', '路线质量良好，大部分指标符合要求'
        else:
            grade, desc = '中等', '路线基本合格，建议微调'
        return {'total_score': round(total, 2), 'grade': grade, 'grade_description': desc, 'recommendation': '推荐'}

    def _generate_final_report(self, results, comp, route_data, theme):
        return {
            'metadata': {'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'theme': theme.get('name'),
                         'route_points': len(route_data.get('route', [])),
                         'total_distance': route_data.get('total_distance', 0)},
            'comprehensive_assessment': comp,
            'dimension_details': results
        }


class TSPPathPlanner:
    def __init__(self, db_connection: Neo4jConnection = neo4j_conn):
        self.db = db_connection
        self.distance_cache = {}
        self.evaluator = ScientificRouteEvaluator()

    def get_all_themes(self):
        q = "MATCH (th:StudyTheme) RETURN th.theme_id as theme_id, th.name as name, th.study_goal as goal, th.suitable_duration as duration ORDER BY th.name"
        return [dict(record) for record in self.db.execute_query(q)]

    def get_resources_by_theme(self, theme_id: str):
        all_res = []
        theme_q = "MATCH (th:StudyTheme {theme_id: $theme_id}) RETURN th.name as theme_name, th.study_goal as goal"
        t_info = self.db.execute_query(theme_q, {'theme_id': theme_id})
        t_name = t_info[0]['theme_name'] if t_info else "未知"
        t_goal = t_info[0]['goal'] if t_info else ""

        for r_type in ['CoreResource', 'IntangibleResource', 'TourismResource']:
            # 这里的逻辑和负责人新代码完全一致：带权重抓取
            q = f"MATCH (r:{r_type})-[:`适配主题`]->(th:StudyTheme {{theme_id: $theme_id}}) RETURN r, 1.0 as w"
            for record in self.db.execute_query(q, {'theme_id': theme_id}):
                res = dict(record['r'])
                res.update(
                    {'type': r_type, 'relevance_weight': record['w'], 'theme_name': t_name, 'theme_goal': t_goal})
                self._parse_coords(res)
                all_res.append(res)

        unique = {}
        for r in all_res:
            uid = f"{r['type']}_{r['resource_id']}"
            if uid not in unique: r['uid'] = uid; unique[uid] = r
        return sorted(unique.values(), key=lambda x: x['relevance_weight'], reverse=True)

    def _parse_coords(self, res):
        try:
            res['lon_parsed'] = float(str(res.get('longitude', '0')).replace('°E', ''))
            res['lat_parsed'] = float(str(res.get('latitude', '0')).replace('°N', ''))
        except:
            res['lon_parsed'], res['lat_parsed'] = 0.0, 0.0

    def haversine_dist(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        p1, p2, d1, d2 = map(math.radians, [lat1, lat2, lat2 - lat1, lon2 - lon1])
        a = math.sin(d1 / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d2 / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _exact_tsp_dp(self, nodes, resources):
        n = len(nodes)
        dist = [[self.haversine_dist(resources[nodes[i]]['lat_parsed'], resources[nodes[i]]['lon_parsed'],
                                     resources[nodes[j]]['lat_parsed'], resources[nodes[j]]['lon_parsed']) for j in
                 range(n)] for i in range(n)]
        dp = [[float('inf')] * n for _ in range(1 << n)]
        parent = [[-1] * n for _ in range(1 << n)]
        dp[1][0] = 0
        for mask in range(1, 1 << n):
            for u in range(n):
                if not (mask & (1 << u)): continue
                for v in range(n):
                    if mask & (1 << v): continue
                    new_m, d = mask | (1 << v), dp[mask][u] + dist[u][v]
                    if d < dp[new_m][v]: dp[new_m][v], parent[new_m][v] = d, u
        best_d, last = float('inf'), -1
        for i in range(1, n):
            d = dp[(1 << n) - 1][i] + dist[i][0]
            if d < best_d: best_d, last = d, i
        path, curr, m = [], last, (1 << n) - 1
        while curr != -1:
            path.append(nodes[curr]);
            prev = parent[m][curr];
            m ^= (1 << curr);
            curr = prev
        return path[::-1], round(best_d, 2)

    def generate_optimal_route(self, resources, start_index, num_points):
        other = [i for i in range(len(resources)) if i != start_index]
        comb_list = list(combinations(other, min(num_points - 1, len(other))))
        if len(comb_list) > 100: comb_list = random.sample(comb_list, 100)

        candidates = []
        for combo in comb_list:
            path, d = self._exact_tsp_dp([start_index] + list(combo), resources)
            candidates.append({'route': [resources[i] for i in path], 'total_distance': d})

        candidates.sort(key=lambda x: x['total_distance'])
        top_20 = candidates[:20]
        theme = {'name': resources[0].get('theme_name'), 'goal': resources[0].get('theme_goal')}

        evaluated = []
        for p in top_20:
            report = self.evaluator.evaluate_route(p, theme)
            evaluated.append(
                {**p, 'evaluation_report': report, 'total_score': report['comprehensive_assessment']['total_score']})

        evaluated.sort(key=lambda x: x['total_score'], reverse=True)
        best = evaluated[0]
        best.update({'point_count': num_points, 'algorithm_name': 'TSP-DP组合优化'})
        return best