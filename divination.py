
# -*- coding: utf-8 -*-
"""
divination.py — 태을육임 점술 엔진 v2.0
점시(占時) 기반 실시간 포국 — 년/월/일/시 4중 포국
"""
from datetime import datetime, date
from taeul_core import TaeulEngine
from interpreter import Interpreter
from constants import (
    DIVINATION_CATEGORIES, DIVINATION_TIME_UNIT,
    GANJI60, JIJI, TAEUL_GUNG_NAME,
    TAEUL_JEONGGUNG_NUM, GUNG_DIRECTION,
    TAEUL_YANG_ORDER, TAEUL_YIN_ORDER,
)

class DivinationEngine:
    """태을육임 점술 엔진 — 점시 기반 실시간 분석"""

    def __init__(self, cheonbu_engine=None):
        """
        cheonbu_engine: 절기 연동용 (시계 양둔/음둔 판정)
        """
        self._cheonbu = cheonbu_engine

    def divine(self, category='general', target_time=None):
        """
        점술 실행.
        category: DIVINATION_CATEGORIES 키 중 하나
        target_time: datetime 객체 (None이면 현재 시각)
        반환: 4중 포국 결과 + 종합 해석
        """
        now = target_time or datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour

        cat_name = DIVINATION_CATEGORIES.get(category, '종합 운세')

        # 4중 포국: 각각 독립된 TaeulEngine으로 세계/월계/일계/시계 산출
        # 세계 (년 단위)
        te_year = TaeulEngine(date(year, month, day), hour, self._cheonbu)
        year_result = te_year.full_analysis(year)

        # 월계: 적년에 월 가중
        month_jeokyeon, _ = te_year.get_jeokyeon(year, month)
        month_guk = month_jeokyeon % 72
        if month_guk == 0: month_guk = 72
        month_ips = month_jeokyeon % 360
        if month_ips == 0: month_ips = 360

        # 일계: 적년에 일 가중
        day_jeokyeon, _ = te_year.get_jeokyeon(year, month, day)
        day_guk = day_jeokyeon % 72
        if day_guk == 0: day_guk = 72

        # 시계: 적년에 시 가중
        hour_jeokyeon, _ = te_year.get_jeokyeon(year, month, day, hour)
        hour_guk = hour_jeokyeon % 72
        if hour_guk == 0: hour_guk = 72

        # 시계 둔법 (절기 연동)
        hour_dunbeop = te_year.get_dunbeop(year, month, day, hour)

        # 4중 포국 재궁
        year_gung = year_result['jaegung']
        month_gung_idx = ((month_ips - 1) % 24) // 3
        from constants import TAEUL_YANG_ORDER, TAEUL_YIN_ORDER
        m_order = TAEUL_YANG_ORDER if 1 <= month_guk <= 36 else TAEUL_YIN_ORDER
        month_gung_num = m_order[month_gung_idx % 8]

        day_ips = day_jeokyeon % 360
        if day_ips == 0: day_ips = 360
        day_gung_idx = ((day_ips - 1) % 24) // 3
        d_order = TAEUL_YANG_ORDER if 1 <= day_guk <= 36 else TAEUL_YIN_ORDER
        day_gung_num = d_order[day_gung_idx % 8]

        hour_ips = hour_jeokyeon % 360
        if hour_ips == 0: hour_ips = 360
        hour_gung_idx = ((hour_ips - 1) % 24) // 3
        h_order = TAEUL_YANG_ORDER if hour_dunbeop == '陽遁' else TAEUL_YIN_ORDER
        hour_gung_num = h_order[hour_gung_idx % 8]

        # 승산 지수 (시계 기준 — 점술의 핵심)
        win_prob = year_result.get('win_probability', 50.0)

        # 해석
        report = Interpreter.generate_report(year_result)

        # 카테고리별 특화 해석
        cat_advice = self._category_advice(category, year_result, win_prob)

        return {
            'timestamp': now.isoformat(),
            'category': cat_name,
            'four_layer': {
                'year': {
                    'guk': year_result.get('guk'),
                    'gung': year_gung,
                    'gyeokguk': year_result.get('gyeokguk'),
                },
                'month': {
                    'guk': month_guk,
                    'gung_num': month_gung_num,
                    'gung_name': TAEUL_GUNG_NAME.get(month_gung_num, ('?',))[0],
                },
                'day': {
                    'guk': day_guk,
                    'gung_num': day_gung_num,
                    'gung_name': TAEUL_GUNG_NAME.get(day_gung_num, ('?',))[0],
                },
                'hour': {
                    'guk': hour_guk,
                    'gung_num': hour_gung_num,
                    'gung_name': TAEUL_GUNG_NAME.get(hour_gung_num, ('?',))[0],
                    'dunbeop': hour_dunbeop,
                },
            },
            'win_probability': win_prob,
            'report': report,
            'category_advice': cat_advice,
            'year_detail': year_result,
        }

    def _category_advice(self, category, result, win_prob):
        """카테고리별 특화 조언"""
        seungpae = result.get('seungpae', '和')
        gyeokguk = result.get('gyeokguk', {})
        gk_type = gyeokguk.get('type', '和') if isinstance(gyeokguk, dict) else '和'
        palmun = result.get('palmun', '休')

        advice_map = {
            'career': self._career_advice(seungpae, gk_type, win_prob),
            'love': self._love_advice(seungpae, gk_type, win_prob),
            'wealth': self._wealth_advice(seungpae, gk_type, win_prob, palmun),
            'lawsuit': self._lawsuit_advice(seungpae, gk_type, win_prob),
            'health': self._health_advice(result),
            'travel': self._travel_advice(result),
            'lost': self._lost_advice(result),
            'general': self._general_advice(seungpae, gk_type, win_prob),
        }
        return advice_map.get(category, advice_map['general'])

    @staticmethod
    def _career_advice(sp, gk, wp):
        if wp >= 65 and gk == '和':
            return '취업·승진에 매우 유리한 시기입니다. 적극적으로 지원하세요.'
        elif wp >= 50:
            return '기회는 있으나 경쟁이 있습니다. 준비를 철저히 하세요.'
        elif gk in ('囚', '格'):
            return '현 직장에서 갈등이 예상됩니다. 이직보다 내부 조율을 우선하세요.'
        else:
            return '당분간 현 위치에서 역량을 쌓는 것이 좋습니다.'

    @staticmethod
    def _love_advice(sp, gk, wp):
        if gk == '和' and wp >= 50:
            return '관계가 조화롭습니다. 진전을 위한 행동을 해도 좋습니다.'
        elif gk in ('廹', '擊'):
            return '감정적 충돌이 예상됩니다. 상대의 입장을 먼저 경청하세요.'
        elif sp == '客勝':
            return '상대방에게 주도권이 있습니다. 억지로 끌고 가지 마세요.'
        else:
            return '자연스러운 흐름에 맡기되, 진심을 전하는 것이 중요합니다.'

    @staticmethod
    def _wealth_advice(sp, gk, wp, palmun):
        if palmun in ('生', '開') and wp >= 60:
            return '재물운이 열려 있습니다. 투자·계약을 추진해도 좋습니다.'
        elif palmun in ('死', '傷'):
            return '자금 유출 위험이 있습니다. 보수적으로 운용하세요.'
        elif gk in ('囚', '提挾'):
            return '재정적으로 갇힌 상황입니다. 무리한 투자를 삼가세요.'
        else:
            return '중간 수준의 재물운입니다. 소규모 투자는 가능합니다.'

    @staticmethod
    def _lawsuit_advice(sp, gk, wp):
        if sp == '主勝' and wp >= 65:
            return '소송·경쟁에서 유리한 위치입니다. 적극 대응하세요.'
        elif sp == '客勝':
            return '상대방이 우세합니다. 화해 또는 중재를 고려하세요.'
        elif gk == '格':
            return '정면 충돌은 양패구상입니다. 우회 전략을 쓰세요.'
        else:
            return '결과를 단정짓기 어렵습니다. 전문가 조언을 구하세요.'

    @staticmethod
    def _health_advice(result):
        year_ganji = result.get('year_ganji', '甲子')
        health = Interpreter.interpret_health(
            year_ganji[0],
            result.get('jaegung', {}).get('ohaeng', '土') if isinstance(result.get('jaegung'), dict) else '土'
        )
        warnings = health.get('warnings', [])
        if warnings:
            first = warnings[0]
            return f"건강 주의: {first['desc']}. 과로를 삼가고 충분한 휴식을 취하세요."
        return '현재 건강운은 양호합니다. 규칙적인 생활을 유지하세요.'

    @staticmethod
    def _travel_advice(result):
        directions = Interpreter.recommend_direction(result)
        if directions:
            best = directions[0]
            return f"이동·출장에 유리한 방위: {best['direction']} ({best['meaning']})"
        return '특별히 유리한 방위가 없습니다. 일정을 유연하게 잡으세요.'

    @staticmethod
    def _lost_advice(result):
        cheonmok = result.get('cheonmok', '')
        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        if cm_gung:
            direction = GUNG_DIRECTION.get(cm_gung, '?')
            return f"분실물은 {direction} 방향을 탐색하세요. 문창(文昌) 방위가 단서입니다."
        return '방위 단서가 불명확합니다. 최근 동선을 역추적해 보세요.'

    @staticmethod
    def _general_advice(sp, gk, wp):
        interp = Interpreter.interpret_seungpae(sp)
        return interp['modern']