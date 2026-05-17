"""Google Translate service for converting descriptions to Chinese."""

import logging
import re

import httpx

logger = logging.getLogger(__name__)

# Free Google Translate API (no key required)
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

# Characters indicating text is already Chinese
_CHINESE_RE = re.compile(r"[一-鿿㐀-䶿]")


class TranslationService:
    """Free Google Translate wrapper for NFO content translation."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def is_chinese(self, text: str) -> bool:
        """Check if text is primarily Chinese (no translation needed)."""
        if not text:
            return True
        chinese_chars = len(_CHINESE_RE.findall(text))
        alpha_chars = len(re.findall(r"[a-zA-Z]", text))
        total = max(chinese_chars + alpha_chars, 1)
        return (chinese_chars / total) > 0.3

    async def to_chinese(self, text: str) -> str:
        """Translate text to Simplified Chinese if not already.

        Returns original text if already Chinese, empty, or on failure.
        """
        if not text or self.is_chinese(text):
            return text

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    TRANSLATE_URL,
                    params={
                        "client": "gtx",
                        "sl": "auto",
                        "tl": "zh-CN",
                        "dt": "t",
                        "q": text,
                    },
                    headers={"User-Agent": "MHTI/1.0"},
                )
                if resp.status_code != 200:
                    logger.warning(f"Translate returned {resp.status_code}")
                    return text
                data = resp.json()
                # Extract translated segments
                parts = []
                for segment in data[0]:
                    if segment and segment[0]:
                        parts.append(segment[0])
                result = "".join(parts)
                if result:
                    logger.info(f"Translated: {text[:60]}... -> {result[:60]}...")
                    return result
                return text
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return text
