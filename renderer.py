# -*- coding: utf-8 -*-
"""
renderer.py — 출력 엔진 v2.0
텍스트 방위도, 게이지 바, 비즈니스 리포트, 건강 리포트 출력
모든 시각화는 v1 = 텍스트 그래프
"""
from constants import (
    TAEUL_GUNG_NAME, TAEUL_16GUNG_INFO, TAEUL_JEONGGUNG_NUM,
    PALMUN_ORDER, PALMUN_GIL, PALMUN_GUNG, PALMUN_ZONE,
    GUNG_DIRECTION, SANG_SAENG, SANG_GEUK,
)

class Renderer:
    """터미널 출력 전담"""

    # ═══════════════════════════════════════
    # A. 게이지 바
    # ═══════════════════════════════════════

    @staticmethod
    def gauge_bar(value, max_value, width=30, label='', color_char='█'):
        """터미널 게이지 바"""
        ratio = value / max_value if max_value > 0 else 0
        filled = int(ratio * width)
        empty = width - filled
        bar = color_char * filled + '░' * empty
        pct = ratio * 100
        return f"  {label:10s} [{bar}] {value}/{max_value} ({pct:.0f}%)"

    @staticmethod
    def dual_gauge(jusan, gaeksan, jeongsan=None, max_val=33):
        """주산·객산·정산 이중/삼중 게이지 — max_val 동적 보정"""
        # 동적 max_val: 실제 값 중 최대치 기준
        actual_max = max(jusan, gaeksan, jeongsan or 0, max_val)
        lines = []
        lines.append(Renderer.gauge_bar(jusan, actual_max, label='주산(主算)', color_char='█'))
        lines.append(Renderer.gauge_bar(gaeksan, actual_max, label='객산(客算)', color_char='▓'))
        if jeongsan is not None:
            lines.append(Renderer.gauge_bar(jeongsan, actual_max, label='정산(定算)', color_char='▒'))
        total = jusan + gaeksan
        win = round(jusan / total * 100, 1) if total > 0 else 50.0
        lines.append(f"  {'─' * 52}")
        lines.append(f"  승산지수: {win}%")
        return '\n'.join(lines)
	
	# ═══════════════════════════════════════
    # B. 방위도 (16신 배치)
    # ═══════════════════════════════════════

    @staticmethod
    def bangwido(taeul_result):
        """텍스트 방위도 — 16신 + 태을·천목·객목·계신 마커 (간신 포함)"""
        jaegung = taeul_result.get('jaegung', {})
        taeul_gung = jaegung.get('gung_num', 5) if isinstance(jaegung, dict) else 5
        cheonmok = taeul_result.get('cheonmok', '')
        gaekmok = taeul_result.get('gaekmok', '')
        gyesin = taeul_result.get('gyesin', '')

        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        gm_gung = TAEUL_JEONGGUNG_NUM.get(gaekmok)
        gs_gung = TAEUL_JEONGGUNG_NUM.get(gyesin)

        def mark(gung_num):
            marks = []
            if gung_num == taeul_gung: marks.append('★')
            if gung_num == cm_gung:    marks.append('◆')
            if gung_num == gm_gung:    marks.append('▲')
            if gung_num == gs_gung:    marks.append('●')
            return ''.join(marks) if marks else '  '

        def cell(gung_num):
            info = TAEUL_GUNG_NAME.get(gung_num, ('?','?','?','?'))
            m = mark(gung_num)
            return f"{gung_num}{info[0]}{m:4s}"

        lines = []
        lines.append("  ┌─────────┬─────────┬─────────┐")
        lines.append(f"  │ {cell(9):7s} │ {cell(2):7s} │ {cell(7):7s} │")
        lines.append(f"  │ 巽 東南  │ 離 正南  │ 坤 西南  │")
        lines.append("  ├─────────┼─────────┼─────────┤")
        lines.append(f"  │ {cell(4):7s} │  5中不入 │ {cell(6):7s} │")
        lines.append(f"  │ 震 正東  │  (樞紐)  │ 兌 正西  │")
        lines.append("  ├─────────┼─────────┼─────────┤")
        lines.append(f"  │ {cell(3):7s} │ {cell(8):7s} │ {cell(1):7s} │")
        lines.append(f"  │ 艮 東北  │ 坎 正北  │ 乾 西北  │")
        lines.append("  └─────────┴─────────┴─────────┘")
        lines.append("")
        lines.append("  ★=태을  ◆=천목(文昌)  ▲=객목(始擊)  ●=계신")

        # 간신(間神) 위치 표시 — 정궁이 아닌 신살
        gansin_lines = []
        if cm_gung is None and cheonmok:
            info = TAEUL_16GUNG_INFO.get(cheonmok, ('?', None, False))
            name = info[0] if isinstance(info, (tuple, list)) else '?'
            gansin_lines.append(f"  ◆ 천목(文昌) = {cheonmok}({name}) — 間神 위치 (정궁 사이)")
        if gm_gung is None and gaekmok:
            info = TAEUL_16GUNG_INFO.get(gaekmok, ('?', None, False))
            name = info[0] if isinstance(info, (tuple, list)) else '?'
            gansin_lines.append(f"  ▲ 객목(始擊) = {gaekmok}({name}) — 間神 위치 (정궁 사이)")
        if gs_gung is None and gyesin:
            info = TAEUL_16GUNG_INFO.get(gyesin, ('?', None, False))
            name = info[0] if isinstance(info, (tuple, list)) else '?'
            gansin_lines.append(f"  ● 계신(計神) = {gyesin}({name}) — 間神 위치 (정궁 사이)")

        if gansin_lines:
            lines.append("")
            lines.append("  ── 間神 위치 (구궁도 밖) ──")
            lines.extend(gansin_lines)

        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # C. 팔문 방위 차트
    # ═══════════════════════════════════════

    @staticmethod
    def palmun_chart():
        """팔문 길흉 방위 차트"""
        lines = []
        lines.append("  ┌────────┬────────┬────────┐")

        layout = [
            [(9,'巽','杜'), (2,'離','景'), (7,'坤','死')],
            [(4,'震','傷'), (5,'中','—'),  (6,'兌','驚')],
            [(3,'艮','生'), (8,'坎','休'), (1,'乾','開')],
        ]

        for row_idx, row in enumerate(layout):
            cells = []
            for gung, gwe, mun in row:
                if gung == 5:
                    cells.append(" 中 不入 ")
                else:
                    gil = PALMUN_GIL.get(mun, '?')
                    zone = PALMUN_ZONE.get(mun, ('Gray',''))[0]
                    zone_mark = {'Blue':'○','Red':'✕','Yellow':'△','Gray':'·'}.get(zone, ' ')
                    cells.append(f"{zone_mark}{mun}門{gil[:2]:2s}")
            lines.append(f"  │{'│'.join(f'{c:8s}' for c in cells)}│")

            if row_idx < 2:
                lines.append("  ├────────┼────────┼────────┤")

        lines.append("  └────────┴────────┴────────┘")
        lines.append("")
        lines.append("  ○=Blue(유망)  ✕=Red(주의)  △=Yellow(경계)  ·=Gray(관망)")
        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # D. 비즈니스 리포트 출력
    # ═══════════════════════════════════════

    @staticmethod
    def business_report(report_data, year_info=''):
        """
        interpreter.generate_report() 결과를 텍스트 리포트로 출력
        """
        lines = []
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"  ▣ 태을 비즈니스 리포트 — {year_info}")
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        wp = report_data.get('win_probability', {})
        lines.append(f"  ■ 현재 국면: [{report_data.get('current_task', '?')}]")
        lines.append(f"  ■ 승산 지수: {wp.get('probability', '?')}% ({wp.get('label', '?')})")

        lines.append(f"  ■ 핵심 액티비티:")
        for act in report_data.get('activities', []):
            lines.append(f"    → {act}")

        risks = report_data.get('risk_factors', [])
        if risks:
            lines.append(f"  ■ 리스크 팩터:")
            for r in risks:
                lines.append(f"    → {r}")

        directions = report_data.get('directions', [])
        if directions:
            best = directions[0]
            lines.append(f"  ■ 전략 방위: {best.get('direction', '?')} ({best.get('meaning', '')})")

        health = report_data.get('health', {})
        if health:
            lines.append(f"  ■ 건강 참고: {health.get('overall', '?')}")

        lines.append("")
        summary = report_data.get('executive_summary', '')
        if summary:
            lines.append(f"  ■ Executive Summary:")
            # 80자 단위로 줄바꿈
            while summary:
                lines.append(f"    {summary[:76]}")
                summary = summary[76:]

        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # E. 건강 리포트 출력
    # ═══════════════════════════════════════

    @staticmethod
    def health_report(health_data, blood_analysis=None):
        """health_module.full_health_report() 결과를 텍스트로 출력"""
        lines = []
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("  ▣ 건강분석 — 삼혼·삼령·삼신 + 오장 + 본심본태양")
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        basic = health_data.get('basic', {})
        lines.append(f"  년간: {basic.get('year_gan','?')}({basic.get('gan_ohaeng','?')}) "
                     f"| 시운: {basic.get('taeul_ohaeng','?')}")

        # 사상체질 정보 (혈액형 기반)
        if blood_analysis:
            sasang = blood_analysis.get('sasang', '')
            elem = blood_analysis.get('element', '')
            organ_big = blood_analysis.get('organ_big', '')
            organ_small = blood_analysis.get('organ_small', '')
            color = blood_analysis.get('color', '')
            herb = blood_analysis.get('herb_note', '')
            desc = blood_analysis.get('description', '')

            lines.append("")
            lines.append("  ┌─ 사상체질 (인산의학 혈액형 기반) ───────┐")
            lines.append(f"  │ 체질: {sasang} ({elem})")
            lines.append(f"  │ {desc}")
            lines.append(f"  │ 대장부(大): {organ_big}")
            lines.append(f"  │ 소장부(小): {organ_small}")
            lines.append(f"  │ 흡수색소: {color}")
            lines.append(f"  │ 약재참고: {herb}")
            note = blood_analysis.get('note', '')
            if note:
                lines.append(f"  │ ※ {note}")
            lines.append("  └────────────────────────────────────────┘")

        lines.append("")

        # 삼혼
        lines.append("  ┌─ 삼혼(三魂) — 간(肝)이 간직 ──────────┐")
        for name, info in health_data.get('samhon', {}).items():
            lines.append(f"  │ {name}: {info['relation']} [{info['status']}]")
        lines.append("  └────────────────────────────────────────┘")

        # 삼신
        lines.append("  ┌─ 삼신(三神) — 생명의 힘 ──────────────┐")
        for name, info in health_data.get('samsin', {}).items():
            lines.append(f"  │ {name}({info['organ']}): {info['status']}")
        lines.append("  └────────────────────────────────────────┘")

        # 오장
        lines.append("  ┌─ 오장(五臟) 상세 ─────────────────────┐")
        for jang, info in health_data.get('ojang', {}).items():
            lines.append(f"  │ {jang}({info['ohaeng']}): {info['strength']}")
            lines.append(f"  │   시운영향: {info['taeul_effect']}")
        lines.append("  └────────────────────────────────────────┘")

        # 체질-년간 교차 분석
        if blood_analysis:
            gan_oh = basic.get('gan_ohaeng', '?')
            sasang_elem = blood_analysis.get('element', '?')
            if gan_oh == sasang_elem:
                cross = '년간과 체질 오행이 동일(比和) — 체질 특성이 극대화됨, 편중 주의'
            elif SANG_SAENG.get(gan_oh) == sasang_elem:
                cross = f'년간({gan_oh})이 체질({sasang_elem})을 생함 — 체질 장부가 과잉 활성, 절제 필요'
            elif SANG_SAENG.get(sasang_elem) == gan_oh:
                cross = f'체질({sasang_elem})이 년간({gan_oh})을 생함 — 에너지 소모가 큼, 보양 필요'
            elif SANG_GEUK.get(gan_oh) == sasang_elem:
                cross = f'년간({gan_oh})이 체질({sasang_elem})을 극함 — 체질 장부 약화 주의!'
            elif SANG_GEUK.get(sasang_elem) == gan_oh:
                cross = f'체질({sasang_elem})이 년간({gan_oh})을 극함 — 과로 주의'
            else:
                cross = '년간과 체질이 특별한 상극·상생 없음'
            lines.append(f"  ● 체질-년간 교차: {cross}")

        # 본심본태양
        bonshim = health_data.get('bonshim', {})
        heart_status = bonshim.get('heart_status', '?')
        lines.append(f"  ● 본심본태양: {heart_status}")

        # 산삼
        sansam = health_data.get('sansam')
        if sansam:
            lines.append(f"  ● 산삼참조: {sansam.get('note', '')}")

        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # F. 점술 결과 출력
    # ═══════════════════════════════════════

    @staticmethod
    def divination_report(div_result):
        """divination.divine() 결과를 텍스트로 출력"""
        lines = []
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"  ▣ 태을육임 점사 — {div_result.get('category', '?')}")
        lines.append(f"  ■ 점시: {div_result.get('timestamp', '?')}")
        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        fl = div_result.get('four_layer', {})
        lines.append("  ┌─ 4중 포국 ─────────────────────────────┐")
        for layer_name, label in [('year','歲'), ('month','月'), ('day','日'), ('hour','時')]:
            layer = fl.get(layer_name, {})
            gn = layer.get('gung_name', layer.get('gung', {}).get('gwe_name', '?') if isinstance(layer.get('gung'), dict) else '?')
            guk = layer.get('guk', '?')
            lines.append(f"  │ {label}계: 제{guk}국 → {gn}")
        lines.append("  └────────────────────────────────────────┘")

        wp = div_result.get('win_probability', 50)
        lines.append(f"  승산 지수: {wp}%")
        lines.append("")

        cat_advice = div_result.get('category_advice', '')
        lines.append(f"  ■ 점사 결과:")
        lines.append(f"    {cat_advice}")

        lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # G. 종합 점수 시각화
    # ═══════════════════════════════════════

    @staticmethod
    def score_summary(scores, verdict):
        """종합 점수 게이지"""
        lines = []
        lines.append(Renderer.gauge_bar(scores.get('cheonbu', 0), 40, label='천부경(體)'))
        lines.append(Renderer.gauge_bar(scores.get('taeul', 0), 40, label='태을신수(用)'))
        lines.append(Renderer.gauge_bar(scores.get('cross', 0), 20, label='교차분석'))
        lines.append(f"  {'─' * 52}")
        lines.append(Renderer.gauge_bar(scores.get('total', 0), 100, label=f'종합({verdict})'))
        return '\n'.join(lines)

    # ═══════════════════════════════════════
    # H. 방위도 — 24방위 원형 차트 (v1 텍스트)
    # ═══════════════════════════════════════

    @staticmethod
    def full_bangwido(taeul_result):
        """
        24방위 원형 방위도 (텍스트 v1)
        중심: 태을(太乙) 재궁
        내환: 주기(主基)·객기(客基) — 주대장/객대장
        중환: 팔문(八門)
        외환: 16신 배치 + 공망 표시
        """
        # ── 데이터 추출 ──
        jaegung = taeul_result.get('jaegung', {})
        taeul_gung = jaegung.get('gung_num', 5) if isinstance(jaegung, dict) else 5
        taeul_name = jaegung.get('gwe_name', '?') if isinstance(jaegung, dict) else '?'
        taeul_oh = jaegung.get('ohaeng', '?') if isinstance(jaegung, dict) else '?'

        cheonmok = taeul_result.get('cheonmok', '')
        gaekmok = taeul_result.get('gaekmok', '')
        gyesin = taeul_result.get('gyesin', '')

        ju_dj = taeul_result.get('ju_daejang', '')
        ju_cj = taeul_result.get('ju_chamjang', '')
        gaek_dj = taeul_result.get('gaek_daejang', '')
        gaek_cj = taeul_result.get('gaek_chamjang', '')

        palmun = taeul_result.get('palmun', '?')
        palmun_gil = taeul_result.get('palmun_gil', '?')

        gyeokguk = taeul_result.get('gyeokguk', {})
        gk_type = gyeokguk.get('type', '?') if isinstance(gyeokguk, dict) else '?'

        win_prob = taeul_result.get('win_probability', 50.0)
        seungpae = taeul_result.get('seungpae', '?')

        # ── 16신 위치 매핑 ──
        from constants import (
            TAEUL_16_ORDER, TAEUL_16GUNG_INFO, TAEUL_JEONGGUNG_NUM,
            TAEUL_GUNG_NAME, PALMUN_GIL, PALMUN_GUNG, PALMUN_ZONE,
            GUNG_DIRECTION,
        )

        cm_gung = TAEUL_JEONGGUNG_NUM.get(cheonmok)
        gm_gung = TAEUL_JEONGGUNG_NUM.get(gaekmok)
        gs_gung = TAEUL_JEONGGUNG_NUM.get(gyesin)

        # ── 마커 함수 ──
        def gung_markers(gn):
            m = []
            if gn == taeul_gung: m.append('太')
            if gn == cm_gung:    m.append('文')
            if gn == gm_gung:    m.append('始')
            if gn == gs_gung:    m.append('計')
            if gn == ju_dj:      m.append('主')
            if gn == gaek_dj:    m.append('客')
            return ','.join(m) if m else '·'

        def sin16_marker(name16):
            info = TAEUL_16GUNG_INFO.get(name16, ('?', None, False))
            sin_name = info[0]
            is_jeonggung = info[2]
            markers = []
            if name16 == cheonmok: markers.append('◆文')
            if name16 == gaekmok:  markers.append('▲始')
            if name16 == gyesin:   markers.append('●計')
            mark_str = ' '.join(markers) if markers else ''
            return sin_name, is_jeonggung, mark_str

        # ── 팔문 궁별 배치 ──
        palmun_map = {}
        for mun, gn in PALMUN_GUNG.items():
            zone = PALMUN_ZONE.get(mun, ('Gray', ''))[0]
            palmun_map[gn] = {'name': mun, 'gil': PALMUN_GIL.get(mun, '?'), 'zone': zone}

        # ── 출력 조립 ──
        lines = []
        lines.append("  ╔══════════════════════════════════════════════════════════╗")
        lines.append("  ║          24방위 태을신수 방위도 (Layout Chart)           ║")
        lines.append("  ╠══════════════════════════════════════════════════════════╣")
        lines.append("")

        # 외환: 16신 원형 배치 (텍스트 근사)
        #
        #              巽(大炅)
        #        巳(大神)      辰(太陽)
        #    午(大威)              卯(高叢)
        # 坤(大武)     [중심]       艮(和德)
        #    未(天道)              寅(呂申)
        #        申(武德)      丑(陽德)
        #              乾(陰德)
        #        戌(陰主)      亥(大義)
        #              子(地主)

        # 상단 (남방: 巽9 — 離2 — 坤7)
        s9 = sin16_marker('巽')
        s_sa = sin16_marker('巳')
        s_jin = sin16_marker('辰')
        s2 = sin16_marker('午')
        s7 = sin16_marker('未')
        s_gon = sin16_marker('坤')

        # 중단 (동서: 震4 — 中5 — 兌6)
        s4 = sin16_marker('卯')
        s6 = sin16_marker('酉')
        s_in = sin16_marker('寅')
        s_sin = sin16_marker('申')

        # 하단 (북방: 艮3 — 坎8 — 乾1)
        s3 = sin16_marker('艮')
        s8 = sin16_marker('子')
        s1 = sin16_marker('乾')
        s_chuk = sin16_marker('丑')
        s_hae = sin16_marker('亥')
        s_sul = sin16_marker('戌')

        lines.append("  ── 외환: 16신(十六神) 배치 ──")
        lines.append("")
        lines.append(f"                         巽 {s9[0]:4s} {s9[2]}")
        lines.append(f"                  巳 {s_sa[0]:4s} {s_sa[2]}     辰 {s_jin[0]:4s} {s_jin[2]}")
        lines.append(f"           午 {s2[0]:4s} {s2[2]}                       卯 {s4[0]:4s} {s4[2]}")
        lines.append(f"     坤 {s_gon[0]:4s} {s_gon[2]}                             艮 {s3[0]:4s} {s3[2]}")
        lines.append(f"           未 {s7[0]:4s} {s7[2]}                       寅 {s_in[0]:4s} {s_in[2]}")
        lines.append(f"                  申 {s_sin[0]:4s} {s_sin[2]}     丑 {s_chuk[0]:4s} {s_chuk[2]}")
        lines.append(f"                         乾 {s1[0]:4s} {s1[2]}")
        lines.append(f"                  戌 {s_sul[0]:4s} {s_sul[2]}     亥 {s_hae[0]:4s} {s_hae[2]}")
        lines.append(f"                         子 {s8[0]:4s} {s8[2]}")
        lines.append("")

        # 중환: 팔문 배치
        lines.append("  ── 중환: 팔문(八門) 길흉 방위 ──")
        lines.append("")
        lines.append("  ┌────────────┬────────────┬────────────┐")

        gung_layout = [
            [9, 2, 7],
            [4, 5, 6],
            [3, 8, 1],
        ]
        dir_label = {
            9: '東南', 2: '正南', 7: '西南',
            4: '正東', 5: '中央', 6: '正西',
            3: '東北', 8: '正北', 1: '西北',
        }

        for row_idx, row in enumerate(gung_layout):
            cells = []
            for gn in row:
                if gn == 5:
                    cells.append("  中 不入   ")
                else:
                    pm = palmun_map.get(gn, {'name':'?', 'gil':'?', 'zone':'Gray'})
                    zone_mark = {'Blue': '○', 'Red': '✕', 'Yellow': '△', 'Gray': '·'}.get(pm['zone'], ' ')
                    mk = gung_markers(gn)
                    cells.append(f"{zone_mark}{pm['name']}門{pm['gil'][:2]:2s}{mk:>3s}")
            lines.append(f"  │{'│'.join(f'{c:12s}' for c in cells)}│")

            sub_cells = []
            for gn in row:
                gname = TAEUL_GUNG_NAME.get(gn, ('?','?','?','?'))
                dl = dir_label.get(gn, '?')
                if gn == 5:
                    sub_cells.append("   (樞紐)   ")
                else:
                    sub_cells.append(f" {gn}{gname[0]} {dl:4s}   ")
            lines.append(f"  │{'│'.join(f'{c:12s}' for c in sub_cells)}│")

            if row_idx < 2:
                lines.append("  ├────────────┼────────────┼────────────┤")

        lines.append("  └────────────┴────────────┴────────────┘")
        lines.append("")

        # 내환: 주기·객기 (주대장/객대장)
        lines.append("  ── 내환: 주기(主基)·객기(客基) ──")
        lines.append("")

        ju_dj_name = TAEUL_GUNG_NAME.get(ju_dj, ('?','?','?','?')) if isinstance(ju_dj, int) else ('?','?','?','?')
        ju_cj_name = TAEUL_GUNG_NAME.get(ju_cj, ('?','?','?','?')) if isinstance(ju_cj, int) else ('?','?','?','?')
        gaek_dj_name = TAEUL_GUNG_NAME.get(gaek_dj, ('?','?','?','?')) if isinstance(gaek_dj, int) else ('?','?','?','?')
        gaek_cj_name = TAEUL_GUNG_NAME.get(gaek_cj, ('?','?','?','?')) if isinstance(gaek_cj, int) else ('?','?','?','?')

        ju_dir = GUNG_DIRECTION.get(ju_dj, '?') if isinstance(ju_dj, int) else '?'
        gaek_dir = GUNG_DIRECTION.get(gaek_dj, '?') if isinstance(gaek_dj, int) else '?'

        lines.append(f"  ┌─ 主(나) ────────────────────────────────┐")
        lines.append(f"  │ 주대장: {ju_dj}궁 {ju_dj_name[0]}({ju_dj_name[1]}) → {ju_dir}")
        lines.append(f"  │ 주참장: {ju_cj}궁 {ju_cj_name[0]}({ju_cj_name[1]})")
        lines.append(f"  ├─ 客(상대) ──────────────────────────────┤")
        lines.append(f"  │ 객대장: {gaek_dj}궁 {gaek_dj_name[0]}({gaek_dj_name[1]}) → {gaek_dir}")
        lines.append(f"  │ 객참장: {gaek_cj}궁 {gaek_cj_name[0]}({gaek_cj_name[1]})")
        lines.append(f"  └────────────────────────────────────────┘")
        lines.append("")

        # 중심: 태을 재궁
        taeul_dir = GUNG_DIRECTION.get(taeul_gung, '?')
        lines.append(f"  ── 중심: 태을(太乙) ──")
        lines.append(f"  ┌────────────────────────────────────────┐")
        lines.append(f"  │ 태을재궁: {taeul_gung}궁 {taeul_name}({taeul_oh}) → {taeul_dir}")
        lines.append(f"  │ 격국: {gk_type}  │  팔문직사: {palmun}門({palmun_gil})")
        lines.append(f"  │ 승패: {seungpae}  │  승산지수: {win_prob}%")
        lines.append(f"  └────────────────────────────────────────┘")
        lines.append("")

        # 방위 존 요약
        blue_dirs = []
        red_dirs = []
        for mun, (zone, desc) in PALMUN_ZONE.items():
            gn = PALMUN_GUNG.get(mun)
            d = GUNG_DIRECTION.get(gn, '?')
            if zone == 'Blue':
                blue_dirs.append(f"{d}({mun})")
            elif zone == 'Red':
                red_dirs.append(f"{d}({mun})")

        lines.append(f"  ○ Blue Zone (유망): {', '.join(blue_dirs)}")
        lines.append(f"  ✕ Red Zone (주의): {', '.join(red_dirs)}")

        # 문창 방위
        if cm_gung:
            cm_dir = GUNG_DIRECTION.get(cm_gung, '?')
            lines.append(f"  ◆ 문창(文昌) 방위: {cm_dir} — 기획·문서·계약 유리")
        elif cheonmok:
            info = TAEUL_16GUNG_INFO.get(cheonmok, ('?', None, False))
            lines.append(f"  ◆ 문창(文昌): {cheonmok}({info[0]}) — 間神 위치")

        lines.append("")
        lines.append("  ╚══════════════════════════════════════════════════════════╝")

        return '\n'.join(lines)

