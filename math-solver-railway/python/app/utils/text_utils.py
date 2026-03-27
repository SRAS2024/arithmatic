import re
import unicodedata


def clean_text(text: str) -> str:
    """Remove excess whitespace and normalize a text string."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def remove_non_math_chars(text: str) -> str:
    """Remove characters that are not part of math expressions."""
    allowed = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/^=()[]{}.,;:!<>| \t\n\\")
    return "".join(c for c in text if c in allowed or unicodedata.category(c).startswith("S"))


def normalize_unicode_math(text: str) -> str:
    """Replace Unicode math symbols with ASCII equivalents."""
    replacements = {
        "\u00d7": "*",   # ×
        "\u00f7": "/",   # ÷
        "\u2212": "-",   # −
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u00b2": "**2", # ²
        "\u00b3": "**3", # ³
        "\u221a": "sqrt",# √
        "\u03c0": "pi",  # π
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
        "\u2264": "<=",  # ≤
        "\u2265": ">=",  # ≥
        "\u2260": "!=",  # ≠
        "\u221e": "oo",  # ∞
        "\u222b": "integrate",  # ∫
        "\u2211": "sum",        # Σ
        "\u220f": "product",    # Π
        "\u2202": "d",          # ∂
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def extract_numbers(text: str) -> list[float]:
    """Extract all numbers from a string."""
    pattern = r"-?\d+\.?\d*(?:[eE][+-]?\d+)?"
    matches = re.findall(pattern, text)
    result = []
    for m in matches:
        try:
            result.append(float(m))
        except ValueError:
            pass
    return result


def is_equation(text: str) -> bool:
    """Check if text contains an equation (has = sign not in <=, >=, !=)."""
    cleaned = text.replace("<=", "").replace(">=", "").replace("!=", "").replace("==", "=")
    return "=" in cleaned


def split_equation(text: str) -> tuple[str, str]:
    """Split an equation at the = sign. Returns (lhs, rhs)."""
    cleaned = text.replace("==", "=")
    parts = cleaned.split("=", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return text.strip(), "0"


def detect_variables(text: str) -> list[str]:
    """Detect variable names in a math expression."""
    known_funcs = {
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan", "log", "ln", "exp",
        "sqrt", "abs", "pi", "inf", "oo",
        "integrate", "diff", "limit", "sum", "product",
        "factorial", "gamma", "beta", "zeta",
        "det", "trace", "transpose", "inverse",
        "mean", "median", "std", "var",
    }
    pattern = r"\b([a-zA-Z_]\w*)\b"
    matches = re.findall(pattern, text)
    variables = []
    seen = set()
    for m in matches:
        if m.lower() not in known_funcs and m not in seen and len(m) <= 3:
            variables.append(m)
            seen.add(m)
    return variables


def contains_math(text: str) -> bool:
    """Check if text likely contains mathematical content."""
    math_indicators = [
        r"\d+\s*[+\-*/^]\s*\d+",
        r"[=<>]",
        r"\b(sin|cos|tan|log|ln|sqrt|integral|derivative|limit)\b",
        r"\b(solve|factor|simplify|expand|differentiate|integrate)\b",
        r"[xy]\s*[+\-*/^=]",
        r"\d+\s*x",
        r"x\s*\^\s*\d+",
    ]
    for pattern in math_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
