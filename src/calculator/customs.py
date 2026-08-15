import datetime
from pydantic import BaseModel


class CostBreakdown(BaseModel):
    auction_price: float
    auction_fee: float
    us_ground_shipping: float
    ocean_freight_poti: float
    poti_to_yerevan_shipping: float
    total_logistics: float
    customs_duty: float
    environmental_tax: float
    customs_clearance_total: float
    broker_fee: float
    total_cost: float


class CustomsCalculator:
    """
    Calculates Republic of Armenia Customs Clearance Duty & Taxes
    and Shipping/Logistics Costs.
    """

    @staticmethod
    def calculate_customs_duty(
        year: int,
        engine_cc: int,
        fuel_type: str,
        car_value_usd: float
    ) -> tuple[float, float]:
        """
        Calculates customs duty and environmental fee in USD.
        Rule breakdown (Armenia EAEU customs rules):
        - Electric vehicles (EV): 0% duty (duty free up to quota) + minimal customs fee.
        - Under 3 years old: ~15% - 20% of value or fixed per cc rate.
        - 3 to 5 years old: Rate based on cc (approx 1.5 - 2.5 USD per cc).
        - 5+ years old: Rate based on cc (approx 2.5 - 3.5 USD per cc).
        - Environmental fee: 2% to 10% depending on age.
        """
        current_year = datetime.datetime.now().year
        age = current_year - year

        fuel = fuel_type.lower()
        if fuel in ["electric", "ev"]:
            customs_duty = max(200.0, car_value_usd * 0.05)
            env_tax = 0.0
            return round(customs_duty, 2), round(env_tax, 2)

        if age <= 3:
            base_duty = max(car_value_usd * 0.15, engine_cc * 1.5)
            env_rate = 0.02
        elif 3 < age <= 5:
            if engine_cc <= 1500:
                base_duty = engine_cc * 1.7
            elif engine_cc <= 2500:
                base_duty = engine_cc * 2.2
            else:
                base_duty = engine_cc * 3.0
            env_rate = 0.03
        else:  # older than 5 years
            if engine_cc <= 1500:
                base_duty = engine_cc * 2.5
            elif engine_cc <= 2500:
                base_duty = engine_cc * 3.2
            else:
                base_duty = engine_cc * 4.0
            env_rate = 0.05

        if fuel in ["hybrid", "plug-in hybrid"]:
            base_duty *= 0.85  # 15% discount/incentive for hybrid vehicles

        customs_duty = max(base_duty, car_value_usd * 0.15)
        env_tax = car_value_usd * env_rate

        return round(customs_duty, 2), round(env_tax, 2)

    @classmethod
    def calculate_full_cost(
        cls,
        auction_price: float,
        year: int,
        engine_cc: int,
        fuel_type: str = "gasoline",
        base_logistics_usd: float = 1800.0,
        broker_fee_usd: float = 300.0
    ) -> CostBreakdown:
        # Copart / Auction buyer fee estimation (~12%-15% with minimums)
        auction_fee = max(350.0, auction_price * 0.12)

        us_ground = 500.0
        ocean_poti = 1000.0
        poti_yerevan = 300.0
        total_logistics = us_ground + ocean_poti + poti_yerevan if base_logistics_usd <= 0 else base_logistics_usd

        customs_duty, env_tax = cls.calculate_customs_duty(year, engine_cc, fuel_type, auction_price)
        customs_total = customs_duty + env_tax

        total_cost = auction_price + auction_fee + total_logistics + customs_total + broker_fee_usd

        return CostBreakdown(
            auction_price=round(auction_price, 2),
            auction_fee=round(auction_fee, 2),
            us_ground_shipping=round(us_ground, 2),
            ocean_freight_poti=round(ocean_poti, 2),
            poti_to_yerevan_shipping=round(poti_yerevan, 2),
            total_logistics=round(total_logistics, 2),
            customs_duty=round(customs_duty, 2),
            environmental_tax=round(env_tax, 2),
            customs_clearance_total=round(customs_total, 2),
            broker_fee=round(broker_fee_usd, 2),
            total_cost=round(total_cost, 2)
        )
