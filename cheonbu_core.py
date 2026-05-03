# -*- coding: utf-8 -*-
"""
cheonbu_core.py — 천부경(天符經) 분석 엔진 v2.0
고영창 진짜만세력 CAL20000 알고리즘 Python 포팅
v2.0: 태을신수 연동을 위한 절기 API 외부 노출 추가
"""

from datetime import date
from constants import (
    CHEONGAN, JIJI, GANJI60,
    OHAENG_GAN, OHAENG_JI, OHAENG_CYCLE,
    SANG_SAENG, SANG_GEUK,
    YINYANG_GAN, YINYANG_JI, SAMJAE_JI,
    SAMHAP, YUKHAP, CHEONGAN_HAPHWA,
    GUGUNG, HYEOL_OHAENG, DAEUN_PHASES,
    UNITY_YEAR, UNITY_MONTH, UNITY_DAY, UNITY_HOUR, UNITY_MIN,
    UNITY_SU_Y, UNITY_SU_M, UNITY_SU_D, UNITY_SU_H,
    YEAR_MINUTES, MONTH_ARRAY, JEOLGI_NAMES, JEOLGI_HANJA,
)


class CheonbuEngine:
    """천부경(天符經) 체(體) 분석 엔진"""

    def __init__(self, name, birth_date, birth_hour, blood_type):
        self.name = name
        if isinstance(birth_date, str):
            self.birth_date = date.fromisoformat(birth_date)
        else:
            self.birth_date = birth_date
        self.birth_hour = birth_hour
        self.birth_min  = 0
        self.blood_type = blood_type.upper()

    # ═══════════════════════════════════════════
    # A. 날짜 유틸리티 (고영창 알고리즘 직접 포팅)
    # ═══════════════════════════════════════════

    @staticmethod
    def _disptimeday(year, month, day):
        """year년 1/1부터 month/day까지의 누적 일수"""
        e = 0
        for i in range(1, month):
            e += 31
            if i in (2, 4, 6, 9, 11):
                e -= 1
            if i == 2:
                e -= 2
                if year % 4 == 0:    e += 1
                if year % 100 == 0:  e -= 1
                if year % 400 == 0:  e += 1
                if year % 4000 == 0: e -= 1
        e += day
        return e

    @staticmethod
    def _disp2days(y1, m1, d1, y2, m2, d2):
        """y1/m1/d1 → y2/m2/d2 사이 일수 (부호 있음)"""
        dtp = CheonbuEngine._disptimeday
        if y2 > y1:
            p1  = dtp(y1, m1, d1)
            p1n = dtp(y1, 12, 31)
            p2  = dtp(y2, m2, d2)
            pp1, pp2, pr = y1, y2, -1
        elif y2 < y1:
            p1  = dtp(y2, m2, d2)
            p1n = dtp(y2, 12, 31)
            p2  = dtp(y1, m1, d1)
            pp1, pp2, pr = y2, y1, 1
        else:
            return dtp(y2, m2, d2) - dtp(y1, m1, d1)

        dis = p1n - p1
        ppp1 = pp1 + 1
        ppp2 = pp2 - 1
        k = ppp1
        while k <= ppp2:
            if k == 1750 and ppp2 > 1990:
                dis += 88023
                k = 1991
                continue
            dis += dtp(k, 12, 31)
            k += 1
        dis += p2
        dis *= pr
        return dis

    @staticmethod
    def _getminbytime(uy, umm, ud, uh, umin, y1, mo1, d1, h1, mm1):
        """두 시점 사이의 분(分) 차이"""
        dispday = CheonbuEngine._disp2days(uy, umm, ud, y1, mo1, d1)
        return dispday * 24 * 60 + (uh - h1) * 60 + (umin - mm1)

    @staticmethod
    def _getdatebymin(tmin, uyear, umonth, uday, uhour, umin):
        """기준점에서 tmin분 떨어진 시점 역산 → (y, m, d, h, min)"""
        g = CheonbuEngine._getminbytime
        y1 = uyear - tmin // YEAR_MINUTES

        if tmin >= 0:
            y1 += 2
            while True:
                y1 -= 1
                if g(uyear, umonth, uday, uhour, umin, y1, 1, 1, 0, 0) >= tmin:
                    break
            mo1 = 13
            while True:
                mo1 -= 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, 1, 0, 0) >= tmin:
                    break
            d1 = 32
            while True:
                d1 -= 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, 0, 0) >= tmin:
                    break
            h1 = 24
            while True:
                h1 -= 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, h1, 0) >= tmin:
                    break
            t = g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, h1, 0)
            mi1 = t - tmin
        else:
            y1 -= 2
            while True:
                y1 += 1
                if g(uyear, umonth, uday, uhour, umin, y1, 1, 1, 0, 0) < tmin:
                    break
            y1 -= 1
            mo1 = 0
            while True:
                mo1 += 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, 1, 0, 0) < tmin:
                    break
            mo1 -= 1
            d1 = 0
            while True:
                d1 += 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, 0, 0) < tmin:
                    break
            d1 -= 1
            h1 = -1
            while True:
                h1 += 1
                if g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, h1, 0) < tmin:
                    break
            h1 -= 1
            t = g(uyear, umonth, uday, uhour, umin, y1, mo1, d1, h1, 0)
            mi1 = t - tmin

        return y1, mo1, d1, h1, mi1

    # ═══════════════════════════════════════════
    # B. 핵심 — 사주 간지 계산 (sydtoso24yd 포팅)
    # ═══════════════════════════════════════════

    def get_saju_raw(self, target_date=None, target_hour=None, target_min=None):
        """
        고영창 sydtoso24yd 알고리즘 포팅.
        반환: (so24, year_idx, month_idx, day_idx, hour_idx)
        """
        d  = target_date or self.birth_date
        h  = target_hour if target_hour is not None else self.birth_hour
        m  = target_min  if target_min  is not None else self.birth_min
        sy, sm, sd, sh, smin = d.year, d.month, d.day, h, m

        U_Y, U_M, U_D, U_H, U_MIN = (
            UNITY_YEAR, UNITY_MONTH, UNITY_DAY, UNITY_HOUR, UNITY_MIN)

        displ2min = self._getminbytime(U_Y, U_M, U_D, U_H, U_MIN,
                                       sy, sm, sd, sh, smin)
        displ2day = self._disp2days(U_Y, U_M, U_D, sy, sm, sd)

        so24 = displ2min // YEAR_MINUTES
        if displ2min >= 0:
            so24 += 1

        so24year = (so24 % 60) * -1 + UNITY_SU_Y
        if so24year < 0:
            so24year += 60
        elif so24year > 59:
            so24year -= 60

        monthmin100 = (displ2min % YEAR_MINUTES) * -1
        if monthmin100 < 0:
            monthmin100 += YEAR_MINUTES
        elif monthmin100 >= YEAR_MINUTES:
            monthmin100 -= YEAR_MINUTES

        so24month_idx = 0
        for i in range(12):
            j = i * 2
            if MONTH_ARRAY[j] <= monthmin100 < MONTH_ARRAY[j + 2]:
                so24month_idx = i
                break

        t = so24year % 10
        t = t % 5
        so24month = t * 12 + 2 + so24month_idx
        if so24month > 59:
            so24month -= 60

        so24day = (displ2day % 60) * -1 + UNITY_SU_D
        if so24day < 0:
            so24day += 60
        elif so24day > 59:
            so24day -= 60

        if (sh == 0 or sh == 1) and smin < 30:
            hi = 0
        elif (sh == 1 and smin >= 30) or sh == 2 or (sh == 3 and smin < 30):
            hi = 1
        elif (sh == 3 and smin >= 30) or sh == 4 or (sh == 5 and smin < 30):
            hi = 2
        elif (sh == 5 and smin >= 30) or sh == 6 or (sh == 7 and smin < 30):
            hi = 3
        elif (sh == 7 and smin >= 30) or sh == 8 or (sh == 9 and smin < 30):
            hi = 4
        elif (sh == 9 and smin >= 30) or sh == 10 or (sh == 11 and smin < 30):
            hi = 5
        elif (sh == 11 and smin >= 30) or sh == 12 or (sh == 13 and smin < 30):
            hi = 6
        elif (sh == 13 and smin >= 30) or sh == 14 or (sh == 15 and smin < 30):
            hi = 7
        elif (sh == 15 and smin >= 30) or sh == 16 or (sh == 17 and smin < 30):
            hi = 8
        elif (sh == 17 and smin >= 30) or sh == 18 or (sh == 19 and smin < 30):
            hi = 9
        elif (sh == 19 and smin >= 30) or sh == 20 or (sh == 21 and smin < 30):
            hi = 10
        elif (sh == 21 and smin >= 30) or sh == 22 or (sh == 23 and smin < 30):
            hi = 11
        elif sh == 23 and smin >= 30:
            so24day += 1
            if so24day == 60:
                so24day = 0
            hi = 0
        else:
            hi = 0

        t = so24day % 10
        t = t % 5
        so24hour = t * 12 + hi

        return so24, so24year, so24month, so24day, so24hour

    # ═══════════════════════════════════════════
    # C. 편의 함수 — 간지 문자열
    # ═══════════════════════════════════════════

    def get_saju_text(self, target_date=None, target_hour=None):
        _, yi, mi, di, hi = self.get_saju_raw(target_date, target_hour)
        return {
            'year':  GANJI60[yi],
            'month': GANJI60[mi],
            'day':   GANJI60[di],
            'hour':  GANJI60[hi],
        }

    def get_year_ganji(self, target_date=None):
        _, yi, _, _, _ = self.get_saju_raw(target_date)
        return GANJI60[yi]

    def get_month_ganji(self, target_date=None):
        _, _, mi, _, _ = self.get_saju_raw(target_date)
        return GANJI60[mi]

    def get_day_ganji(self, target_date=None):
        _, _, _, di, _ = self.get_saju_raw(target_date)
        return GANJI60[di]

    def get_hour_ganji(self, target_hour=None):
        _, _, _, _, hi = self.get_saju_raw(target_hour=target_hour)
        return GANJI60[hi]

    # ═══════════════════════════════════════════
    # D. 절기 시각 계산 (SolortoSo24 포팅)
    # ═══════════════════════════════════════════

    def get_jeolgi_dates(self, target_date=None):
        """해당 날짜가 속한 절기 구간의 입절·중기·출절 시각"""
        d  = target_date or self.birth_date
        sy, sm, sd = d.year, d.month, d.day
        U_Y, U_M, U_D, U_H, U_MIN = (
            UNITY_YEAR, UNITY_MONTH, UNITY_DAY, UNITY_HOUR, UNITY_MIN)

        _, _, so24month_raw, _, _ = self.get_saju_raw(d, 0)

        displ2min = self._getminbytime(U_Y, U_M, U_D, U_H, U_MIN,
                                       sy, sm, sd, 0, 0)

        monthmin100 = (displ2min % YEAR_MINUTES) * -1
        if monthmin100 < 0:
            monthmin100 += YEAR_MINUTES
        elif monthmin100 >= YEAR_MINUTES:
            monthmin100 -= YEAR_MINUTES

        i_month = so24month_raw % 12 - 2
        if i_month == -2: i_month = 10
        elif i_month == -1: i_month = 11

        j = i_month * 2
        result = {}
        for label, offset in [('ingi', 0), ('midgi', 1), ('outgi', 2)]:
            name_idx = j + offset
            tmin = displ2min + (monthmin100 - MONTH_ARRAY[j + offset])
            y1, mo1, d1, h1, mi1 = self._getdatebymin(
                tmin, U_Y, U_M, U_D, U_H, U_MIN)
            result[label] = (
                JEOLGI_NAMES[name_idx], JEOLGI_HANJA[name_idx],
                y1, mo1, d1, h1, mi1
            )
        return result

    # ═══════════════════════════════════════════
    # D-2. 절기 외부 노출 API (v2.0 신규)
    # ═══════════════════════════════════════════

    def get_dongji_date(self, year):
        """
        해당 연도의 동지(冬至) 날짜·시각 반환.
        태을신수 시계 포국에서 양둔↔음둔 전환 기점으로 사용.
        반환: (year, month, day, hour, minute)
        """
        # 동지는 대설 다음 절기 → JEOLGI_NAMES 인덱스 21
        # 동지가 포함된 대략적 날짜로 시작
        test_date = date(year, 12, 20)
        jg = self.get_jeolgi_dates(test_date)
        # midgi가 동지인지 확인, 아니면 전후 탐색
        for offset in range(-10, 11):
            try:
                td = date(year, 12, 15 + offset)
            except ValueError:
                continue
            jg = self.get_jeolgi_dates(td)
            for key in ('ingi', 'midgi', 'outgi'):
                entry = jg[key]
                if entry[1] == '冬至':
                    return (entry[2], entry[3], entry[4], entry[5], entry[6])
        # 폴백: 12/22 00:00
        return (year, 12, 22, 0, 0)

    def get_haji_date(self, year):
        """
        해당 연도의 하지(夏至) 날짜·시각 반환.
        태을신수 시계 포국에서 양둔↔음둔 전환 기점으로 사용.
        반환: (year, month, day, hour, minute)
        """
        test_date = date(year, 6, 20)
        jg = self.get_jeolgi_dates(test_date)
        for offset in range(-10, 11):
            try:
                td = date(year, 6, 15 + offset)
            except ValueError:
                continue
            jg = self.get_jeolgi_dates(td)
            for key in ('ingi', 'midgi', 'outgi'):
                entry = jg[key]
                if entry[1] == '夏至':
                    return (entry[2], entry[3], entry[4], entry[5], entry[6])
        return (year, 6, 21, 0, 0)

    def get_all_jeolgi_dates(self, year):
        """
        해당 연도의 24절기 전체 날짜·시각 반환.
        반환: list of (절기명, 한자, year, month, day, hour, minute)
        """
        results = []
        # 1월부터 12월까지 매월 1일, 15일에서 절기 탐색
        seen = set()
        for month in range(1, 13):
            for day_probe in (1, 8, 15, 22):
                try:
                    td = date(year, month, day_probe)
                except ValueError:
                    continue
                jg = self.get_jeolgi_dates(td)
                for key in ('ingi', 'midgi', 'outgi'):
                    entry = jg[key]
                    if entry[2] == year and entry[1] not in seen:
                        seen.add(entry[1])
                        results.append(entry)
        # 정렬: 월→일→시 순
        results.sort(key=lambda x: (x[2], x[3], x[4], x[5], x[6]))
        return results

    def get_minutes_from_unity(self, year, month, day, hour=0, minute=0):
        """
        기준점(UNITY)으로부터의 분(分) 차이.
        태을신수 엔진에서 정밀 시간 계산에 사용.
        """
        return self._getminbytime(
            UNITY_YEAR, UNITY_MONTH, UNITY_DAY, UNITY_HOUR, UNITY_MIN,
            year, month, day, hour, minute
        )

    def get_days_from_unity(self, year, month, day):
        """기준점(UNITY)으로부터의 일수 차이."""
        return self._disp2days(
            UNITY_YEAR, UNITY_MONTH, UNITY_DAY,
            year, month, day
        )

    # ═══════════════════════════════════════════
    # E. 4주 종합 분석
    # ═══════════════════════════════════════════

    def get_four_pillars(self, target_date=None, target_hour=None):
        """4주 간지 + 오행 + 음양 + 삼재"""
        saju = self.get_saju_text(target_date, target_hour)
        pillars = {}
        for key, gz in saju.items():
            gan_char = gz[0]
            ji_char  = gz[1]
            pillars[key] = {
                'ganji':   gz,
                'gan':     gan_char,
                'ji':      ji_char,
                'ohaeng':  OHAENG_GAN[gan_char],
                'yinyang': YINYANG_GAN[gan_char],
                'samjae':  SAMJAE_JI[ji_char],
            }
        return pillars

    def get_age(self, ref_year=None):
        return (ref_year or date.today().year) - self.birth_date.year

    def get_life_phase(self, ref_year=None):
        age = self.get_age(ref_year)
        for lo, hi, phase in DAEUN_PHASES:
            if lo <= age <= hi:
                return phase
        return '선천운'

    def get_blood_analysis(self):
        """
        인산의학 사상체질 — 혈액형 기반
        비(脾)=土는 중앙장부이므로 사상체질 분류에서 제외.
        AB=태양인(金), A=태음인(木), O=소양인(火), B=소음인(水)
        ※ 혈액형은 100% 단일이 아니라 부모로부터 복수 혈액 성질을 공유함.
        """
        elem = HYEOL_OHAENG.get(self.blood_type, '木')
        desc = {
            '金': '태양인(太陽人) — 폐대간소(肺大肝小), 백색소 흡수, 익모초가 약쑥보다 좋음',
            '木': '태음인(太陰人) — 간대폐소(肝大肺小), 청색소 흡수, 애엽·노나무 양약, 정신병 적음',
            '火': '소양인(少陽人) — 심대신소(心大腎小), 적색소 흡수, 대추 필수, 인삼·꿀 과용 주의',
            '水': '소음인(少陰人) — 신대심소(腎大心小), 흑색소 흡수, 인삼 온중보양 양약, 녹용 무효',
        }
        sasang = {
            '金': '太陽人', '木': '太陰人', '火': '少陽人', '水': '少陰人',
        }
        organ_big_small = {
            '金': ('肺·大腸', '肝·膽'),     # 폐대간소
            '木': ('肝·膽', '肺·大腸'),     # 간대폐소
            '火': ('心·小腸', '腎·膀胱'),   # 심대신소
            '水': ('腎·膀胱', '心·小腸'),   # 신대심소
        }
        color = {
            '金': '白色素', '木': '靑色素', '火': '赤色素', '水': '黑色素',
        }
        herb_note = {
            '金': '익모초 주약, 약쑥 보조',
            '木': '애엽(잠양온중), 노나무 무해, 보리밥·감자·호밀 부적합',
            '火': '대추 필수, 녹용 1/3만 적합, 인삼·꿀 과용시 열독, 송근 부적합',
            '水': '익모초 3.5근+약쑥 1.5근, 인삼 온중보양 적합, 녹용 무효, 밀가루·닭·돼지 양식',
        }
        big, small = organ_big_small.get(elem, ('?', '?'))
        return {
            'element': elem,
            'description': desc.get(elem, ''),
            'sasang': sasang.get(elem, ''),
            'organ_big': big,
            'organ_small': small,
            'color': color.get(elem, ''),
            'herb_note': herb_note.get(elem, ''),
            'note': '비(脾)=土는 중앙장부로 사상체질 분류에서 제외. '
                    '혈액형은 단일이 아니라 부모 혈액 성질을 복수 공유하며, '
                    '주된 성질이 해당 형으로 발현됨.',
        }

    # ── 관계 분석 ──

    def get_samhap(self, ji_char):
        for name, members in SAMHAP.items():
            if ji_char in members:
                return name
        return None

    def get_yukhap(self, ji_char):
        return YUKHAP.get(ji_char)

    def get_cheongan_hap(self, gan_char):
        for (a, b), result in CHEONGAN_HAPHWA.items():
            if gan_char == a: return f"{a}+{b} = {result}"
            if gan_char == b: return f"{b}+{a} = {result}"
        return None

    # ── 구궁 ──

    def get_gugung_position(self, target_date=None):
        _, yi, _, _, _ = self.get_saju_raw(target_date)
        gung_num = (yi % 9) + 1
        return gung_num, GUGUNG.get(gung_num, {})

    # ═══════════════════════════════════════════
    # F. 천부경 체(體) 점수 (40점 만점)
    # ═══════════════════════════════════════════

    @staticmethod
    def _is_sangsaeng(a, b):
        return SANG_SAENG.get(a) == b or SANG_SAENG.get(b) == a

    def calculate_score(self, target_date=None):
        """년16 + 월10 + 일10 + 시4 = 40"""
        pillars = self.get_four_pillars(target_date)
        score = 0

        gn, gi = self.get_gugung_position(target_date)
        gh = gi[2] if isinstance(gi, tuple) else gi.get('gilhyung', '평')
        score += {'大吉':16,'吉':12,'평':8,'凶':4}.get(gh, 2)

        y_oh = pillars['year']['ohaeng']

        m_oh = pillars['month']['ohaeng']
        if self._is_sangsaeng(y_oh, m_oh):   score += 10
        elif y_oh == m_oh:                    score += 7
        else:                                 score += 3

        d_oh = pillars['day']['ohaeng']
        if self._is_sangsaeng(y_oh, d_oh):   score += 10
        elif y_oh == d_oh:                    score += 7
        else:                                 score += 3

        h_oh = pillars['hour']['ohaeng']
        if self._is_sangsaeng(d_oh, h_oh):   score += 4
        elif d_oh == h_oh:                    score += 3
        else:                                 score += 1

        return score

    @staticmethod
    def get_verdict(score):
        if score >= 35: return '大吉'
        if score >= 28: return '中吉'
        if score >= 20: return '小吉'
        if score >= 12: return '평'
        return '凶'

    # ═══════════════════════════════════════════
    # G. 종합 분석 dict
    # ═══════════════════════════════════════════

    def full_analysis(self, ref_year=None):
        pillars = self.get_four_pillars()
        score   = self.calculate_score()
        gn, gi  = self.get_gugung_position()
        jeolgi  = self.get_jeolgi_dates()
        y_ji    = pillars['year']['ji']

        return {
            'name':           self.name,
            'birth':          str(self.birth_date),
            'hour':           self.birth_hour,
            'blood':          self.blood_type,
            'age':            self.get_age(ref_year),
            'life_phase':     self.get_life_phase(ref_year),
            'pillars':        pillars,
            'gugung':         {'number': gn, 'info': gi},
            'blood_analysis': self.get_blood_analysis(),
            'samhap':         self.get_samhap(y_ji),
            'yukhap':         self.get_yukhap(y_ji),
            'cheongan_hap':   self.get_cheongan_hap(pillars['year']['gan']),
            'jeolgi':         jeolgi,
            'score':          score,
            'max_score':      40,
            'verdict':        self.get_verdict(score),
        }