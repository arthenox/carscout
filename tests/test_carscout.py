#!/usr/bin/env python3
"""Unit tests for CarScout OBD2 Diagnostic Tool.

Tests cover the main functions of carscout.py including:
- DTC database loading (load_dtc_db)
- DTC scanning (scan_dtcs)
- DTC clearing (clear_dtcs)
- Live data streaming (live_data)
- Demo mode functionality
- Localization (get_text)

All OBD2 connections are mocked to allow testing without real hardware.
"""

import os
import sys
import types

# Mock the 'obd' module BEFORE importing carscout
# This prevents the sys.exit(1) when obd is not installed
obd_mock = types.ModuleType("obd")


class MockCommands:
    """Mock obd.commands namespace."""

    GET_DTC = "GET_DTC"
    CLEAR_DTC = "CLEAR_DTC"
    RPM = "RPM"
    SPEED = "SPEED"
    COOLANT_TEMP = "COOLANT_TEMP"


obd_mock.commands = MockCommands()
obd_mock.OBD = lambda **kwargs: None
sys.modules["obd"] = obd_mock

# Add parent directory to path so we can import carscout
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carscout import (  # noqa: E402
    DemoConnection,
    MockResponse,
    get_text,
    load_dtc_db,
)


# ----------------------------------------------------------------------
# Tests for get_text()
# ----------------------------------------------------------------------
class TestGetText:
    """Tests for the get_text localization function."""

    def test_get_text_english_default(self):
        """Test that English is the default language."""
        result = get_text("app_name")
        assert result == "CarScout"

    def test_get_text_french(self):
        """Test French language lookup."""
        result = get_text("tagline", lang="fr")
        assert "diagnostic" in result.lower()

    def test_get_text_unknown_key_returns_key(self):
        """Test that unknown keys return the key itself."""
        result = get_text("nonexistent_key")
        assert result == "nonexistent_key"

    def test_get_text_unknown_lang_falls_back_to_english(self):
        """Test that unknown languages fall back to English."""
        result = get_text("app_name", lang="de")
        assert result == "CarScout"

    def test_get_text_all_keys_present_both_languages(self):
        """Test that both languages have the same keys."""
        from carscout import LANGUAGES
        en_keys = set(LANGUAGES["en"].keys())
        fr_keys = set(LANGUAGES["fr"].keys())
        assert en_keys == fr_keys, (
            f"Missing FR keys: {en_keys - fr_keys}, "
            f"Extra FR keys: {fr_keys - en_keys}"
        )

    def test_get_text_demo_mode_keys(self):
        """Test that demo mode keys exist in both languages."""
        for lang in ["en", "fr"]:
            assert get_text("demo_mode", lang) is not None
            assert get_text("demo_connected", lang) is not None


# ----------------------------------------------------------------------
# Tests for load_dtc_db()
# ----------------------------------------------------------------------
class TestLoadDtcDb:
    """Tests for the DTC database loading function."""

    def test_load_english_db(self):
        """Test loading the English DTC database."""
        db = load_dtc_db("en")
        assert isinstance(db, dict)
        assert len(db) > 2100
        assert "P0420" in db
        assert "Catalyst" in db["P0420"] or "catalyst" in db["P0420"]

    def test_load_french_db(self):
        """Test loading the French DTC database."""
        db = load_dtc_db("fr")
        assert isinstance(db, dict)
        assert len(db) > 2100
        assert "P0420" in db

    def test_load_default_db(self):
        """Test loading the default DTC database."""
        db = load_dtc_db("pt")
        assert isinstance(db, dict)
        assert len(db) > 2100

    def test_load_db_nonexistent_path(self):
        """Test loading a database when the file doesn't exist."""
        import carscout
        original_base = carscout.BASE_DIR
        try:
            carscout.BASE_DIR = "/nonexistent/path"
            db = load_dtc_db("en")
            assert db == {}
        finally:
            carscout.BASE_DIR = original_base

    def test_english_db_has_no_portuguese(self):
        """Test that the English DB contains no Portuguese words."""
        db = load_dtc_db("en")
        pt_words = [
            "banco", "cilindro", "desempenho", "combustivel",
            "circuito", "validvula", "posic3a7c3a3o", "Atuador",
            "Avaria", "Sincronismo", "Virabrequim"
        ]
        contaminated = []
        for code, desc in db.items():
            for word in pt_words:
                if word in desc:
                    contaminated.append((code, desc, word))
                    break
        assert len(contaminated) == 0, (
            f"Found {len(contaminated)} Portuguese entries"
            f" in English DB: {contaminated[:5]}"
        )

    def test_french_db_has_no_portuguese(self):
        """Test that the French DB contains no Portuguese words."""
        db = load_dtc_db("fr")
        pt_words = [
            "banco", "cilindro", "desempenho", "sinal",
            "muito", "posic3a7c3a3o", "Atuador", "Avaria",
            "circuito", "combustivel",
            "validvula", "comando", "Virabrequim",
            "Sincronismo"
        ]
        contaminated = []
        for code, desc in db.items():
            for word in pt_words:
                if word in desc:
                    contaminated.append((code, desc, word))
                    break
        assert len(contaminated) == 0, (
            f"Found {len(contaminated)} Portuguese entries"
            f" in French DB: {contaminated[:5]}"
        )

    def test_english_db_entry_count(self):
        """Test that the English DB has at least 2200 standard entries."""
        db = load_dtc_db("en")
        assert len(db) >= 2200, (
            f"English DB has only {len(db)} entries, expected >= 2200"
        )


# ----------------------------------------------------------------------
# Tests for DemoConnection
# ----------------------------------------------------------------------
class TestDemoConnection:
    """Tests for the DemoConnection mock OBD2 class."""

    def test_demo_connection_is_connected(self):
        """Test that DemoConnection always reports as connected."""
        conn = DemoConnection()
        assert conn.is_connected() is True

    def test_demo_connection_port_name(self):
        """Test that DemoConnection returns a mock port name."""
        conn = DemoConnection()
        assert conn.port_name() == "DEMO-MOCK"

    def test_demo_connection_scan_dtcs(self):
        """Test that DemoConnection returns mock DTC codes."""
        conn = DemoConnection()
        mock_cmd = type("Cmd", (), {
            "__str__": lambda s: "GET_DTC"
        })()
        response = conn.query(mock_cmd)
        assert not response.is_null()
        codes = response.value
        assert len(codes) == 3

    def test_demo_connection_clear_dtcs(self):
        """Test that DemoConnection can clear DTC codes."""
        conn = DemoConnection()
        response = conn.query(
            type("Cmd", (), {"__str__": lambda s: "GET_DTC"})()
        )
        assert len(response.value) > 0
        conn.query(
            type("Cmd", (), {"__str__": lambda s: "CLEAR_DTC"})()
        )
        response = conn.query(
            type("Cmd", (), {"__str__": lambda s: "GET_DTC"})()
        )
        assert response.is_null() or len(response.value) == 0

    def test_demo_connection_live_data_rpm(self):
        """Test that DemoConnection returns mock RPM data."""
        conn = DemoConnection()
        cmd = type("Cmd", (), {"__str__": lambda s: "RPM"})()
        response = conn.query(cmd)
        assert not response.is_null()
        assert response.value == "2500"

    def test_demo_connection_live_data_speed(self):
        """Test that DemoConnection returns mock speed data."""
        conn = DemoConnection()
        cmd = type("Cmd", (), {"__str__": lambda s: "SPEED"})()
        response = conn.query(cmd)
        assert not response.is_null()
        assert response.value == "80"

    def test_demo_connection_live_data_coolant(self):
        """Test that DemoConnection returns mock coolant temp."""
        conn = DemoConnection()
        cmd = type("Cmd", (), {
            "__str__": lambda s: "COOLANT_TEMP"
        })()
        response = conn.query(cmd)
        assert not response.is_null()
        assert response.value == "92"

    def test_demo_connection_default_dtc_codes(self):
        """Test that DemoConnection starts with 3 default DTCs."""
        conn = DemoConnection()
        assert len(conn.dtc_codes) == 3
        codes = [c for c, _ in conn.dtc_codes]
        assert "P0301" in codes
        assert "P0420" in codes
        assert "P0171" in codes


# ----------------------------------------------------------------------
# Tests for MockResponse
# ----------------------------------------------------------------------
class TestMockResponse:
    """Tests for the MockResponse class."""

    def test_mock_response_with_value(self):
        """Test MockResponse with a non-null value."""
        resp = MockResponse("2500", unit="rpm")
        assert resp.value == "2500"
        assert resp.is_null() is False

    def test_mock_response_with_none(self):
        """Test MockResponse with a None value."""
        resp = MockResponse(None)
        assert resp.is_null() is True

    def test_mock_response_with_empty_list(self):
        """Test MockResponse with an empty list."""
        resp = MockResponse([])
        assert resp.is_null() is True

    def test_mock_response_with_list(self):
        """Test MockResponse with a list of DTC codes."""
        resp = MockResponse([("P0301", ""), ("P0420", "")])
        assert resp.is_null() is False
        assert len(resp.value) == 2

    def test_mock_response_unit_property(self):
        """Test MockResponse unit property (C-09)."""
        resp = MockResponse("2500", unit="rpm")
        assert resp.unit == "rpm"
        resp_no_unit = MockResponse(None)
        assert resp_no_unit.unit == ""


# ----------------------------------------------------------------------
# Tests for DTC database content integrity
# ----------------------------------------------------------------------
class TestDtcDbContent:
    """Tests for DTC database content quality and integrity."""

    def test_default_db_matches_english_db(self):
        """Test that the default DB is identical to the English DB."""
        en_db = load_dtc_db("en")
        default_db = load_dtc_db("xx")
        assert en_db.keys() == default_db.keys(), (
            "Default DB keys don't match English DB keys"
        )

    def test_common_codes_present_in_english(self):
        """Test that common OBD-II codes are in the English DB."""
        db = load_dtc_db("en")
        common_codes = [
            "P0010", "P0011", "P0012",
            "P0100", "P0101", "P0102", "P0103",
            "P0171", "P0172", "P0174", "P0175",
            "P0300", "P0301", "P0302", "P0303", "P0304",
            "P0420", "P0430",
            "P0500", "P0505",
            "P0700",
        ]
        for code in common_codes:
            assert code in db, (
                f"Common code {code} missing from English DB"
            )

    def test_no_empty_descriptions_english(self):
        """Test that no English DB entries have empty descriptions."""
        db = load_dtc_db("en")
        empty = [(k, v) for k, v in db.items() if not v.strip()]
        assert len(empty) == 0, (
            f"Found {len(empty)} empty descriptions in English DB"
        )

    def test_no_empty_descriptions_french(self):
        """Test that no French DB entries have empty descriptions."""
        db = load_dtc_db("fr")
        empty = [(k, v) for k, v in db.items() if not v.strip()]
        assert len(empty) == 0, (
            f"Found {len(empty)} empty descriptions in French DB"
        )


# ----------------------------------------------------------------------
# Tests for scan_dtcs integration
# ----------------------------------------------------------------------
class TestScanDtcs:
    """Integration tests for the scan_dtcs function."""

    def test_scan_with_demo_connection(self):
        """Test scan_dtcs with DemoConnection."""
        from carscout import scan_dtcs
        conn = DemoConnection()
        db = load_dtc_db("en")
        try:
            scan_dtcs(conn, "en", db)
        except SystemExit:
            pass

    def test_scan_with_cleared_demo(self):
        """Test scan_dtcs after clearing demo DTCs."""
        from carscout import scan_dtcs
        conn = DemoConnection()
        db = load_dtc_db("en")
        conn.clear_demo_dtcs()
        try:
            scan_dtcs(conn, "en", db)
        except SystemExit:
            pass


# ----------------------------------------------------------------------
# Tests for clear_dtcs integration
# ----------------------------------------------------------------------
class TestClearDtcs:
    """Integration tests for the clear_dtcs function."""

    def test_clear_with_demo_connection(self):
        """Test clear_dtcs with DemoConnection using mock confirmation."""
        from unittest.mock import patch
        from carscout import clear_dtcs
        conn = DemoConnection()
        # Confirm clearing
        with patch('carscout.Confirm.ask', return_value=True):
            clear_dtcs(conn, "en")
        # Verify DTCs were actually cleared
        response = conn.query(
            type("Cmd", (), {"__str__": lambda s: "GET_DTC"})()
        )
        assert response.is_null() or len(response.value) == 0

    def test_clear_dtcs_cancelled(self):
        """Test clear_dtcs when user cancels."""
        from unittest.mock import patch
        from carscout import clear_dtcs
        conn = DemoConnection()
        # Cancel clearing - DTCs should remain
        with patch('carscout.Confirm.ask', return_value=False):
            clear_dtcs(conn, "en")
        assert len(conn.dtc_codes) > 0
