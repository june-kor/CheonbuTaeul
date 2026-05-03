# -*- coding: utf-8 -*-
"""
taeul_core.py — 태을신수(太乙神數) 분석 엔진 v2.0
태을금경식·태을통종대전 기반 알고리즘
v2.0: 시간축 다중입구(년/월/일/시) + 격국 7중 완성 + 절기 연동
"""
from datetime import date
from constants import (
    CHEONGAN, JIJI, GANJI60, OHAENG_GAN, OHAENG_JI, OHAENG_CYCLE,
    SANG_SAENG, SANG_GEUK,
    TAEUL_GRAND_EPOCH,
    TAEUL_DONGJI_EPOCH, TAEUL_DONGJI_BASE_JEOKYEON,
    TAEUL_GUNG_NAME, TAEUL_YANG_GUNG, TAEUL_YIN_GUNG,
    TAEUL_YANG_ORDER, TAEUL_YIN_ORDER,
    TAEUL_16_ORDER, TAEUL_16GUNG_INFO, TAEUL_JEONGGUNG_NUM,
    TAEUL_GUNGNUM_TO_16, TAEUL_DAEGUNG,
    GYESIN_TABLE,
    PALMUN_ORDER, PALMUN_GIL, PALMUN_GUNG,
    GYEOKGUK_TYPE, EUMYANG_SU_GRADE, HAWASU_VALUES,
    NAEEUM_60, NAEEUM_OHAENG,
    YANG9_GRAND_CYCLE, YANG9_SMALL_CYCLE,
    YIN6_GRAND_CYCLE, YIN6_SMALL_CYCLE,
    HAPSIN_TABLE,
    GUA64_SEQUENCE, GUA64_KOR,
    YANG_YEARS, YIN_YEARS,
    JIJI_12_ORDER,
    OBOK_ORDER, DAEYU_ORDER,
    SOYU_YANG_ORDER, SOYU_YIN_ORDER,
    SASIN_ORDER, CHEONUL_ORDER, JIEUL_ORDER,
    YANG_GUNG, YIN_GUNG,
    EUMYANG_DETAIL, EUMYANG_GIL,
    DIVINATION_TIME_UNIT,
)


class TaeulEngine:
    """태을신수 정통 포국 엔진 v2.0"""

    def __init__(self, birth_date, birth_hour, cheonbu_engine=None):
        """
        v2.0: cheonbu_engine을 선택적으로 받아 절기 연동 가능
        """
        self.birth_date = (
            date.fromisoformat(birth_date) if isinstance(birth_date, str)
            else birth_date
        )
        self.birth_hour = birth_hour
        self._cheonbu = cheonbu_engine  # 절기 연동용

    # ═══════════════════════════════════════
    # A. 적년 — 시간축 다중입구 (v2.0 핵심 리팩)
    # ═══════════════════════════════════════

    def get_jeokyeon(self, year=None, month=None, day=None, hour=None):
        """
        통합 적년 산출.
        - year만: 세계(歲計) — 기존과 동일
        - year+month: 월계(月計)
        - year+month+day: 일계(日計)
        - year+month+day+hour: 시계(時計)
        """
        y = year or date.today().year
        grand = TAEUL_GRAND_EPOCH + y

        if month is None:
            return grand, 'year'

        # 월계: 대적년 × 12 + (월-1)
        if day is None:
            monthly = grand * 12 + (month - 1)
            return monthly, 'month'

        # 일계: 대적년 × 360 + 해당연도 경과일수
        day_of_year = self._day_of_year(y, month, day)
        daily = grand * 360 + day_of_year
        if hour is None:
            return daily, 'day'

        # 시계: 일적년 × 12 + 시진(0~11)
        shi_idx = self._hour_to_shijin(hour)
        hourly = daily * 12 + shi_idx
        return hourly, 'hour'

    def get_grand_jeokyeon(self, target_year=None):
        """하위호환: 기존 세계 적년"""
        jy, _ = self.get_jeokyeon(target_year)
        return jy

    @staticmethod
    def _day_of_year(year, month, day):
        """해당 연도의 1/1부터 누적 일수"""
        days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            days_in_month[1] = 29
        return sum(days_in_month[:month-1]) + day

    @staticmethod
    def _hour_to_shijin(hour):
        """시간(0~23) → 시진 인덱스(0~11)"""
        return ((hour + 1) // 2) % 12

    # ═══════════════════════════════════════
    # A-2. 둔법 판정 — 시계용 동지·하지 연동
    # ═══════════════════════════════════════

    def get_dunbeop(self, year=None, month=None, day=None, hour=None):
        """
        둔법 판정.
        - 세계/월계/일계: 국수 기반 (1~36 양둔, 37~72 음둔)
        - 시계: 동지후 양둔, 하지후 음둔 (절기 연동)
        """
        if hour is not None and self._cheonbu is not None:
            # 시계: 절기 기반 판정
            y = year or date.today().year
            m = month or 1
            d = day or 1
            dongji = self._cheonbu.get_dongji_date(y - 1)  # 전년도 동지
            haji = self._cheonbu.get_haji_date(y)
            # 동지~하지: 양둔, 하지~동지: 음둔
            current = (y, m, d, hour)
            dongji_t = dongji[:4] if len(dongji) >= 4 else (y-1, 12, 22, 0)
            haji_t = haji[:4] if len(haji) >= 4 else (y, 6, 21, 0)
            if dongji_t <= current < haji_t:
                return '陽遁'
            else:
                return '陰遁'
        # 세계/월계/일계: 국수 기반
        guk = self.get_taeul_guk(year)
        return '陽遁' if 1 <= guk <= 36 else '陰遁'

    # ═══════════════════════════════════════
    # B. 입성수·국수 (기존 유지)
    # ═══════════════════════════════════════

    def get_dongji_jeokyeon(self, target_year=None):
        y = target_year or date.today().year
        return TAEUL_DONGJI_BASE_JEOKYEON + (y - TAEUL_DONGJI_EPOCH)

    def get_ipseongsu(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        ips = gj % 360
        return ips if ips != 0 else 360

    def get_taeul_guk(self, target_year=None):
        ips = self.get_ipseongsu(target_year)
        guk = ips % 72
        return guk if guk != 0 else 72

    def get_won_info(self, target_year=None):
        guk = self.get_taeul_guk(target_year)
        if 1 <= guk <= 24:
            return '上元'
        elif 25 <= guk <= 48:
            return '中元'
        else:
            return '下元'

    # ═══════════════════════════════════════
    # C. 태을재궁 (기존 유지)
    # ═══════════════════════════════════════

    def get_taeul_jaegung(self, target_year=None):
        ips = self.get_ipseongsu(target_year)
        pos_in_24 = (ips - 1) % 24
        gung_idx = pos_in_24 // 3
        dunbeop = self.get_dunbeop(target_year)
        if dunbeop == '陽遁':
            return TAEUL_YANG_ORDER[gung_idx]
        else:
            return TAEUL_YIN_ORDER[gung_idx]

    def get_taeul_jaegung_detail(self, target_year=None):
        gnum = self.get_taeul_jaegung(target_year)
        name, oh, mun, nature = TAEUL_GUNG_NAME[gnum]
        ips = self.get_ipseongsu(target_year)
        pos_in_3 = (ips - 1) % 3
        sari = ['理天', '理地', '理人'][pos_in_3]
        return {
            'gung_num': gnum,
            'gwe_name': name,
            'ohaeng': oh,
            'mun_name': mun,
            'gung_type': nature,
            'samli': sari,
            'samli_year': pos_in_3 + 1,
        }

    # ═══════════════════════════════════════
    # D. 연지·계신 (기존 유지)
    # ═══════════════════════════════════════

    def _get_year_ganji(self, target_year=None):
        y = target_year or date.today().year
        idx = (y - 4) % 60
        return GANJI60[idx]

    def _get_year_ji(self, target_year=None):
        return self._get_year_ganji(target_year)[1]

    def get_gyesin(self, target_year=None):
        ji = self._get_year_ji(target_year)
        return GYESIN_TABLE[ji]

    # ═══════════════════════════════════════
    # E. 천목/문창 (기존 유지)
    # ═══════════════════════════════════════

    def _advance_16(self, start_name, steps, dunbeop):
        start_idx = TAEUL_16_ORDER.index(start_name)
        count = 0
        pos = start_idx
        if steps <= 0:
            return TAEUL_16_ORDER[pos]
        while True:
            current = TAEUL_16_ORDER[pos]
            count += 1
            if dunbeop == '陽遁' and current in ('乾', '坤'):
                if count < steps:
                    count += 1
            elif dunbeop == '陰遁' and current in ('艮', '巽'):
                if count < steps:
                    count += 1
            if count >= steps:
                return TAEUL_16_ORDER[pos]
            pos = (pos + 1) % 16

    def get_cheonmok(self, target_year=None):
        guk = self.get_taeul_guk(target_year)
        dunbeop = self.get_dunbeop(target_year)
        remainder = guk % 18
        if remainder == 0:
            remainder = 18
        start = '申' if dunbeop == '陽遁' else '寅'
        return self._advance_16(start, remainder, dunbeop)

    # ═══════════════════════════════════════
    # F. 객목/시격 (기존 유지)
    # ═══════════════════════════════════════

    def get_gaekmok(self, target_year=None):
        gyesin = self.get_gyesin(target_year)
        cheonmok = self.get_cheonmok(target_year)
        gyesin_idx = TAEUL_16_ORDER.index(gyesin)
        cheonmok_idx = TAEUL_16_ORDER.index(cheonmok)
        dist = (cheonmok_idx - gyesin_idx) % 16
        gan_idx = TAEUL_16_ORDER.index('艮')
        result_idx = (gan_idx + dist) % 16
        return TAEUL_16_ORDER[result_idx]

    # ═══════════════════════════════════════
    # G. 주산·객산 (기존 유지)
    # ═══════════════════════════════════════

    def _gung16_to_number(self, name16):
        info = TAEUL_16GUNG_INFO[name16]
        if info[2]:
            return TAEUL_JEONGGUNG_NUM[name16]
        else:
            return 1

    def _find_16_idx_of_gungnum(self, gung_num):
        name16 = TAEUL_GUNGNUM_TO_16[gung_num]
        return TAEUL_16_ORDER.index(name16)

    def _calc_san(self, start_name16, taeul_gung_num):
        """
        start_name16에서 시작하여 태을 전궁까지 순행하며 합산.
        정궁은 궁수로, 간신은 1로 계산.
        태을이 있는 궁의 바로 전 궁에서 멈춤.

        특수 처리:
        - 시작점의 정궁번호가 태을궁과 같으면 해당 궁수만 반환
        - 시작점이 간신이면서 다음 정궁이 태을궁이면 간신값(1)만 반환
        """
        # 특수 처리: 시작점이 태을궁과 같은 정궁인 경우
        start_gung = TAEUL_JEONGGUNG_NUM.get(start_name16)
        if start_gung is not None and start_gung == taeul_gung_num:
            return self._gung16_to_number(start_name16)

        # 태을궁의 16궁 배열 인덱스
        taeul_16_name = TAEUL_GUNGNUM_TO_16[taeul_gung_num]
        taeul_16_idx = TAEUL_16_ORDER.index(taeul_16_name)

        # 시작점의 16궁 배열 인덱스
        start_idx = TAEUL_16_ORDER.index(start_name16)

        # 특수 처리: 시작 다음이 바로 태을궁인 경우
        next_idx = (start_idx + 1) % 16
        if next_idx == taeul_16_idx:
            return self._gung16_to_number(start_name16)

        # 일반 순행 합산
        total = 0
        pos = start_idx
        for _ in range(16):
            current = TAEUL_16_ORDER[pos]
            total += self._gung16_to_number(current)
            next_pos = (pos + 1) % 16
            if next_pos == taeul_16_idx:
                break
            pos = next_pos

        return total

    def get_jusan(self, target_year=None):
        cheonmok = self.get_cheonmok(target_year)
        taeul_gung = self.get_taeul_jaegung(target_year)
        return self._calc_san(cheonmok, taeul_gung)

    def get_gaeksan(self, target_year=None):
        gaekmok = self.get_gaekmok(target_year)
        taeul_gung = self.get_taeul_jaegung(target_year)
        return self._calc_san(gaekmok, taeul_gung)

    # ═══════════════════════════════════════
    # H. 대장·참장 (기존 유지)
    # ═══════════════════════════════════════

    def _san_to_daejang(self, san_value):
        if san_value % 10 == 0:
            r = san_value % 9
            return r if r != 0 else 9
        else:
            return san_value % 10

    def _daejang_to_chamjang(self, daejang_gung):
        val = daejang_gung * 3
        if val > 9:
            val = val % 10
            if val == 0:
                val = (daejang_gung * 3) % 9
                if val == 0:
                    val = 9
        return val

    def get_ju_daejang(self, target_year=None):
        return self._san_to_daejang(self.get_jusan(target_year))

    def get_ju_chamjang(self, target_year=None):
        return self._daejang_to_chamjang(self.get_ju_daejang(target_year))

    def get_gaek_daejang(self, target_year=None):
        return self._san_to_daejang(self.get_gaeksan(target_year))

    def get_gaek_chamjang(self, target_year=None):
        return self._daejang_to_chamjang(self.get_gaek_daejang(target_year))

    # ═══════════════════════════════════════
    # I. 격국 7중 판정 (v2.0 완성)
    # ═══════════════════════════════════════

    def get_gyeokguk(self, target_year=None):
        """
        격국 7중 판정 — 태을금경식 정통법
        1. 囚: 주대장 = 태을 (같은 궁)
        2. 格: 주대장과 태을이 대궁
        3. 廹: 주대장이 태을 좌우 (순서상 ±1)
        4. 掩: 객목이 태을과 같은 궁
        5. 擊: 객대장이 태을 좌우
        6. 提挾: 태을·천목이 객측에 끼임
        7. 四郭固: 주객 대소장이 태을 사방을 포위
        ※ 복합 발생 시 가장 흉한 것을 취함
        """
        taeul_gung = self.get_taeul_jaegung(target_year)
        ju_dj = self.get_ju_daejang(target_year)
        ju_cj = self.get_ju_chamjang(target_year)
        gaek_dj = self.get_gaek_daejang(target_year)
        gaek_cj = self.get_gaek_chamjang(target_year)

        # 천목·객목의 궁수 (정궁이면 궁수, 간신이면 None)
        cheonmok = self.get_cheonmok(target_year)
        gaekmok = self.get_gaekmok(target_year)
        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        gm_gung = TAEUL_JEONGGUNG_NUM.get(gaekmok)

        dunbeop = self.get_dunbeop(target_year)
        order = TAEUL_YANG_ORDER if dunbeop == '陽遁' else TAEUL_YIN_ORDER

        detected = []

        # ① 囚: 주대장 = 태을
        if ju_dj == taeul_gung:
            detected.append('囚')

        # ② 格: 대궁 관계
        daegung = TAEUL_DAEGUNG.get(taeul_gung)
        if ju_dj == daegung:
            detected.append('格')

        # ③ 廹: 태을 좌우
        if taeul_gung in order:
            t_idx = order.index(taeul_gung)
            for dj in [ju_dj, ju_cj]:
                if dj in order:
                    d_idx = order.index(dj)
                    circ = min(abs(t_idx - d_idx), 8 - abs(t_idx - d_idx))
                    if circ == 1 and '囚' not in detected:
                        if '廹' not in detected:
                            detected.append('廹')

        # ④ 掩: 객목이 태을과 같은 궁
        if gm_gung is not None and gm_gung == taeul_gung:
            detected.append('掩')

        # ⑤ 擊: 객대장이 태을 좌우
        if taeul_gung in order:
            t_idx = order.index(taeul_gung)
            for dj in [gaek_dj, gaek_cj]:
                if dj in order:
                    d_idx = order.index(dj)
                    circ = min(abs(t_idx - d_idx), 8 - abs(t_idx - d_idx))
                    if circ == 1:
                        if '擊' not in detected:
                            detected.append('擊')

        # ⑥ 提挾: 태을과 천목이 객측(객대장·객참장) 사이에 끼임
        if cm_gung is not None and taeul_gung in order and cm_gung in order:
            t_idx = order.index(taeul_gung)
            c_idx = order.index(cm_gung) if cm_gung in order else -1
            gaek_positions = set()
            for g in [gaek_dj, gaek_cj]:
                if g in order:
                    gaek_positions.add(order.index(g))
            if len(gaek_positions) >= 2:
                gp = sorted(gaek_positions)
                if gp[0] < t_idx < gp[-1] or gp[0] < c_idx < gp[-1]:
                    detected.append('提挾')

        # ⑦ 四郭固: 주객 대소장 4개가 태을을 사방에서 포위
        if taeul_gung in order:
            t_idx = order.index(taeul_gung)
            surround = set()
            for s in [ju_dj, ju_cj, gaek_dj, gaek_cj]:
                if s in order:
                    surround.add(order.index(s))
            if len(surround) >= 4:
                left = any(i < t_idx for i in surround)
                right = any(i > t_idx for i in surround)
                if left and right:
                    detected.append('四郭固')

        # 결과: 가장 흉한 것 반환
        priority = ['四郭固', '提挾', '囚', '掩', '格', '擊', '廹']
        for p in priority:
            if p in detected:
                return p

        # 5궁 관문
        if ju_dj == 5:
            return '關'

        return '和'

    def get_gyeokguk_detail(self, target_year=None):
        guk = self.get_gyeokguk(target_year)
        grade, desc = GYEOKGUK_TYPE.get(guk, ('中', '판정 불능'))
        return {'type': guk, 'gilhyung': grade, 'description': desc}

    # ═══════════════════════════════════════
    # J. 팔문직사 (기존 유지)
    # ═══════════════════════════════════════

    def get_palmun_jiksa(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        r240 = gj % 240
        if r240 == 0:
            r240 = 240
        idx = (r240 - 1) // 30
        mun = PALMUN_ORDER[idx % 8]
        gil = PALMUN_GIL[mun]
        return mun, gil

    # ═══════════════════════════════════════
    # K. 음양수 (기존 유지)
    # ═══════════════════════════════════════

    def get_eumyangsu(self, target_year=None):
        jusan = self.get_jusan(target_year)
        taeul_gung = self.get_taeul_jaegung(target_year)
        ones = jusan % 10
        if ones == 0:
            ones = jusan % 9 or 9

        is_yang_gung = taeul_gung in TAEUL_YANG_GUNG
        is_odd = (jusan % 2 == 1)

        if ones in (3, 9) and is_yang_gung:          label = '重陽'
        elif ones in (2, 6) and not is_yang_gung:     label = '重陰'
        elif ones in (1, 7) and not is_yang_gung:     label = '陰中重陽'
        elif ones in (4, 8) and is_yang_gung:         label = '陽中重陰'
        elif (ones == 1 and not is_yang_gung) or \
             (ones in (4, 8) and is_yang_gung):       label = '上和'
        elif (ones in (2, 6) and not is_yang_gung) or \
             (ones in (3, 9) and is_yang_gung):       label = '次和'
        elif jusan in HAWASU_VALUES:                  label = '下和'
        elif (is_yang_gung and is_odd) or \
             (not is_yang_gung and not is_odd):       label = '不和'
        else:                                         label = '次和'

        grade, desc = EUMYANG_SU_GRADE.get(label, ('中', '판정 불능'))
        return {'label': label, 'grade': grade, 'description': desc, 'value': jusan}

    # ═══════════════════════════════════════
    # L. 삼재수 (기존 유지)
    # ═══════════════════════════════════════

    def get_samjaesu(self, target_year=None):
        jusan = self.get_jusan(target_year)
        has_heaven = (jusan >= 10)
        has_earth = ('5' in str(jusan))
        has_human = ('1' in str(jusan))
        result = []
        if has_heaven: result.append('天')
        if has_earth:  result.append('地')
        if has_human:  result.append('人')
        label = '完' if len(result) == 3 else ('空' if len(result) == 0 else ''.join(result))
        return {'label': label, 'parts': result, 'jusan': jusan}

    # ═══════════════════════════════════════
    # M. 주승객패 / 장단수 (기존 유지)
    # ═══════════════════════════════════════

    def get_seungpae(self, target_year=None):
        jusan = self.get_jusan(target_year)
        gaeksan = self.get_gaeksan(target_year)
        if jusan > gaeksan:   return '主勝', jusan, gaeksan
        elif gaeksan > jusan: return '客勝', jusan, gaeksan
        else:                 return '和', jusan, gaeksan

    def get_jangdan(self, target_year=None):
        jusan = self.get_jusan(target_year)
        gaeksan = self.get_gaeksan(target_year)
        return {
            'jusan': '長數' if jusan >= 11 else '短數',
            'gaeksan': '長數' if gaeksan >= 11 else '短數',
        }

    # ═══════════════════════════════════════
    # N. 납음오행 승부 판정 (v2.0 신규)
    # ═══════════════════════════════════════

    def get_naeeum_seungpae(self, target_year=None):
        """납음오행 기반 주객 정밀 승부 판정"""
        year_ganji = self._get_year_ganji(target_year)
        naeeum_name = NAEEUM_60.get(year_ganji, '?')
        naeeum_oh = NAEEUM_OHAENG.get(year_ganji, '土')

        cheonmok = self.get_cheonmok(target_year)
        gaekmok = self.get_gaekmok(target_year)

        # 천목·객목의 오행 (정궁이면 궁오행, 간신이면 지지오행)
        cm_info = TAEUL_16GUNG_INFO.get(cheonmok, ('?', None, False))
        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        cm_oh = TAEUL_GUNG_NAME[cm_gung][1] if cm_gung else OHAENG_JI.get(cheonmok, '土')

        gm_info = TAEUL_16GUNG_INFO.get(gaekmok, ('?', None, False))
        gm_gung = TAEUL_JEONGGUNG_NUM.get(gaekmok)
        gm_oh = TAEUL_GUNG_NAME[gm_gung][1] if gm_gung else OHAENG_JI.get(gaekmok, '土')

        # 주(천목) → 객(객목) 상극 판정
        if SANG_GEUK.get(cm_oh) == gm_oh:
            return '主剋客', naeeum_name, cm_oh, gm_oh
        elif SANG_GEUK.get(gm_oh) == cm_oh:
            return '客剋主', naeeum_name, cm_oh, gm_oh
        elif cm_oh == gm_oh:
            return '同音平', naeeum_name, cm_oh, gm_oh
        elif SANG_SAENG.get(cm_oh) == gm_oh:
            return '主生客', naeeum_name, cm_oh, gm_oh
        elif SANG_SAENG.get(gm_oh) == cm_oh:
            return '客生主', naeeum_name, cm_oh, gm_oh
        else:
            return '無關', naeeum_name, cm_oh, gm_oh

    # ═══════════════════════════════════════
    # O. 양9·음6 재앙 주기 (v2.0 신규)
    # ═══════════════════════════════════════

    def get_yang9_yin6(self, target_year=None):
        """양9·음6 대재앙 주기 판정"""
        gj = self.get_grand_jeokyeon(target_year)

        yang9_grand_pos = gj % YANG9_GRAND_CYCLE
        yang9_small_pos = gj % YANG9_SMALL_CYCLE
        yin6_grand_pos = gj % YIN6_GRAND_CYCLE
        yin6_small_pos = gj % YIN6_SMALL_CYCLE

        # 주기 끝(0)이거나 마지막 10% 구간이면 경고
        yang9_warn = yang9_small_pos == 0 or yang9_small_pos > YANG9_SMALL_CYCLE * 0.9
        yin6_warn = yin6_small_pos == 0 or yin6_small_pos > YIN6_SMALL_CYCLE * 0.9

        return {
            'yang9_grand': {'position': yang9_grand_pos, 'cycle': YANG9_GRAND_CYCLE},
            'yang9_small': {'position': yang9_small_pos, 'cycle': YANG9_SMALL_CYCLE,
                            'warning': yang9_warn},
            'yin6_grand':  {'position': yin6_grand_pos,  'cycle': YIN6_GRAND_CYCLE},
            'yin6_small':  {'position': yin6_small_pos,  'cycle': YIN6_SMALL_CYCLE,
                            'warning': yin6_warn},
        }

    # ═══════════════════════════════════════
    # P. 승산 지수 (v2.0 신규)
    # ═══════════════════════════════════════

    def get_win_probability(self, target_year=None):
        """주산/(주산+객산) × 100 = 승산 지수 (%)"""
        jusan = self.get_jusan(target_year)
        gaeksan = self.get_gaeksan(target_year)
        total = jusan + gaeksan
        if total == 0:
            return 50.0
        return round(jusan / total * 100, 1)

    # ═══════════════════════════════════════
    # Q. 동지일 간지 검증 (기존 유지)
    # ═══════════════════════════════════════

    def get_dongji_ganji(self, target_year=None):
        jy = self.get_dongji_jeokyeon(target_year)
        raw = jy * 365.2425
        frac = raw - int(raw)
        val = int(raw) + 1 if frac >= 0.7 else int(raw)
        remainder = val % 60
        idx_0based = remainder
        if idx_0based >= 60:
            idx_0based = 0
        return GANJI60[idx_0based]

    # ═══════════════════════════════════════
    # R~AC. v1.2 확장 메서드 (모두 유지)
    # ═══════════════════════════════════════

    def get_hapsin(self, target_year=None):
        year_ji = self._get_year_ji(target_year)
        hapsin_ji = HAPSIN_TABLE.get(year_ji, year_ji)
        gung = TAEUL_JEONGGUNG_NUM.get(hapsin_ji)
        info = TAEUL_16GUNG_INFO.get(hapsin_ji, ())
        name = info[0] if isinstance(info, (tuple, list)) and len(info) >= 1 else str(info)
        return {'year_ji': year_ji, 'hapsin': hapsin_ji, 'name': name, 'gung_num': gung}

    def get_jeongmok(self, target_year=None):
        hapsin = self.get_hapsin(target_year)
        year_ji = hapsin['year_ji']
        hapsin_ji = hapsin['hapsin']
        idx_hapsin = TAEUL_16_ORDER.index(hapsin_ji)
        idx_taese = TAEUL_16_ORDER.index(year_ji)
        dist = (idx_taese - idx_hapsin) % 16
        cheonmok_pos = self.get_cheonmok(target_year)
        if cheonmok_pos not in TAEUL_16_ORDER:
            cheonmok_pos = '子'
        idx_cheonmok = TAEUL_16_ORDER.index(cheonmok_pos)
        idx_jeongmok = (idx_cheonmok + dist) % 16
        jeongmok_pos = TAEUL_16_ORDER[idx_jeongmok]
        gung = TAEUL_JEONGGUNG_NUM.get(jeongmok_pos)
        info = TAEUL_16GUNG_INFO.get(jeongmok_pos, ())
        name = info[0] if isinstance(info, (tuple, list)) and len(info) >= 1 else ''
        return {'position': jeongmok_pos, 'gung_num': gung, 'dist': dist, 'name': name}

    def get_jeongsan(self, target_year=None):
        jeongmok = self.get_jeongmok(target_year)
        jm_pos = jeongmok['position']
        taeul_gung = self.get_taeul_jaegung(target_year)
        return self._calc_san(jm_pos, taeul_gung)

    def get_jeong_daejang(self, target_year=None):
        return self._san_to_daejang(self.get_jeongsan(target_year))

    def get_jeong_chamjang(self, target_year=None):
        return self._daejang_to_chamjang(self.get_jeong_daejang(target_year))

    def get_yeon_gwae(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        remainder = gj % 64
        if remainder == 0: remainder = 64
        idx = remainder - 1
        return {'sequence': remainder, 'name': GUA64_SEQUENCE[idx], 'kor': GUA64_KOR[idx]}

    def get_yeon_gwae_detail(self, target_year=None):
        gwae = self.get_yeon_gwae(target_year)
        year_ji = self._get_year_ji(target_year)
        gwae['is_yang_year'] = year_ji in YANG_YEARS
        gwae['year_ji'] = year_ji
        return gwae

    # ═══════════════════════════════════════
    # R~AC. v1.2 확장 메서드 계속
    # ═══════════════════════════════════════

    def get_samgi(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        base = (gj + 250) % 360
        if base == 0: base = 360

        gun_q, gun_r = divmod(base, 30)
        if gun_r == 0: gun_q -= 1; gun_r = 30
        gun_pos = JIJI_12_ORDER[(JIJI_12_ORDER.index('午') + gun_q % 12) % 12]

        sin_rem = base % 36
        if sin_rem == 0: sin_rem = 36
        sin_q, sin_r = divmod(sin_rem, 3)
        if sin_r == 0: sin_q -= 1; sin_r = 3
        sin_pos = JIJI_12_ORDER[(JIJI_12_ORDER.index('午') + sin_q % 12) % 12]

        min_rem = base % 12
        if min_rem == 0: min_rem = 12
        min_idx = (min_rem - 1) % 12
        min_pos = JIJI_12_ORDER[(JIJI_12_ORDER.index('戌') + min_idx) % 12]

        return {
            'base': base,
            'gungi': {'position': gun_pos, 'year_in_gung': gun_r},
            'singi': {'position': sin_pos, 'year_in_gung': sin_r},
            'mingi': {'position': min_pos, 'year_in_gung': min_rem},
        }

    def get_obok(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        base = (gj + 250) % 225
        if base == 0: base = 225
        q, r = divmod(base, 45)
        if r == 0: q -= 1; r = 45
        gung_num = OBOK_ORDER[q % len(OBOK_ORDER)]
        return {
            'gung_num': gung_num,
            'gung_name': TAEUL_GUNG_NAME.get(gung_num, ('中','土','樞紐','不入')),
            'year_in_gung': r,
        }

    def get_daeyu(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        base = (gj + 34) % 288
        if base == 0: base = 288
        q, r = divmod(base, 36)
        if r == 0: q -= 1; r = 36
        gung_num = DAEYU_ORDER[q % len(DAEYU_ORDER)]
        if r <= 12:   samli = '理天'
        elif r <= 24: samli = '理地'
        else:         samli = '理人'
        return {
            'gung_num': gung_num,
            'gung_name': TAEUL_GUNG_NAME.get(gung_num, ('?','?','?','?')),
            'year_in_gung': r,
            'samli': samli,
        }

    def get_soyu(self, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        base = gj % 360
        if base == 0: base = 360
        q1, r1 = divmod(base, 24)
        if r1 == 0: r1 = 24
        q2, r2 = divmod(r1, 3)
        if r2 == 0: q2 -= 1; r2 = 3
        order = SOYU_YANG_ORDER
        gung_num = order[q2 % len(order)]
        return {
            'gung_num': gung_num,
            'gung_name': TAEUL_GUNG_NAME.get(gung_num, ('?','?','?','?')),
            'year_in_gung': r2,
        }

    def _get_12ji_star(self, start_order, target_year=None):
        gj = self.get_grand_jeokyeon(target_year)
        base = gj % 360
        if base == 0: base = 360
        rem36 = base % 36
        if rem36 == 0: rem36 = 36
        q, r = divmod(rem36, 3)
        if r == 0: q -= 1; r = 3
        pos_idx = q % len(start_order)
        return {'position': start_order[pos_idx], 'year_in_pos': r}

    def get_sasin(self, target_year=None):
        return self._get_12ji_star(SASIN_ORDER, target_year)

    def get_cheonul(self, target_year=None):
        return self._get_12ji_star(CHEONUL_ORDER, target_year)

    def get_jieul(self, target_year=None):
        return self._get_12ji_star(JIEUL_ORDER, target_year)

    def get_eumyangsu_detail(self, target_year=None):
        jusan = self.get_jusan(target_year)
        taeul_gung = self.get_taeul_jaegung(target_year)

        if jusan % 10 == 5:
            return {'value': jusan, 'label': '杜塞', 'grade': '大凶', 'score': 0}

        units = jusan % 10
        tens = (jusan // 10) % 10 if jusan >= 10 else 0
        is_yang_num = (units % 2 == 1)
        is_yang_gung = (taeul_gung in YANG_GUNG)

        if is_yang_gung and is_yang_num:
            return {'value': jusan, 'label': '不和',
                    'grade': EUMYANG_GIL.get('不和', ('凶',1))[0],
                    'score': EUMYANG_GIL.get('不和', ('凶',1))[1]}
        if not is_yang_gung and not is_yang_num:
            return {'value': jusan, 'label': '不和',
                    'grade': EUMYANG_GIL.get('不和', ('凶',1))[0],
                    'score': EUMYANG_GIL.get('不和', ('凶',1))[1]}

        if is_yang_num and is_yang_gung:      cat = 'A'
        elif not is_yang_num and not is_yang_gung: cat = 'B'
        elif is_yang_num and not is_yang_gung: cat = 'C'
        else:                                  cat = 'D'

        if jusan < 10:
            label = '上和' if not (is_yang_gung == is_yang_num) else '不和'
        else:
            tens_yang = (tens % 2 == 1)
            if tens_yang and is_yang_gung:          cat_tens = 'A'
            elif not tens_yang and not is_yang_gung: cat_tens = 'B'
            elif tens_yang and not is_yang_gung:     cat_tens = 'C'
            else:                                    cat_tens = 'D'
            combo = cat_tens + cat
            label = EUMYANG_DETAIL.get(combo, '不和')

        info = EUMYANG_GIL.get(label, ('평', 3))
        return {'value': jusan, 'label': label, 'grade': info[0], 'score': info[1]}

    # ═══════════════════════════════════════
    # S. 종합 점수 (기존 유지 + 납음 가산)
    # ═══════════════════════════════════════

    def calculate_score(self, target_year=None):
        """태을신수 종합 점수 (40점 만점)"""
        score = 0

        guk = self.get_gyeokguk(target_year)
        guk_scores = {'和':10, '廹':5, '關':4, '格':2, '擊':3, '掩':2, '囚':0, '提挾':0, '四郭固':0}
        score += guk_scores.get(guk, 3)

        eys = self.get_eumyangsu(target_year)
        eys_scores = {'上和':10, '重陽':9, '次和':7, '下和':5,
                      '陰中重陽':6, '陽中重陰':3, '不和':1, '重陰':0, '杜塞':0}
        score += eys_scores.get(eys['label'], 3)

        mun, gil = self.get_palmun_jiksa(target_year)
        mun_scores = {'大吉':8, '小吉':6, '小凶':3, '大凶':0}
        score += mun_scores.get(gil, 4)

        result, ju, gaek = self.get_seungpae(target_year)
        if result == '主勝':   score += 6
        elif result == '和':   score += 4
        else:                  score += 2

        sj = self.get_samjaesu(target_year)
        score += len(sj['parts']) * 2

        return min(score, 40)

    def get_verdict(self, score):
        if score >= 35: return '大吉'
        elif score >= 28: return '吉'
        elif score >= 21: return '小吉'
        elif score >= 14: return '평'
        elif score >= 7:  return '凶'
        else:             return '大凶'

    # ═══════════════════════════════════════
    # T. 전체 분석 (v2.0 통합)
    # ═══════════════════════════════════════

    def full_analysis(self, target_year=None):
        y = target_year or date.today().year

        grand_jy = self.get_grand_jeokyeon(y)
        ips = self.get_ipseongsu(y)
        guk = self.get_taeul_guk(y)
        dunbeop = self.get_dunbeop(y)
        won = self.get_won_info(y)
        jaegung = self.get_taeul_jaegung_detail(y)

        year_ganji = self._get_year_ganji(y)
        gyesin = self.get_gyesin(y)
        cheonmok = self.get_cheonmok(y)
        gaekmok = self.get_gaekmok(y)

        jusan = self.get_jusan(y)
        gaeksan = self.get_gaeksan(y)
        seungpae, _, _ = self.get_seungpae(y)
        jangdan = self.get_jangdan(y)

        ju_dj = self.get_ju_daejang(y)
        ju_cj = self.get_ju_chamjang(y)
        gaek_dj = self.get_gaek_daejang(y)
        gaek_cj = self.get_gaek_chamjang(y)

        gyeokguk = self.get_gyeokguk_detail(y)
        palmun, palmun_gil = self.get_palmun_jiksa(y)
        eumyangsu = self.get_eumyangsu(y)
        samjaesu = self.get_samjaesu(y)
        dongji = self.get_dongji_ganji(y)
        win_prob = self.get_win_probability(y)
        naeeum = self.get_naeeum_seungpae(y)
        yang9yin6 = self.get_yang9_yin6(y)

        score = self.calculate_score(y)
        verdict = self.get_verdict(score)

        cm_info = TAEUL_16GUNG_INFO.get(cheonmok, ('?', None, False))
        gm_info = TAEUL_16GUNG_INFO.get(gaekmok, ('?', None, False))
        gs_info = TAEUL_16GUNG_INFO.get(gyesin, ('?', None, False))

        # v1.2 확장
        hapsin = self.get_hapsin(y)
        jeongmok = self.get_jeongmok(y)
        jeongsan = self.get_jeongsan(y)
        jeong_dj = self.get_jeong_daejang(y)
        jeong_cj = self.get_jeong_chamjang(y)
        yeon_gwae = self.get_yeon_gwae_detail(y)
        samgi = self.get_samgi(y)
        obok = self.get_obok(y)
        daeyu = self.get_daeyu(y)
        soyu = self.get_soyu(y)
        sasin = self.get_sasin(y)
        cheonul = self.get_cheonul(y)
        jieul = self.get_jieul(y)
        eumyangsu_detail = self.get_eumyangsu_detail(y)

        return {
            'target_year': y,
            'year_ganji': year_ganji,
            'grand_jeokyeon': grand_jy,
            'ipseongsu': ips,
            'guk': guk,
            'dunbeop': dunbeop,
            'won': won,
            'jaegung': jaegung,
            'gyesin': gyesin,
            'gyesin_name': gs_info[0],
            'cheonmok': cheonmok,
            'cheonmok_name': cm_info[0],
            'gaekmok': gaekmok,
            'gaekmok_name': gm_info[0],
            'jusan': jusan,
            'gaeksan': gaeksan,
            'seungpae': seungpae,
            'jangdan': jangdan,
            'ju_daejang': ju_dj,
            'ju_chamjang': ju_cj,
            'gaek_daejang': gaek_dj,
            'gaek_chamjang': gaek_cj,
            'gyeokguk': gyeokguk,
            'palmun': palmun,
            'palmun_gil': palmun_gil,
            'eumyangsu': eumyangsu,
            'samjaesu': samjaesu,
            'dongji_ganji': dongji,
            'win_probability': win_prob,
            'naeeum_seungpae': naeeum,
            'yang9_yin6': yang9yin6,
            'score': score,
            'verdict': verdict,
            # v1.2 확장
            'hapsin': hapsin,
            'jeongmok': jeongmok,
            'jeongsan': jeongsan,
            'jeong_daejang': jeong_dj,
            'jeong_chamjang': jeong_cj,
            'yeon_gwae': yeon_gwae,
            'samgi': samgi,
            'obok': obok,
            'daeyu': daeyu,
            'soyu': soyu,
            'sasin': sasin,
            'cheonul': cheonul,
            'jieul': jieul,
            'eumyangsu_detail': eumyangsu_detail,
        }

    def yearly_analysis(self, start_year, span=10):
        return [self.full_analysis(y) for y in range(start_year, start_year + span)]