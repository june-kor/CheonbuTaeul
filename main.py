# -*- coding: utf-8 -*-
"""
main.py — 천부태을 天符太乙 v2.0 메인 진입점
경량화: 모든 출력 로직은 renderer.py로 이관
"""
import sys
import io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

from datetime import date
from integration import IntegrationEngine
from divination import DivinationEngine
from renderer import Renderer
from interpreter import Interpreter
from utils import validate_date, validate_hour, validate_blood, validate_name

VERSION = "v2.0"
BANNER = f"""
╔════════════════════════════════════════════════════╗
║          천부태을 天符太乙 {VERSION}               ║
║          一始無始一 … 一終無終一                   ║
║   體(천부경) + 用(태을신수) + 占(태을육임) + 健(건강)  ║
╚════════════════════════════════════════════════════╝"""


def get_mode():
    print("\n  모드 선택:")
    print("  1) 종합 분석 (체용합일)")
    print("  2) 태을육임 점술")
    print("  3) 건강 분석")
    print("  4) 비즈니스 리포트")
    return input("  선택 (1-4): ").strip()


def get_input():
    print(BANNER)
    name = input("  이름 (한글): ").strip()
    birth_date = input("  생년월일 (YYYY-MM-DD): ").strip()
    birth_hour = int(input("  생시 (0-23): ").strip())
    blood_type = input("  혈액형 (A/B/O/AB): ").strip().upper()
    return name, birth_date, birth_hour, blood_type


def run_full_analysis(engine, result):
    """종합 분석 결과 출력 (V2.1 — 세국×명국 교차 개인화 포함)"""
    R = Renderer()
    personal = result.get('personal', {})
    scores = result.get('scores', {})

    name = result.get('name', engine.name)
    print(f"\n{'='*60}")
    print(f"  【 {name} 님 — 종합 분석 리포트 】")
    print(f"{'='*60}")

    # ── 1) 천부경 분석 ──
    cb = result.get('cheonbu', {})
    saju = cb.get('saju', {})
    print(f"\n▶ 천부경 분석")
    if isinstance(saju, dict) and saju:
        print(f"  사주: 年:{saju.get('year','-')} 月:{saju.get('month','-')} 日:{saju.get('day','-')} 時:{saju.get('hour','-')}")
    else:
        print(f"  사주: {cb.get('saju_text', '-')}")
    print(f"  천부 점수: {cb.get('score', '-')}점")

    # ── 2) 태을신수 세국 (당해 연도) ──
    segye = result.get('taeul', {})
    print(f"\n▶ 태을신수 — 세국 (당해)")
    jae = segye.get('jaegung', {})
    print(f"  재궁: {jae.get('gung_num', '-')}궁 ({jae.get('gwe_name', '-')}) [{jae.get('ohaeng', '-')}]")
    gyeok = segye.get('gyeokguk', {})
    print(f"  격국: {gyeok.get('type', '-')} — {gyeok.get('gilhyung', '-')}")
    print(f"  주산: {segye.get('jusan', '-')}  객산: {segye.get('gaeksan', '-')}")
    print(f"  팔문: {segye.get('palmun', '-')} ({segye.get('palmun_gil', '-')})")
    print(f"  승패: {segye.get('seungpae', '-')}")
    print(f"  세국 승산지수: {segye.get('win_probability', 0):.1f}%")

    # ── 3) 태을신수 명국 (생년) — 개인화 레이어 ──
    myeong = result.get('myeong', {})
    if myeong:
        print(f"\n▶ 태을신수 — 명국 (생년 포국)")
        mjae = myeong.get('jaegung', {})
        print(f"  명국 재궁: {mjae.get('gung_num', '-')}궁 ({mjae.get('gwe_name', '-')}) [{mjae.get('ohaeng', '-')}]")
        mgyeok = myeong.get('gyeokguk', {})
        print(f"  명국 격국: {mgyeok.get('type', '-')} — {mgyeok.get('gilhyung', '-')}")
        print(f"  명국 주산: {myeong.get('jusan', '-')}  객산: {myeong.get('gaeksan', '-')}")

    # ── 4) 개인화 교차 분석 ──
    print(f"\n▶ 개인화 교차 분석")
    print(f"  생년 간지: {personal.get('birth_gz', '-')}")
    print(f"  생년 납음: {personal.get('birth_naeum', '-')}")
    print(f"  개인 계신: {personal.get('personal_gyesin', '-')}")
    se_gk = segye.get('gyeokguk', {}).get('type', '-')
    my_gk = myeong.get('gyeokguk', {}).get('type', '-')
    print(f"  세국 격국: {se_gk}  ×  명국 격국: {my_gk}")
    print(f"  → 개인화 격국: {personal.get('personal_gyeok', '-')}")
    print(f"  교차 보정: {personal.get('cross_adj', 0):+.1f}점")
    print(f"  유년괘: {personal.get('flow_gua', '-')}")
    print(f"  ★ 개인화 승산지수: {personal.get('personal_wp', 0):.1f}%")

    # ── 5) 종합 점수 ──
    total = scores.get('total', 0)
    grade = personal.get('personal_grade', result.get('verdict', '-'))
    print(f"\n{'─'*60}")
    print(f"  ★ 종합 점수: {total}점 (천부{scores.get('cheonbu',0)} + 태을{scores.get('taeul',0)} + 교차{scores.get('cross',0)})  |  등급: {grade}")
    print(f"{'─'*60}")

    # ── 6) 게이지 출력 ──
    jusan = segye.get('jusan', 0)
    gaeksan = segye.get('gaeksan', 0)
    jeongsan = jusan + gaeksan if jusan and gaeksan else None
    try:
        gauge = R.dual_gauge(jusan, gaeksan, jeongsan)
        if gauge:
            print(gauge)
    except Exception:
        pass

    # ── 7) 방위도 ──
    try:
        bw = R.bangwido(segye)
        if bw:
            print(f"\n▶ 방위도")
            print(bw)
    except Exception:
        pass

    try:
        fbw = R.full_bangwido(segye)
        if fbw:
            print(fbw)
    except Exception:
        pass

    # ── 8) 건강 분석 ──
    health = result.get('health', {})
    if health:
        # blood_analysis를 cheonbu_core에서 직접 가져옴
        try:
            blood_analysis = engine.cheonbu.get_blood_analysis()
        except Exception:
            blood_analysis = None
        try:
            hr = R.health_report(health, blood_analysis)
            if hr:
                print(f"\n▶ 건강 분석")
                print(hr)
        except Exception:
            pass

    # ── 9) 10년 운 예측 ──
    forecast = result.get('forecast', [])
    if forecast:
        print(f"\n▶ 10년 운세 예측")
        print(f"  {'연도':<6} {'간지':<6} {'점수':>4} {'등급':>4} {'개인WP':>7} {'격국':<10} {'유년괘':<8}")
        print(f"  {'─'*55}")
        for yr_data in forecast:
            yr = yr_data.get('year', '-')
            gj = yr_data.get('ganji', '-')
            sc = yr_data.get('score', '-')
            gr = yr_data.get('verdict', '-')
            pwp = yr_data.get('wp', '-')
            pg = yr_data.get('gyeokguk', '-')
            fg = yr_data.get('gwae', '-')
            if isinstance(pwp, (int, float)):
                print(f"  {yr:<6} {gj:<6} {sc:>4} {gr:>4} {pwp:>6.1f}% {pg:<10} {fg:<8}")
            else:
                print(f"  {yr:<6} {gj:<6} {sc:>4} {gr:>4} {str(pwp):>7} {pg:<10} {fg:<8}")

    print(f"\n{'='*60}")
    print(f"  분석 완료 — {name} 님의 종합 리포트")
    print(f"{'='*60}\n")

def run_divination(cheonbu_engine):
    """점술 모드"""
    from constants import DIVINATION_CATEGORIES
    print("\n  점사 카테고리:")
    cats = list(DIVINATION_CATEGORIES.items())
    for i, (key, name) in enumerate(cats, 1):
        print(f"    {i}) {name}")
    choice = int(input("  선택: ").strip()) - 1
    category = cats[choice][0] if 0 <= choice < len(cats) else 'general'

    div = DivinationEngine(cheonbu_engine)
    result = div.divine(category)
    print(Renderer.divination_report(result))

def run_health(engine, result):
    """건강 분석 모드"""
    health = result.get('health', engine.get_health_analysis())
    blood_analysis = engine.cheonbu.get_blood_analysis()
    print(Renderer.health_report(health, blood_analysis))

def run_business(engine, result):
    """비즈니스 리포트 모드"""
    biz = result.get('business_report', engine.get_business_report())
    year_info = f"{date.today().year}년"
    print(Renderer.business_report(biz, year_info))


def print_forecast(fc):
    if not fc:
        return
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ▣ 10년 운 (年運) 예측")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {'연도':<5} {'간지':<5} {'재궁':<9} {'격국':<4} "
          f"{'팔문':<5} {'음양수':<7} {'연괘':<5} {'점수':<4} {'판정':<5}")
    print("  " + "─" * 56)
    for f in fc:
        print(f"  {f.get('year',''):<5} {f.get('ganji',''):<5} "
              f"{f.get('taeul_gung',''):<9} {f.get('gyeokguk',''):<4} "
              f"{f.get('palmun',''):<5} {f.get('eumyangsu',''):<7} "
              f"{f.get('gwae',''):<5} {f.get('score',''):<4} {f.get('verdict',''):<5}")
    print("  " + "─" * 56)
    print()
    print("  [범례]")
    print("  재궁  = 태을 소재궁 (3년마다 이동, 중궁 불입)")
    print("  격국  = 囚·格·廹·掩·擊·提挾·四郭固·和 (7중 판정)")
    print("  팔문  = 八門直事 (30년 주기 교대 — 동일 기간 내 불변)")
    print("  음양수= 주산의 수와 궁의 음양 조합")
    print("  연괘  = 적년 mod 64 → 주역 64괘")

def main():
    try:
        name, birth_date, birth_hour, blood_type = get_input()
        engine = IntegrationEngine(name, birth_date, birth_hour, blood_type)
        result = engine.full_analysis()

        mode = get_mode()

        if mode == '1':
            run_full_analysis(engine, result)
        elif mode == '2':
            run_divination(engine.cheonbu)
        elif mode == '3':
            run_health(engine, result)
        elif mode == '4':
            run_business(engine, result)
        else:
            run_full_analysis(engine, result)

        print(f"\n  {name}님, 천부태을 v2.0 분석이 완료되었습니다.")
        print("  體(천부경) + 用(태을신수) + 占(태을육임) + 健(건강) = 完全體")

    except KeyboardInterrupt:
        print("\n\n  분석을 중단합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()