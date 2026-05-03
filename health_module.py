# -*- coding: utf-8 -*-
"""
health_module.py — 건강분석 모듈 v2.0
삼혼·삼령·삼신 체계 + 오장육부 + 본심본태양 + 산삼 약리학
천부경 주해 인산 김일훈 해설 기반
"""
from constants import (
    OHAENG_GAN, OHAENG_JI, SANG_SAENG, SANG_GEUK,
    SAMHON, SAMRYEONG, SAMSIN,
    OJANG_OHAENG, CHILGONG, OMO,
    BONSHIM_TAEYANG,
    SANSAM_OHAENG_RATIO, SANSAM_CHEONGAN_JANGBU, SANSAM_DIRECTION,
    TAEUL_GUNG_NAME,
)


class HealthModule:
    """
    천부경 인체론 기반 건강분석.
    析三極無盡本 → 삼신·삼령·삼혼이 인체에서 무한히 분화.
    本心本太陽 → 심장=태양=지중화구의 삼위일체.
    """

    def __init__(self, year_gan, year_ji, taeul_ohaeng, birth_hour=None):
        """
        year_gan: 년간 (甲~癸)
        year_ji: 년지 (子~亥)
        taeul_ohaeng: 태을재궁 오행
        birth_hour: 출생시 (건강 상세 분석용)
        """
        self.year_gan = year_gan
        self.year_ji = year_ji
        self.gan_ohaeng = OHAENG_GAN.get(year_gan, '土')
        self.ji_ohaeng = OHAENG_JI.get(year_ji, '土')
        self.taeul_ohaeng = taeul_ohaeng
        self.birth_hour = birth_hour

    # ═══════════════════════════════════════
    # A. 삼혼·삼령·삼신 분석
    # ═══════════════════════════════════════

    def analyze_samhon(self):
        """삼혼(三魂) 분석 — 간(肝)이 간직하는 세 혼"""
        results = {}
        for name, info in SAMHON.items():
            # 년간 오행과 혼의 오행 관계
            hon_oh = info['오행']
            if SANG_SAENG.get(self.gan_ohaeng) == hon_oh:
                relation = '상생(我生) — 혼이 잘 양육됨'
                status = '良好'
            elif SANG_SAENG.get(hon_oh) == self.gan_ohaeng:
                relation = '상생(生我) — 혼으로부터 힘을 받음'
                status = '良好'
            elif SANG_GEUK.get(self.gan_ohaeng) == hon_oh:
                relation = '상극(我剋) — 혼을 지나치게 억누름'
                status = '注意'
            elif SANG_GEUK.get(hon_oh) == self.gan_ohaeng:
                relation = '상극(剋我) — 혼이 본체를 침범'
                status = '警告'
            elif self.gan_ohaeng == hon_oh:
                relation = '비화(比和) — 안정적'
                status = '安定'
            else:
                relation = '무관'
                status = '平'
            results[name] = {
                'info': info,
                'relation': relation,
                'status': status,
            }
        return results

    def analyze_samryeong(self):
        """삼령(三靈) 분석 — 혼이 따르는 세 영"""
        results = {}
        for name, info in SAMRYEONG.items():
            ryeong_oh = info['오행']
            if self.gan_ohaeng == ryeong_oh:
                status = '활성'
            elif SANG_SAENG.get(self.gan_ohaeng) == ryeong_oh:
                status = '성장'
            elif SANG_GEUK.get(ryeong_oh) == self.gan_ohaeng:
                status = '억제'
            else:
                status = '보통'
            results[name] = {
                'function': info['기능'],
                'ohaeng': ryeong_oh,
                'status': status,
            }
        return results

    def analyze_samsin(self):
        """삼신(三神) 분석 — 생명의 힘"""
        results = {}
        for name, info in SAMSIN.items():
            sin_oh = info['오행']
            organ = info['대응']
            organ_info = OJANG_OHAENG.get(organ, {})
            if SANG_SAENG.get(self.taeul_ohaeng) == sin_oh:
                status = '시운이 신을 돕는 길한 흐름'
            elif SANG_GEUK.get(self.taeul_ohaeng) == sin_oh:
                status = '시운이 신을 억누르는 주의 구간'
            else:
                status = '보통'
            results[name] = {
                'function': info['기능'],
                'ohaeng': sin_oh,
                'organ': organ,
                'organ_emotion': organ_info.get('정서', '?'),
                'status': status,
            }
        return results

    # ═══════════════════════════════════════
    # B. 오장육부 상세 분석
    # ═══════════════════════════════════════

    def analyze_ojang(self):
        """오장(五臟) 상세 — 년간 오행 기준"""
        results = {}
        for jang, info in OJANG_OHAENG.items():
            jang_oh = info['오행']

            # 년간과의 관계
            if self.gan_ohaeng == jang_oh:
                strength = '왕성(旺) — 본 오행과 동일'
            elif SANG_SAENG.get(self.gan_ohaeng) == jang_oh:
                strength = '상(相) — 본 오행이 생해줌'
            elif SANG_SAENG.get(jang_oh) == self.gan_ohaeng:
                strength = '휴(休) — 이미 힘을 쏟은 상태'
            elif SANG_GEUK.get(self.gan_ohaeng) == jang_oh:
                strength = '수(囚) — 본 오행이 극하여 약화'
            elif SANG_GEUK.get(jang_oh) == self.gan_ohaeng:
                strength = '사(死) — 극을 받아 가장 약함'
            else:
                strength = '평(平)'

            # 태을 시운과의 관계
            if self.taeul_ohaeng == jang_oh:
                taeul_effect = '시운 강화'
            elif SANG_GEUK.get(self.taeul_ohaeng) == jang_oh:
                taeul_effect = '시운 억제 — 주의'
            elif SANG_SAENG.get(self.taeul_ohaeng) == jang_oh:
                taeul_effect = '시운 생조 — 양호'
            else:
                taeul_effect = '시운 무관'

            results[jang] = {
                'ohaeng': jang_oh,
                'bu': info['부'],
                'gong': info['공'],
                'mo': info['모'],
                'emotion': info['정서'],
                'strength': strength,
                'taeul_effect': taeul_effect,
            }
        return results

    # ═══════════════════════════════════════
    # C. 칠공오모 (七孔五毛)
    # ═══════════════════════════════════════

    def analyze_chilgong_omo(self):
        """
        칠공(七孔)은 삼혼칠백(三魂七魄)에 응하고
        오모(五毛)는 삼정오신(三精五神)에 응한다.
        — 천부경 주해 오칠일묘연(五七一妙衍)
        """
        return {
            'chilgong': {
                'count': 7,
                'list': CHILGONG,
                'meaning': '삼혼칠백(三魂七魄)에 응함',
                'cheonbu': '七 = 칠요운(七曜運) — 일월화수목금토',
            },
            'omo': {
                'count': 5,
                'list': OMO,
                'meaning': '삼정오신(三精五神)에 응함',
                'cheonbu': '五 = 오행성(五行星) — 목화토금수',
            },
            'il': {
                'count': 1,
                'meaning': '일심(一心) — 모든 것의 중심',
                'cheonbu': '一 = 추성(樞星) — 북극성',
            },
            'total': '五七一妙衍 — 5×7=35, 하나를 중심으로 신묘하게 불어남',
        }

    # ═══════════════════════════════════════
    # D. 본심본태양
    # ═══════════════════════════════════════

    def analyze_bonshim(self):
        """본심본태양 — 심장=태양=지중화구의 삼위일체"""
        results = {}
        for name, info in BONSHIM_TAEYANG.items():
            results[name] = {
                'correspondence': info['대응'],
                'ohaeng': info['오행'],
                'function': info['기능'],
            }

        # 심장(火) 상태 판정
        heart_oh = '火'
        if SANG_GEUK.get(self.taeul_ohaeng) == heart_oh:
            heart_status = '시운이 심장(火)을 극함 — 심혈관 주의'
        elif SANG_SAENG.get(self.taeul_ohaeng) == heart_oh:
            heart_status = '시운이 심장(火)을 생함 — 활력 양호'
        elif self.taeul_ohaeng == heart_oh:
            heart_status = '시운과 심장이 비화 — 과열 주의'
        else:
            heart_status = '심장 상태 보통'

        results['heart_status'] = heart_status
        return results

    # ═══════════════════════════════════════
    # E. 산삼 약리학 참조
    # ═══════════════════════════════════════

    def get_sansam_analysis(self):
        """산삼 생장년도(천간)별 장부 대응 및 오행성 정기 배분"""
        jangbu = SANSAM_CHEONGAN_JANGBU.get(self.year_gan)
        if not jangbu:
            return None

        jang, bu, oh, desc = jangbu
        direction = SANSAM_DIRECTION.get(oh, '中')

        return {
            'year_gan': self.year_gan,
            'target_organ': jang,
            'target_bu': bu,
            'ohaeng': oh,
            'description': desc,
            'sansam_direction': direction,
            'ohaeng_ratio': SANSAM_OHAENG_RATIO,
            'note': (
                f"산삼이 {self.year_gan}년에 생장하면 "
                f"{jang}({bu}) 기를 통하여 보음보양하며, "
                f"상강시절에 싹이 {direction}방으로 쓰러짐"
            ),
        }

    # ═══════════════════════════════════════
    # F. 종합 건강 리포트
    # ═══════════════════════════════════════

    def full_health_report(self):
        """전체 건강 분석 통합"""
        return {
            'basic': {
                'year_gan': self.year_gan,
                'year_ji': self.year_ji,
                'gan_ohaeng': self.gan_ohaeng,
                'taeul_ohaeng': self.taeul_ohaeng,
            },
            'samhon': self.analyze_samhon(),
            'samryeong': self.analyze_samryeong(),
            'samsin': self.analyze_samsin(),
            'ojang': self.analyze_ojang(),
            'chilgong_omo': self.analyze_chilgong_omo(),
            'bonshim': self.analyze_bonshim(),
            'sansam': self.get_sansam_analysis(),
        }