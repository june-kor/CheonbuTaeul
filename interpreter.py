# -*- coding: utf-8 -*-
"""
interpreter.py — 해석 엔진 v2.0
격국→일상어 변환, 비즈니스 태스크 매핑, 건강 해석, 승산 지수 해석
"""
from constants import (
    BUSINESS_TASK_MAP, GYEOKGUK_TASK_MAP, PALMUN_ZONE,
    WIN_PROBABILITY_GRADE, GUNG_DIRECTION, MUNCHANG_DIRECTION_MEANING,
    REPORT_TONE, DIVINATION_CATEGORIES,
    TAEUL_GUNG_NAME, TAEUL_JEONGGUNG_NUM,
    OHAENG_GAN, OJANG_OHAENG, SAMHON, SAMRYEONG, SAMSIN,
    BONSHIM_TAEYANG, SANSAM_CHEONGAN_JANGBU,
    PALMUN_GIL, PALMUN_GUNG,
)


class Interpreter:
    """태을신수 결과를 현대적 언어로 해석"""

    # ═══════════════════════════════════════
    # A. 격국 → 현대 일상어
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_gyeokguk(gyeokguk_type):
        """
        격국 유형 → 현대적 해석 딕셔너리
        반환: {'task', 'action', 'modern', 'grade'}
        """
        info = GYEOKGUK_TASK_MAP.get(gyeokguk_type, {})
        if not info:
            return {
                'task': '판정 불능',
                'action': '추가 분석 필요',
                'modern': '현재 상황을 단정짓기 어렵습니다.',
                'grade': '中',
            }
        return {
            'task': info['task'],
            'action': info['action'],
            'modern': info['modern'],
            'grade': info.get('grade', '中'),
        }

    # ═══════════════════════════════════════
    # B. 승패 → 비즈니스 태스크
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_seungpae(seungpae_result):
        """
        '主勝'/'客勝'/'和' → 비즈니스 태스크·액티비티
        """
        info = BUSINESS_TASK_MAP.get(seungpae_result, BUSINESS_TASK_MAP['和'])
        return {
            'task': info['task'],
            'activities': info['activity'],
            'action': info['action'],
            'modern': info['modern'],
        }

    # ═══════════════════════════════════════
    # C. 승산 지수 해석
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_win_probability(win_prob):
        """승산 지수(%) → 등급·판정·권고"""
        for (lo, hi), (label, grade, advice) in WIN_PROBABILITY_GRADE.items():
            if lo <= win_prob <= hi:
                return {
                    'probability': win_prob,
                    'label': label,
                    'grade': grade,
                    'advice': advice,
                }
        return {
            'probability': win_prob,
            'label': '판정 불능',
            'grade': '中',
            'advice': '추가 분석 필요',
        }

    # ═══════════════════════════════════════
    # D. 팔문 방위 존 해석
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_palmun_zone():
        """팔문 8개 전체의 존(Blue/Red/Yellow/Gray) 분류"""
        zones = {'Blue': [], 'Red': [], 'Yellow': [], 'Gray': []}
        for mun, (zone, desc) in PALMUN_ZONE.items():
            gung_num = PALMUN_GUNG.get(mun)
            direction = GUNG_DIRECTION.get(gung_num, '?')
            zones[zone].append({
                'mun': mun,
                'gung': gung_num,
                'direction': direction,
                'description': desc,
                'gilhyung': PALMUN_GIL.get(mun, '?'),
            })
        return zones

    # ═══════════════════════════════════════
    # E. 전략 방위 추천
    # ═══════════════════════════════════════

    @staticmethod
    def recommend_direction(taeul_result):
        """
        태을 결과에서 최적 방위 추천.
        1순위: 문창(文昌) 방위 — 기획·문서·계약
        2순위: 생문·개문·휴문 방위 — 투자·확장
        3순위: 태을 재궁 방위 — 군왕의 기운
        """
        recommendations = []

        # 문창 방위
        cheonmok = taeul_result.get('cheonmok', '')
        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        if cm_gung:
            direction = GUNG_DIRECTION.get(cm_gung, '?')
            recommendations.append({
                'priority': 1,
                'type': '文昌方位',
                'direction': direction,
                'gung': cm_gung,
                'meaning': MUNCHANG_DIRECTION_MEANING,
            })

        # 길문 방위 (생·개·휴)
        for mun in ['生', '開', '休']:
            gung = PALMUN_GUNG.get(mun)
            if gung:
                direction = GUNG_DIRECTION.get(gung, '?')
                zone_info = PALMUN_ZONE.get(mun, ('Blue', ''))
                recommendations.append({
                    'priority': 2,
                    'type': f'{mun}門方位',
                    'direction': direction,
                    'gung': gung,
                    'meaning': zone_info[1],
                })

        # 태을 재궁 방위
        jaegung = taeul_result.get('jaegung', {})
        jg_num = jaegung.get('gung_num') if isinstance(jaegung, dict) else None
        if jg_num:
            direction = GUNG_DIRECTION.get(jg_num, '?')
            recommendations.append({
                'priority': 3,
                'type': '太乙方位',
                'direction': direction,
                'gung': jg_num,
                'meaning': '군왕의 기운이 머무는 방위',
            })

        return sorted(recommendations, key=lambda x: x['priority'])

    # ═══════════════════════════════════════
    # F. 건강 해석 (삼혼·오장 기반)
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_health(year_gan, taeul_ohaeng):
        """
        년간 오행 + 태을재궁 오행 → 건강 주의 장부·정서 해석
        """
        gan_oh = OHAENG_GAN.get(year_gan, '土')

        # 주의 장부: 상극 받는 오행의 장부
        # 예: 년간=木이면 木이 극하는 土(脾)가 과활성, 金이 극하는 木(肝)이 피극
        warnings = []

        # 내가 극하는 장부 (과잉 주의)
        from constants import SANG_GEUK
        target_oh = SANG_GEUK.get(gan_oh)
        if target_oh:
            for jang, info in OJANG_OHAENG.items():
                if info['오행'] == target_oh:
                    warnings.append({
                        'type': '과잉주의',
                        'organ': jang,
                        'bu': info['부'],
                        'ohaeng': target_oh,
                        'emotion': info['정서'],
                        'desc': f"{gan_oh}이 {target_oh}을 극하므로 {jang}({info['부']}) 과잉 활성 주의",
                    })

        # 나를 극하는 오행의 장부 (약화 주의)
        for oh, target in SANG_GEUK.items():
            if target == gan_oh:
                for jang, info in OJANG_OHAENG.items():
                    if info['오행'] == gan_oh:
                        warnings.append({
                            'type': '약화주의',
                            'organ': jang,
                            'bu': info['부'],
                            'ohaeng': gan_oh,
                            'emotion': info['정서'],
                            'desc': f"{oh}이 {gan_oh}을 극하므로 {jang}({info['부']}) 기능 약화 주의",
                        })
                break

        # 태을재궁 오행과 년간 오행 관계
        if taeul_ohaeng == gan_oh:
            overall = '비화(比和) — 체질과 시운이 같아 안정적이나 편중 주의'
        elif SANG_GEUK.get(taeul_ohaeng) == gan_oh:
            overall = f'시운({taeul_ohaeng})이 체질({gan_oh})을 극함 — 건강 관리 필수'
        elif SANG_GEUK.get(gan_oh) == taeul_ohaeng:
            overall = f'체질({gan_oh})이 시운({taeul_ohaeng})을 극함 — 과로 주의'
        else:
            overall = '상생 관계 — 비교적 건강 양호'

        # 본심본태양 참조
        heart_info = BONSHIM_TAEYANG['人心']

        return {
            'year_gan_ohaeng': gan_oh,
            'taeul_ohaeng': taeul_ohaeng,
            'overall': overall,
            'warnings': warnings,
            'heart_note': f"심장({heart_info['오행']})은 태양의 기운 — {heart_info['기능']}",
        }

    # ═══════════════════════════════════════
    # G. 약리학 참조 (산삼 생장년도 해석)
    # ═══════════════════════════════════════

    @staticmethod
    def interpret_sansam(year_gan):
        """년간에 따른 산삼 약리 대응 장부"""
        info = SANSAM_CHEONGAN_JANGBU.get(year_gan)
        if not info:
            return None
        jang, bu, oh, desc = info
        return {
            'year_gan': year_gan,
            'organ': jang,
            'bu': bu,
            'ohaeng': oh,
            'description': desc,
        }

    # ═══════════════════════════════════════
    # H. 종합 리포트 생성
    # ═══════════════════════════════════════

    @staticmethod
    def generate_report(taeul_result, tone='executive'):
        """
        태을 결과 → 종합 리포트 딕셔너리
        tone: 'executive' (차분·분석적) / 'casual' (친근·쉬운)
        """
        tone_info = REPORT_TONE.get(tone, REPORT_TONE['executive'])

        # 승패 해석
        seungpae = taeul_result.get('seungpae', '和')
        sp_interp = Interpreter.interpret_seungpae(seungpae)

        # 격국 해석
        gyeokguk = taeul_result.get('gyeokguk', {})
        gk_type = gyeokguk.get('type', '和') if isinstance(gyeokguk, dict) else '和'
        gk_interp = Interpreter.interpret_gyeokguk(gk_type)

        # 승산 지수
        win_prob = taeul_result.get('win_probability', 50.0)
        wp_interp = Interpreter.interpret_win_probability(win_prob)

        # 방위 추천
        directions = Interpreter.recommend_direction(taeul_result)

        # 건강 해석
        year_ganji = taeul_result.get('year_ganji', '甲子')
        year_gan = year_ganji[0]
        jaegung = taeul_result.get('jaegung', {})
        taeul_oh = jaegung.get('ohaeng', '土') if isinstance(jaegung, dict) else '土'
        health = Interpreter.interpret_health(year_gan, taeul_oh)

        # 리스크 팩터
        risk_factors = []
        if gk_type in ('囚', '格', '掩', '提挾', '四郭固'):
            risk_factors.append(f"격국 '{gk_type}' 발생 — {gk_interp['action']}")
        yang9yin6 = taeul_result.get('yang9_yin6', {})
        if yang9yin6:
            y9s = yang9yin6.get('yang9_small', {})
            y6s = yang9yin6.get('yin6_small', {})
            if y9s.get('warning'):
                risk_factors.append('양9 소주기 경고 구간 — 대규모 변동 주의')
            if y6s.get('warning'):
                risk_factors.append('음6 소주기 경고 구간 — 지속적 침체 주의')

        return {
            'tone': tone_info,
            'current_task': sp_interp['task'],
            'activities': sp_interp['activities'],
            'win_probability': wp_interp,
            'gyeokguk_interp': gk_interp,
            'directions': directions,
            'health': health,
            'risk_factors': risk_factors,
            'executive_summary': _build_summary(sp_interp, gk_interp, wp_interp, tone_info),
        }

def _build_summary(sp, gk, wp, tone):
    """Executive Summary 문장 생성"""
    prefix = tone['prefix']
    suffix = tone['suffix']

    if wp['grade'] in ('大吉', '吉'):
        mood = '긍정적'
    elif wp['grade'] in ('凶', '大凶'):
        mood = '신중을 요하는'
    else:
        mood = '균형 잡힌'

    # 조사 처리: 받침 유무에 따라 '이/가' 자동 선택
    action = gk['action']
    last_char = action[-1] if action else ''
    # 받침 있으면 '이', 없으면 '가'
    if last_char and (ord(last_char) - 0xAC00) % 28 > 0:
        josa = '이'
    else:
        josa = '가'

    return (
        f"{prefix}, 현재 국면은 [{sp['task']}]이며 "
        f"승산 지수는 {wp['probability']}%로 {mood} 흐름입니다. "
        f"격국은 '{gk['task']}' 국면이므로 {action}{josa} 필요합니다. "
        f"{suffix}"
    )