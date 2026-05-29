"""
Tests for the compatibility service.
Run with: python -m pytest tests/test_compatibility.py -v
"""
import pytest
from app import create_app
from database.db import db
from models.component import Component
from services.compatibility_service import (
    check_cpu_motherboard,
    check_ram_compatibility,
    check_psu_wattage,
    check_full_build,
)


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_components(app):
    with app.app_context():
        cpu = Component(id=1, name="Ryzen 5 7600X", brand="AMD", category="CPU",
                        price=16000, specs="AM5, DDR5, 105W")
        cpu_b = Component(id=2, name="Core i5-13600K", brand="Intel", category="CPU",
                          price=17500, specs="LGA1700, DDR5, 125W")
        mb_ok = Component(id=3, name="X670E Tomahawk", brand="MSI", category="Motherboard",
                          price=18000, specs="AM5, DDR5, PCIe 5.0")
        mb_bad = Component(id=4, name="Z790 AORUS", brand="Gigabyte", category="Motherboard",
                           price=15000, specs="LGA1700, DDR5, PCIe 5.0")
        ram_ddr5 = Component(id=5, name="Vengeance 16GB DDR5", brand="Corsair",
                             category="RAM", price=5500, specs="DDR5-5600")
        ram_ddr4 = Component(id=6, name="Fury Beast 32GB DDR4", brand="Kingston",
                             category="RAM", price=6000, specs="DDR4-3600")
        psu_ok = Component(id=7, name="RM850x", brand="Corsair", category="PSU",
                           price=7500, specs="850W, 80+ Gold")
        psu_weak = Component(id=8, name="CX450", brand="Corsair", category="PSU",
                             price=3000, specs="450W, 80+ Bronze")
        for c in [cpu, cpu_b, mb_ok, mb_bad, ram_ddr5, ram_ddr4, psu_ok, psu_weak]:
            db.session.add(c)
        db.session.commit()
        return {"cpu": cpu, "cpu_b": cpu_b, "mb_ok": mb_ok, "mb_bad": mb_bad,
                "ram_ddr5": ram_ddr5, "ram_ddr4": ram_ddr4,
                "psu_ok": psu_ok, "psu_weak": psu_weak}


class TestCpuMotherboardCompatibility:
    def test_compatible_am5(self, app, sample_components):
        with app.app_context():
            result = check_cpu_motherboard(1, 3)   # Ryzen 7600X + X670E
            assert result["compatible"] is True
            assert result["issues"] == []

    def test_incompatible_socket(self, app, sample_components):
        with app.app_context():
            result = check_cpu_motherboard(1, 4)   # AM5 CPU + LGA1700 MB
            assert result["compatible"] is False
            assert any("socket" in i.lower() for i in result["issues"])

    def test_intel_on_intel_board(self, app, sample_components):
        with app.app_context():
            result = check_cpu_motherboard(2, 4)   # i5-13600K + Z790
            assert result["compatible"] is True


class TestRamCompatibility:
    def test_ddr5_ram_on_ddr5_board(self, app, sample_components):
        with app.app_context():
            result = check_ram_compatibility(5, 3)  # DDR5 RAM + DDR5 MB
            assert result["compatible"] is True

    def test_ddr4_ram_on_ddr5_board(self, app, sample_components):
        with app.app_context():
            result = check_ram_compatibility(6, 3)  # DDR4 RAM + DDR5 MB
            assert result["compatible"] is False
            assert any("ddr" in i.lower() for i in result["issues"])


class TestPsuWattage:
    def test_sufficient_psu(self, app, sample_components):
        with app.app_context():
            result = check_psu_wattage([1, 3, 5], 7)   # 850W PSU
            assert result["compatible"] is True

    def test_insufficient_psu(self, app, sample_components):
        with app.app_context():
            result = check_psu_wattage([1, 3, 5], 8)   # 450W PSU
            assert result["compatible"] is False
            assert any("watt" in i.lower() or "power" in i.lower() for i in result["issues"])


class TestFullBuildCheck:
    def test_full_compatible_build(self, app, sample_components):
        with app.app_context():
            ids = [1, 3, 5, 7]   # AM5 CPU + AM5 MB + DDR5 RAM + 850W PSU
            result = check_full_build(ids)
            assert result["compatible"] is True
            assert result["issues"] == []

    def test_mixed_incompatible(self, app, sample_components):
        with app.app_context():
            ids = [1, 4, 5, 7]   # AM5 CPU + LGA1700 MB
            result = check_full_build(ids)
            assert result["compatible"] is False
            assert len(result["issues"]) >= 1
