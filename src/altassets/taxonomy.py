"""Asset class taxonomy used to tag every series in the store."""

from enum import Enum


class AssetClass(str, Enum):
    # Equity
    REAL_ESTATE_EQUITY = "real_estate_equity"
    INFRASTRUCTURE_EQUITY = "infrastructure_equity"
    PUBLIC_EQUITY = "public_equity"
    PRIVATE_EQUITY = "private_equity"
    # Debt
    INFRASTRUCTURE_DEBT = "infrastructure_debt"
    ILLIQUID_TERM_LOANS = "illiquid_term_loans"
    PRIVATE_LIQUID_LOANS = "private_liquid_loans"
    COMMERCIAL_MORTGAGES = "commercial_mortgages"
    # Rates, FX, macro drivers shared by every class
    MACRO = "macro"


EQUITY = {
    AssetClass.REAL_ESTATE_EQUITY,
    AssetClass.INFRASTRUCTURE_EQUITY,
    AssetClass.PUBLIC_EQUITY,
    AssetClass.PRIVATE_EQUITY,
}
DEBT = {
    AssetClass.INFRASTRUCTURE_DEBT,
    AssetClass.ILLIQUID_TERM_LOANS,
    AssetClass.PRIVATE_LIQUID_LOANS,
    AssetClass.COMMERCIAL_MORTGAGES,
}
