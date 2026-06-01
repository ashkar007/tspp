"""
TSIL Constants — Weight schemes, expiry codes, and DSL-wide enumerations.
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Weight Schemes
# ---------------------------------------------------------------------------

class WeightScheme(str, Enum):
    """Weighting schemes for basket instruments."""
    EQ   = "WGT_EQ"    # Equal-weighted
    VOL  = "WGT_VOL"   # Inverse-volatility weighted
    MOM  = "WGT_MOM"   # Momentum-weighted
    MCAP = "WGT_MCAP"  # Market-capitalisation weighted


# Convenience aliases so users can write  t(["SPX","SX5E"], WGT_EQ)
WGT_EQ   = WeightScheme.EQ
WGT_VOL  = WeightScheme.VOL
WGT_MOM  = WeightScheme.MOM
WGT_MCAP = WeightScheme.MCAP


# ---------------------------------------------------------------------------
# Expiry Month Codes (CME / listed-style)
# ---------------------------------------------------------------------------

EXPIRY_MONTH_CODES: dict[str, int] = {
    "F": 1,   # January
    "G": 2,   # February
    "H": 3,   # March
    "J": 4,   # April
    "K": 5,   # May
    "M": 6,   # June
    "N": 7,   # July
    "Q": 8,   # August
    "U": 9,   # September
    "V": 10,  # October
    "X": 11,  # November
    "Z": 12,  # December
}

MONTH_NAME_TO_NUM: dict[str, int] = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


# ---------------------------------------------------------------------------
# Strike Types
# ---------------------------------------------------------------------------

class StrikeType(str, Enum):
    ABSOLUTE          = "ABSOLUTE"
    FORWARD_MONEYNESS = "FORWARD_MONEYNESS"
    SPOT_MONEYNESS    = "SPOT_MONEYNESS"
    DELTA             = "DELTA"
    DELTA_PUT         = "DELTA_PUT"
    DELTA_CALL        = "DELTA_CALL"
    NORMALIZED        = "NORMALIZED"


# ---------------------------------------------------------------------------
# Expiry Types
# ---------------------------------------------------------------------------

class ExpiryType(str, Enum):
    FIXED   = "FIXED"
    TENOR   = "TENOR"
    FORWARD = "FORWARD"
