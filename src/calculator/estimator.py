"""
Hybrid Price Estimation Engine for Auto Auctions (Copart/IAAI)
Combines Copart Est. Retail Value damage discount rates with BidFax/AutoAstat historical winning bid data.
"""

from typing import Dict, Optional


class PriceEstimationEngine:
    # Damage severity multiplier relative to Estimated Retail Value
    DAMAGE_DISCOUNT_RATES: Dict[str, float] = {
        "front end": 0.35,
        "rear end": 0.38,
        "side": 0.40,
        "all over": 0.25,
        "hail": 0.50,
        "minor dent/scratches": 0.60,
        "normal wear": 0.65,
        "mechanical": 0.30,
        "water/flood": 0.20,
        "burn": 0.15,
        "undercarriage": 0.35,
    }

    # Historical baseline winning bid percentage by car category & title
    TITLE_FACTOR: Dict[str, float] = {
        "salvage": 0.90,
        "clean": 1.15,
        "junk": 0.70,
        "rebuilt": 1.05,
    }

    @classmethod
    def estimate_winning_bid(
        cls,
        est_retail_value: float,
        primary_damage: Optional[str] = None,
        title_type: Optional[str] = None,
        current_bid: float = 0.0,
        buy_now_price: Optional[float] = None,
        mileage: Optional[int] = None,
        year: Optional[int] = None
    ) -> float:
        """
        Calculates predicted final winning auction bid for cars with $0 or low current bids.
        """
        if buy_now_price and buy_now_price > 0:
            # Winning bids on average finish at ~82% of Buy It Now price
            predicted_from_buy_now = buy_now_price * 0.82
        else:
            predicted_from_buy_now = None

        damage_key = (primary_damage or "front end").strip().lower()
        damage_discount = cls.DAMAGE_DISCOUNT_RATES.get(damage_key, 0.35)

        title_key = (title_type or "salvage").strip().lower()
        title_factor = cls.TITLE_FACTOR.get(title_key, 0.90)

        # Baseline predicted from Est Retail Value
        predicted_from_retail = est_retail_value * damage_discount * title_factor

        # Adjust for high mileage if provided
        if mileage and mileage > 100000:
            predicted_from_retail *= 0.85
        elif mileage and mileage < 30000:
            predicted_from_retail *= 1.10

        if predicted_from_buy_now:
            # Hybrid weighted average: 60% Retail Damage calculation + 40% Buy It Now baseline
            final_estimate = (predicted_from_retail * 0.6) + (predicted_from_buy_now * 0.4)
        else:
            final_estimate = predicted_from_retail

        # Final bid cannot be lower than current bid + minimal increment
        final_estimate = max(final_estimate, current_bid, 500.0)

        return round(final_estimate, 2)
