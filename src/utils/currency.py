"""
currency.py - Handles Rupiah formatting and parsing.
Budget formatting handles Indonesian dot formats.
"""
import re

def parse_rupiah(value: str) -> int:
    """
    Parses a string like '10.000.000', 'Rp 10.000.000', or '10000000' into integer 10000000.
    Returns 0 if invalid.
    """
    if not value:
        return 0
    # Remove everything except digits
    clean = re.sub(r'[^\d]', '', str(value))
    if not clean:
        return 0
    try:
        return int(clean)
    except ValueError:
        return 0

def format_rupiah(value: int) -> str:
    """
    Formats integer 10000000 into 'Rp10.000.000'
    """
    if value is None:
        return "Rp0"
    # Format with dot as thousand separator
    formatted = "{:,}".format(value).replace(',', '.')
    return f"Rp{formatted}"

def calculate_budget_range(budget: int, tolerance_pct: float) -> tuple[int, int]:
    """
    Calculates min and max budget based on tolerance percentage.
    """
    if not budget or budget <= 0:
        return 0, 0
    
    # Tolerance is a percentage (e.g., 20 means 20%)
    frac = max(0, min(tolerance_pct, 100)) / 100.0
    
    min_budget = int(budget * (1.0 - frac))
    max_budget = int(budget * (1.0 + frac))
    
    return min_budget, max_budget
