"""Series name vocabulary — episode-variant suffix patterns for grouping.

Patterns that indicate a suffix after ・ or inside 【】 is an episode variant,
NOT part of the actual series name.  Extend these lists as new patterns are found.
"""

# ============================================================================
# ・suffix 模式：名・后缀 → 后缀是单集变体，不是剧名的一部分
# ============================================================================

# 颜色词（赤/紫/青/黑/白/红/蓝/绿/金/银 等）
COLOR_WORDS = [
    "赤", "紫", "青", "黑", "白", "红", "蓝", "绿", "金", "银",
    "朱", "碧", "蒼", "翠", "紅", "丹", "紺", "藍",
]

# 日语序数/编号（参=3, 弐=2, 零=0）
JAPANESE_NUMERALS = [
    "零", "壱", "弐", "参", "壱ノ", "弐ノ", "参ノ",
    "一", "二", "三", "四", "五", "六",
]

# 单字标记（通常表示子标题/角色名）
SINGLE_CHAR_MARKERS = COLOR_WORDS + JAPANESE_NUMERALS

# ============================================================================
# 综合模式：组合检查
# ============================================================================

def looks_like_episode_variant(suffix: str) -> bool:
    """Check if a string looks like an episode variant rather than series name part.

    Heuristics (any match → likely variant):
    - Starts with a single-kanji color/numeral
    - Contains character name patterns (kanji + hiragana, like 千夏, 咲夜)
    - Contains episode indicators (前編/後編, 上巻/下巻)
    - Is short (<= 8 chars) and follows a longer base name
    - Contains OVA/OVA marker
    - Ends with 編/篇 (chapter indicator)
    """
    if not suffix:
        return False

    suffix = suffix.strip()

    # Single character: color, numeral, etc.
    if suffix in SINGLE_CHAR_MARKERS:
        return True

    # Known episode markers after ・
    episode_indicators = [
        r"OVA", r"OAD", r"ONA",
        r"前編", r"後編", r"前篇", r"後篇",
        r"上巻", r"下巻", r"中編", r"中篇",
        r"第[一二三四五六七八九十\d]+[話巻集]",
        r"Experiment\.?\s*\d",
        r"ope_\d+",
        r"SCENE\.?\d*",
        r"Vol\.?\s*\d",
        r"＃\d+",
    ]
    import re
    for pat in episode_indicators:
        if re.search(pat, suffix):
            return True

    # Ends with 編/篇 (chapter/story marker)
    if re.search(r"[編篇]$", suffix):
        return True

    # Short suffix (<= 6 chars) likely a character marker
    if len(suffix) <= 6:
        return True

    return False


def looks_like_bracket_variant(bracket_content: str) -> bool:
    """Check if 【content】 looks like an episode variant.

    Almost all 【】 suffixes in hanime filenames are episode variants.
    Returns True for known patterns.
    """
    if not bracket_content:
        return False

    import re

    # Episode numbers: 第01話, 第02話
    if re.match(r"第\d+[話話集]", bracket_content):
        return True

    # Character names with circle numbers: 千夏①, 春香&千夏②
    if re.search(r"[①②③④⑤⑥⑦⑧⑨⑩]", bracket_content):
        return True

    # Special markers: 最終巻, 含特典
    if bracket_content in ("最終巻", "含特典", "完全版"):
        return True

    # Short content (character name, etc.)
    if len(bracket_content) <= 10:
        return True

    # Numbers
    if re.match(r"\d+$", bracket_content):
        return True

    return False
