import re
import unicodedata


class NormalizeService:
    """Normalizes math notation from various input formats."""

    UNICODE_REPLACEMENTS = {
        "\u00d7": "*",    # ×
        "\u00f7": "/",    # ÷
        "\u2212": "-",    # −
        "\u2013": "-",    # en dash
        "\u2014": "-",    # em dash
        "\u00b2": "**2",  # ²
        "\u00b3": "**3",  # ³
        "\u2074": "**4",  # ⁴
        "\u2075": "**5",  # ⁵
        "\u2076": "**6",  # ⁶
        "\u2077": "**7",  # ⁷
        "\u2078": "**8",  # ⁸
        "\u2079": "**9",  # ⁹
        "\u221a": "sqrt",
        "\u03c0": "pi",
        "\u03b1": "alpha",
        "\u03b2": "beta",
        "\u03b3": "gamma",
        "\u03b4": "delta",
        "\u03b5": "epsilon",
        "\u03b8": "theta",
        "\u03bb": "lambda",
        "\u03bc": "mu",
        "\u03c3": "sigma",
        "\u03c4": "tau",
        "\u03c6": "phi",
        "\u03c9": "omega",
        "\u2264": "<=",
        "\u2265": ">=",
        "\u2260": "!=",
        "\u221e": "oo",
        "\u222b": "integrate",
        "\u2211": "sum",
        "\u220f": "product",
        "\u2202": "d",
        "\u00b9": "**1",
        "\u2070": "**0",
    }

    OCR_FIXES = {
        "×": "*",
        "÷": "/",
        "—": "-",
        "–": "-",
        "'": "'",
        "\u201c": '"',
        "\u201d": '"',
        "O": "0",  # Only when clearly numeric context
        "l": "1",  # Only when clearly numeric context
    }

    def normalize(self, text: str) -> str:
        """Full normalization pipeline."""
        if not text:
            return ""
        result = text.strip()
        result = self._replace_unicode(result)
        result = self._fix_spacing(result)
        result = self._normalize_operators(result)
        result = self._normalize_functions(result)
        result = self._fix_implicit_multiplication(result)
        result = self._balance_parentheses(result)
        return result.strip()

    def normalize_ocr(self, text: str) -> str:
        """Normalization specifically for OCR output."""
        if not text:
            return ""
        result = text.strip()
        result = self._replace_unicode(result)
        result = self._fix_ocr_artifacts(result)
        result = self._fix_spacing(result)
        result = self._normalize_operators(result)
        result = self._normalize_functions(result)
        result = self._fix_implicit_multiplication(result)
        result = self._balance_parentheses(result)
        return result.strip()

    def _replace_unicode(self, text: str) -> str:
        for old, new in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(old, new)
        return text

    def _fix_ocr_artifacts(self, text: str) -> str:
        """Fix common OCR misreadings."""
        # Fix 'x' misread as '×' (already handled by unicode)
        # Fix common letter/number confusions in numeric contexts
        # Replace 'O' with '0' when surrounded by digits
        text = re.sub(r"(\d)O(\d)", r"\g<1>0\g<2>", text)
        text = re.sub(r"(\d)O\b", r"\g<1>0", text)
        text = re.sub(r"\bO(\d)", r"0\g<1>", text)
        # Replace 'l' with '1' when surrounded by digits
        text = re.sub(r"(\d)l(\d)", r"\g<1>1\g<2>", text)
        text = re.sub(r"(\d)l\b", r"\g<1>1", text)
        # Fix 'S' misread as '5' in numeric context
        text = re.sub(r"(\d)S(\d)", r"\g<1>5\g<2>", text)
        # Remove stray characters that OCR often adds
        text = re.sub(r"[|\\]{2,}", "", text)
        return text

    def _fix_spacing(self, text: str) -> str:
        """Clean up spacing."""
        text = re.sub(r"\s+", " ", text)
        # Remove spaces around operators within expressions
        text = re.sub(r"\s*\*\*\s*", "**", text)
        return text

    def _normalize_operators(self, text: str) -> str:
        """Standardize operator notation."""
        # Caret to power
        text = text.replace("^", "**")
        # Handle doubled operators
        text = re.sub(r"\*\*\*+", "**", text)
        return text

    def _normalize_functions(self, text: str) -> str:
        """Normalize function names."""
        replacements = {
            r"\barcsin\b": "asin",
            r"\barccos\b": "acos",
            r"\barctan\b": "atan",
            r"\blog\b(?!\s*\()": "log",
            r"\bln\b": "log",
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _fix_implicit_multiplication(self, text: str) -> str:
        """Add explicit multiplication where implied."""
        # 2x -> 2*x, 3( -> 3*(
        text = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", text)
        # )( -> )*(, )2 -> )*2
        text = re.sub(r"\)(\w)", r")*\1", text)
        text = re.sub(r"\)\(", ")*(", text)
        # But fix function calls: undo multiplication before known functions
        funcs = [
            "sin", "cos", "tan", "cot", "sec", "csc",
            "asin", "acos", "atan",
            "sinh", "cosh", "tanh",
            "log", "ln", "exp", "sqrt", "abs",
            "integrate", "diff", "limit", "sum", "product",
            "solve", "factor", "expand", "simplify",
            "factorial", "gamma", "beta",
            "Matrix", "det", "trace",
            "pi", "oo",
        ]
        for func in funcs:
            # Fix: number*function -> number*function (keep) but fix parse issues
            text = re.sub(rf"\*({func})\b", rf"*{func}", text)
            # Remove accidental * inserted between function name parts
            # e.g., "s*i*n" should not happen, but "2*sin" is fine
        return text

    def _balance_parentheses(self, text: str) -> str:
        """Attempt to balance unmatched parentheses."""
        open_count = text.count("(") - text.count(")")
        if open_count > 0:
            text += ")" * open_count
        elif open_count < 0:
            text = "(" * (-open_count) + text
        return text
