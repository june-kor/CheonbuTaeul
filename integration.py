# -*- coding: utf-8 -*-
"""
integration.py — 체용합일(體用合一) 교차분석 엔진 v2.1
천부경(體) + 태을신수(用) + 점술(占) + 건강(健) 통합
v2.1: 세국(世局) × 명국(命局) 이중 레이어 개인화
"""
from datetime import date
from cheonbu_core import CheonbuEngine
from taeul_core import TaeulEngine
from interpreter import Interpreter
from health_module import HealthModule
from constants import (
    GANJI60, CHEONGAN, JIJI, OHAENG_GAN, OHAENG_JI,
    SANG_SAENG, SANG_GEUK, GUGUNG, TAEUL_GUNG_NAME,
    NAEEUM_OHAENG, GYESIN_TABLE, GUA64_SEQUENCE,
)


class IntegrationEngine:
    """천부경(體) + 태을신수(用) + 건강(健) 통합 엔진 v2.1"""

    def __init__(self, name, birth_date, birth_hour, blood_type):
        self.name = name
        self.birth_date_str = birth_date
        self.cheonbu = CheonbuEngine(name, birth_date, birth_hour, blood_type)
        self.taeul = TaeulEngine(birth_date, birth_hour, cheonbu_engine=self.cheonbu)
        self.interpreter = Interpreter()

        # 생년 정보 추출
        if isinstance(birth_date, str):
            self.birth_year = int(birth_date.split('-')[0])
        else:
            self.birth_year = birth_date.year

        # 생년 간지·납음 산출
        self._init_birth_info()

    # ═══════════════════════════════════════
    # 생년 정보 초기화
    # ═══════════════════════════════════════

    def _init_birth_info(self):
        """생년 간지·납음오행·개인계신 산출"""
        idx = (self.birth_year - 4) % 60
        self.birth_gan = CHEONGAN[idx % 10]
        self.birth_ji = JIJI[idx % 12]
        self.birth_gz = GANJI60[idx]
        self.birth_naeum = NAEEUM_OHAENG.get(self.birth_gz, '土')
        self.personal_gyesin = GYESIN_TABLE.get(self.birth_ji, '寅')

    # ═══════════════════════════════════════
    # 천부경 래퍼 (기존 유지)
    # ═══════════════════════════════════════

    def _get_saju(self):
        fp = self.cheonbu.get_four_pillars()
        if isinstance(fp, dict):
            first_val = next(iter(fp.values()), None)
            if isinstance(first_val, dict):
                return {k: v.get('ganji', '??') for k, v in fp.items()}
            return fp
        return {'year': '甲子', 'month': '甲子', 'day': '甲子', 'hour': '甲子'}

    def _get_gugung(self):
        gp = self.cheonbu.get_gugung_position()
        if isinstance(gp, (list, tuple)):
            return gp[0] if gp else 5
        if isinstance(gp, int):
            return gp
        if isinstance(gp, dict):
            return gp.get('number', gp.get('position', 5))
        return 5

    # ═══════════════════════════════════════
    # 세국 × 명국 이중 레이어 (v2.1 핵심 신규)
    # ═══════════════════════════════════════

    def _get_segye(self, target_year):
        """세국(世局): 당해 연도 포국 — 모든 사람 공통"""
        return self.taeul.full_analysis(target_year)

    def _get_myeong(self):
        """명국(命局): 생년 포국 — 개인별 고유"""
        return self.taeul.full_analysis(self.birth_year)

    def _extract_gung_ohaeng(self, taeul_result):
        """태을 결과에서 재궁 오행 추출"""
        jaegung = taeul_result.get('jaegung', {})
        if isinstance(jaegung, dict):
            return jaegung.get('ohaeng', '土')
        return '土'

    def _extract_gung_num(self, taeul_result):
        """태을 결과에서 재궁 번호 추출"""
        jaegung = taeul_result.get('jaegung', {})
        if isinstance(jaegung, dict):
            return jaegung.get('gung_num', 5)
        return 5

    def _extract_gyeokguk_type(self, taeul_result):
        """태을 결과에서 격국 유형 추출"""
        gyeokguk = taeul_result.get('gyeokguk', {})
        if isinstance(gyeokguk, dict):
            return gyeokguk.get('type', '和')
        return '和'

    def _ohaeng_relation(self, oh_a, oh_b):
        """두 오행 사이의 관계 판정"""
        if oh_a == oh_b:
            return '比和', 6
        elif SANG_SAENG.get(oh_b) == oh_a:
            return '生我', 12
        elif SANG_SAENG.get(oh_a) == oh_b:
            return '我生', 8
        elif SANG_GEUK.get(oh_b) == oh_a:
            return '剋我', -8
        elif SANG_GEUK.get(oh_a) == oh_b:
            return '我剋', 2
        return '無關', 0

    def _cross_segye_myeong(self, se, my):
        """세국 × 명국 교차 점수 산출"""
        score = 0

        # 1) 세궁 오행 vs 명궁 오행
        se_oh = self._extract_gung_ohaeng(se)
        my_oh = self._extract_gung_ohaeng(my)
        rel1, pts1 = self._ohaeng_relation(my_oh, se_oh)
        score += pts1

        # 2) 납음오행 vs 세궁 오행
        rel2, pts2 = self._ohaeng_relation(self.birth_naeum, se_oh)
        score += pts2

        # 3) 격국 교차 보정
        se_gk = self._extract_gyeokguk_type(se)
        my_gk = self._extract_gyeokguk_type(my)
        if se_gk == '和' and my_gk == '和':
            score += 10
        elif se_gk == '和' or my_gk == '和':
            score += 5
        elif se_gk in ('囚', '格', '四郭固') or my_gk in ('囚', '格', '四郭固'):
            score -= 5
        elif se_gk in ('掩', '提挾') or my_gk in ('掩', '提挾'):
            score -= 3

        return score, rel1, rel2

    def _personalized_win_prob(self, se, my, cross_adj):
        """세국 주객산 + 명국 주객산 + 교차보정 → 개인화 승산지수"""
        se_ju = se.get('jusan', 19)
        se_gaek = se.get('gaeksan', 7)
        my_ju = my.get('jusan', 19)
        my_gaek = my.get('gaeksan', 7)

        # 가중 합산: 세국 60% + 명국 40%
        total_ju = se_ju * 0.6 + my_ju * 0.4
        total_gaek = se_gaek * 0.6 + my_gaek * 0.4
        total = total_ju + total_gaek
        if total == 0:
            total = 1

        base_wp = (total_ju / total) * 100
        adj = max(-15, min(15, cross_adj * 0.5))
        wp = max(5, min(95, base_wp + adj))
        return round(wp, 1)

    def _personalized_gyeokguk(self, se, my):
        """세국 격국 + 명국 격국 → 최종 개인 격국"""
        se_g = self._extract_gyeokguk_type(se)
        my_g = self._extract_gyeokguk_type(my)

        if se_g == my_g:
            return se_g

        priority = ['四郭固', '提挾', '囚', '掩', '格', '擊', '廹', '關', '和']
        for g in priority:
            if se_g == g or my_g == g:
                return g
        return se_g

    def _flow_year_gua(self, target_year):
        """유년괘: 생년 기반 + 당해 나이 → 64괘"""
        birth_base = ((self.birth_year - 4) % 60) + 1
        age = target_year - self.birth_year + 1
        gua_idx = (birth_base + age) % 64
        if gua_idx == 0:
            gua_idx = 64
        return GUA64_SEQUENCE[gua_idx - 1]

    # ═══════════════════════════════════════
    # 기존 교차 분석 (하위호환 유지)
    # ═══════════════════════════════════════

    def cross_gugung(self, target_year=None):
        cb_gung = self._get_gugung()
        taeul_detail = self.taeul.get_taeul_jaegung_detail(target_year)
        taeul_gung = taeul_detail['gung_num']
        hap = (cb_gung + taeul_gung) % 9
        if hap == 0: hap = 9
        hap_info = GUGUNG.get(hap, ('?','?','?','?'))
        return {
            'cheonbu_gung': cb_gung, 'cheonbu_name': GUGUNG.get(cb_gung, ('?',))[0],
            'taeul_gung': taeul_gung, 'taeul_name': taeul_detail['gwe_name'],
            'hap_gung': hap, 'hap_name': hap_info[0],
        }

    def cross_ohaeng(self, target_year=None):
        saju = self._get_saju()
        year_gan = saju.get('year', '甲子')[0]
        cb_oh = OHAENG_GAN.get(year_gan, '土')
        taeul_detail = self.taeul.get_taeul_jaegung_detail(target_year)
        taeul_oh = taeul_detail['ohaeng']
        if cb_oh == taeul_oh:                       relation = '比和'
        elif SANG_SAENG.get(cb_oh) == taeul_oh:     relation = '我→生他'
        elif SANG_SAENG.get(taeul_oh) == cb_oh:     relation = '他→生我'
        elif SANG_GEUK.get(cb_oh) == taeul_oh:      relation = '我→剋他'
        elif SANG_GEUK.get(taeul_oh) == cb_oh:      relation = '他→剋我'
        else:                                        relation = '無關'
        return {'cheonbu_ohaeng': cb_oh, 'taeul_ohaeng': taeul_oh, 'relation': relation}

    def cross_verdict(self, target_year=None):
        cb_score = self.cheonbu.calculate_score()
        taeul_score = self.taeul.calculate_score(target_year)
        cb_good = cb_score >= 20
        taeul_good = taeul_score >= 20
        if cb_good and taeul_good:       return '體吉用吉', '안팎 모두 순조 — 적극 추진기'
        elif cb_good and not taeul_good: return '體吉用凶', '내면은 좋으나 외부 환경 주의 — 신중기'
        elif not cb_good and taeul_good: return '體凶用吉', '외부는 좋으나 내면 보강 필요 — 내적 성찰기'
        else:                            return '體凶用凶', '안팎 모두 어려움 — 인내와 수양기'

    # ═══════════════════════════════════════
    # 점수 (v2.1: 교차점수에 세명교차 반영)
    # ═══════════════════════════════════════

    def calculate_cross_score(self, target_year=None):
        score = 0
        cg = self.cross_gugung(target_year)
        hap_info = GUGUNG.get(cg['hap_gung'], ('?','?','中','?'))
        score += {'吉':6, '中':3, '凶':1}.get(hap_info[2], 3)
        co = self.cross_ohaeng(target_year)
        oh_scores = {'比和':6, '他→生我':8, '我→生他':5, '他→剋我':1, '我→剋他':3, '無關':4}
        score += oh_scores.get(co['relation'], 3)
        verdict, _ = self.cross_verdict(target_year)
        v_scores = {'體吉用吉':6, '體吉用凶':3, '體凶用吉':3, '體凶用凶':0}
        score += v_scores.get(verdict, 2)
        return min(score, 20)

    def calculate_total_score(self, target_year=None):
        cb = self.cheonbu.calculate_score()
        taeul = self.taeul.calculate_score(target_year)
        cross = self.calculate_cross_score(target_year)
        return {'cheonbu': cb, 'taeul': taeul, 'cross': cross, 'total': cb + taeul + cross}

    def get_total_verdict(self, total_score):
        if total_score >= 80:   return '大吉'
        elif total_score >= 65: return '吉'
        elif total_score >= 50: return '小吉'
        elif total_score >= 35: return '평'
        elif total_score >= 20: return '凶'
        else:                   return '大凶'

    # ═══════════════════════════════════════
    # 건강분석 (기존 유지)
    # ═══════════════════════════════════════

    def get_health_analysis(self, target_year=None):
        saju = self._get_saju()
        year_ganji = saju.get('year', '甲子')
        taeul_detail = self.taeul.get_taeul_jaegung_detail(target_year)
        hm = HealthModule(
            year_gan=year_ganji[0],
            year_ji=year_ganji[1],
            taeul_ohaeng=taeul_detail['ohaeng'],
            birth_hour=self.cheonbu.birth_hour,
        )
        return hm.full_health_report()

    # ═══════════════════════════════════════
    # 비즈니스 리포트 (기존 유지)
    # ═══════════════════════════════════════

    def get_business_report(self, target_year=None, tone='executive'):
        taeul_result = self.taeul.full_analysis(target_year)
        return Interpreter.generate_report(taeul_result, tone)

    # ═══════════════════════════════════════
    # 10년 예측 (v2.1: 개인화 반영)
    # ═══════════════════════════════════════

    def forecast(self, start_year=None, span=10):
        if start_year is None: start_year = date.today().year
        my = self._get_myeong()  # 명국은 한 번만 산출

        results = []
        for yr in range(start_year, start_year + span):
            se = self._get_segye(yr)

            # 개인화 교차
            cross_adj, _, _ = self._cross_segye_myeong(se, my)
            p_wp = self._personalized_win_prob(se, my, cross_adj)
            p_gk = self._personalized_gyeokguk(se, my)
            flow_gua = self._flow_year_gua(yr)

            taeul_detail = se.get('jaegung', {})
            palmun = se.get('palmun', '?')
            palmun_gil = se.get('palmun_gil', '?')
            eumyangsu = se.get('eumyangsu', {})
            yeon_gwae = se.get('yeon_gwae', {})

            # 개인화된 점수
            cb = self.cheonbu.calculate_score()
            t_score = se.get('score', 19)
            c_base = max(0, min(20, 10 + int(cross_adj * 0.3)))
            total = min(cb + t_score + c_base, 100)

            if p_wp >= 66:     grade = '吉'
            elif p_wp >= 55:   grade = '小吉'
            elif p_wp >= 45:   grade = '평'
            elif p_wp >= 35:   grade = '小凶'
            else:              grade = '凶'

            results.append({
                'year': yr,
                'ganji': self.taeul._get_year_ganji(yr),
                'taeul_gung': f"{taeul_detail.get('gwe_name','?')}({taeul_detail.get('ohaeng','?')})",
                'gyeokguk': p_gk,
                'palmun': palmun,
                'eumyangsu': eumyangsu.get('label', '?') if isinstance(eumyangsu, dict) else '?',
                'gwae': flow_gua,
                'score': total,
                'verdict': grade,
                'wp': p_wp,
            })
        return results

    # ═══════════════════════════════════════
    # 전체 분석 (v2.1: 이중 레이어 통합)
    # ═══════════════════════════════════════

    def full_analysis(self, target_year=None):
        y = target_year or date.today().year
        saju = self._get_saju()

        # ① 세국 (天道 — 당해)
        se = self._get_segye(y)

        # ② 명국 (人道 — 생년)
        my = self._get_myeong()

        # ③ 천부경 분석
        cb_analysis = {
            'saju': saju,
            'saju_text': self.cheonbu.get_saju_text(),
            'jeolgi': self.cheonbu.get_jeolgi_dates(),
            'score': self.cheonbu.calculate_score(),
        }

        # ④ 세국×명국 교차
        cross_adj, rel_gung, rel_naeum = self._cross_segye_myeong(se, my)

        # ⑤ 개인화된 결과
        p_wp = self._personalized_win_prob(se, my, cross_adj)
        p_gk = self._personalized_gyeokguk(se, my)
        flow_gua = self._flow_year_gua(y)

        # ⑥ 기존 교차 (하위호환)
        cross = {
            'gugung': self.cross_gugung(y),
            'ohaeng': self.cross_ohaeng(y),
            'verdict': self.cross_verdict(y),
            'score': self.calculate_cross_score(y),
        }

        # ⑦ 개인화된 종합점수
        cb_score = cb_analysis['score']
        se_score = se.get('score', 19)
        c_base = max(0, min(20, 10 + int(cross_adj * 0.3)))
        total = min(cb_score + se_score + c_base, 100)

        if p_wp >= 66:     p_grade = '吉'
        elif p_wp >= 55:   p_grade = '小吉'
        elif p_wp >= 45:   p_grade = '평'
        elif p_wp >= 35:   p_grade = '小凶'
        else:              p_grade = '凶'

        scores = {
            'cheonbu': cb_score,
            'taeul': se_score,
            'cross': c_base,
            'total': total,
        }
        verdict = self.get_total_verdict(total)

        # ⑧ 10년 예측 (개인화)
        forecast = self.forecast(y, 10)

        # ⑨ 건강
        health = self.get_health_analysis(y)

        # ⑩ 비즈니스
        business = self.get_business_report(y)

        return {
            'name': self.name,
            'birth_date': self.cheonbu.birth_date,
            'birth_hour': self.cheonbu.birth_hour,
            'blood_type': self.cheonbu.blood_type,
            # 천부경
            'cheonbu': cb_analysis,
            # 세국 (taeul 키로 하위호환)
            'taeul': se,
            # 명국 (신규)
            'myeong': my,
            # 개인화 정보 (신규)
            'personal': {
                'birth_gz': self.birth_gz,
                'birth_naeum': self.birth_naeum,
                'personal_gyesin': self.personal_gyesin,
                'cross_adj': cross_adj,
                'rel_gung': rel_gung,
                'rel_naeum': rel_naeum,
                'personal_wp': p_wp,
                'personal_gyeok': p_gk,
                'personal_grade': p_grade,
                'flow_gua': flow_gua,
            },
            # 교차
            'cross': cross,
            # 점수
            'scores': scores,
            'verdict': verdict,
            # 예측
            'forecast': forecast,
            # 건강
            'health': health,
            # 비즈니스
            'business_report': business,
        }