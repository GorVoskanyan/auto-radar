import pytest
from src.calculator.customs import CustomsCalculator


def test_customs_duty_electric():
    duty, env_tax = CustomsCalculator.calculate_customs_duty(2022, 0, "electric", 10000)
    assert duty == 500.0
    assert env_tax == 0.0


def test_customs_duty_gasoline_under_3_years():
    duty, env_tax = CustomsCalculator.calculate_customs_duty(2023, 2000, "gasoline", 10000)
    assert duty >= 3000.0  # max(15% of 10k, 2000 * 1.5)
    assert env_tax == 200.0  # 2% of 10k


def test_customs_duty_hybrid_discount():
    duty_gas, _ = CustomsCalculator.calculate_customs_duty(2020, 2000, "gasoline", 8000)
    duty_hyb, _ = CustomsCalculator.calculate_customs_duty(2020, 2000, "hybrid", 8000)
    assert duty_hyb < duty_gas


def test_full_cost_calculation():
    cost = CustomsCalculator.calculate_full_cost(
        auction_price=5000.0,
        year=2020,
        engine_cc=2000,
        fuel_type="gasoline",
        base_logistics_usd=1800.0,
        broker_fee_usd=300.0
    )
    assert cost.auction_price == 5000.0
    assert cost.auction_fee == 600.0  # 12% of 5000
    assert cost.total_logistics == 1800.0
    assert cost.broker_fee == 300.0
    assert cost.total_cost == 5000.0 + 600.0 + 1800.0 + cost.customs_clearance_total + 300.0
