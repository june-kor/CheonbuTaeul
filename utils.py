# -*- coding: utf-8 -*-
"""
utils.py — 천부태을 v2.0 유틸리티 함수 (변경 없음)
"""


def validate_date(date_str):
    try:
        parts = date_str.split('-')
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1900 <= y <= 2100): return False, "년도는 1900~2100 사이여야 합니다."
        if not (1 <= m <= 12):      return False, "월은 1~12 사이여야 합니다."
        if not (1 <= d <= 31):      return False, "일은 1~31 사이여야 합니다."
        from datetime import date
        date(y, m, d)
        return True, ""
    except Exception:
        return False, "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"


def validate_hour(hour):
    try:
        h = int(hour)
        if 0 <= h <= 23: return True, ""
        return False, "시는 0~23 사이여야 합니다."
    except Exception:
        return False, "시는 숫자여야 합니다."


def validate_blood(blood):
    if blood.upper() in ('A', 'B', 'O', 'AB'): return True, ""
    return False, "혈액형은 A, B, O, AB 중 하나여야 합니다."


def validate_name(name):
    if len(name) < 2: return False, "이름은 2자 이상이어야 합니다."
    return True, ""


def score_bar(score, max_score, width=30):
    ratio = score / max_score if max_score > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = '█' * filled + '░' * empty
    pct = ratio * 100
    return f"[{bar}] {score}/{max_score} ({pct:.0f}%)"