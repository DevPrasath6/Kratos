import pytest
from agents.shelter_capacity_agent import ShelterCapacityAgent
from agents.infrastructure_risk_agent import InfrastructureRiskAgent
from agents.damage_verification_agent import DamageVerificationAgent
from agents.supply_logistics_agent import SupplyLogisticsAgent

@pytest.mark.asyncio
async def test_shelter_capacity_agent():
    agent = ShelterCapacityAgent()
    res = await agent.run({"evacuee_count": 25})
    assert res["status"] == "success"
    assert "recommended_shelter" in res
    assert len(res["all_shelters"]) > 0

@pytest.mark.asyncio
async def test_infrastructure_risk_agent():
    agent = InfrastructureRiskAgent()
    res = await agent.run({"disaster_type": "earthquake"})
    assert res["status"] == "success"
    assert "infrastructure_evaluations" in res
    assert res["disaster_type"] == "earthquake"

@pytest.mark.asyncio
async def test_damage_verification_agent():
    agent = DamageVerificationAgent()
    res = await agent.run({"location_label": "Bridge 7"})
    assert res["status"] == "success"
    assert res["location_evaluated"] == "Bridge 7"

@pytest.mark.asyncio
async def test_supply_logistics_agent():
    agent = SupplyLogisticsAgent()
    res = await agent.run({"isolated_population": 300})
    assert res["status"] == "success"
    assert res["logistics_manifest"]["water_liters"] == 900.0
    assert len(res["air_drop_zones"]) > 0
