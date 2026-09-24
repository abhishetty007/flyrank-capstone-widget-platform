from unittest.mock import patch

from backend.app.services.geo import get_geo_location


def test_provider_a_success():
    provider_a_result = {
        "country": "India",
        "city": "Bengaluru",
        "provider": "ip-api",
    }

    with patch(
        "backend.app.services.geo.get_geo_from_ip_api",
        return_value=provider_a_result,
    ) as provider_a, patch(
        "backend.app.services.geo.get_geo_from_ipapi"
    ) as provider_b:

        result = get_geo_location("8.8.8.8")

        assert result == provider_a_result
        provider_a.assert_called_once_with("8.8.8.8")
        provider_b.assert_not_called()


def test_provider_a_failure_uses_provider_b():
    provider_b_result = {
        "country": "India",
        "city": "Bengaluru",
        "provider": "ipapi.co",
    }

    with patch(
        "backend.app.services.geo.get_geo_from_ip_api",
        return_value=None,
    ) as provider_a, patch(
        "backend.app.services.geo.get_geo_from_ipapi",
        return_value=provider_b_result,
    ) as provider_b:

        result = get_geo_location("8.8.8.8")

        assert result == provider_b_result
        provider_a.assert_called_once_with("8.8.8.8")
        provider_b.assert_called_once_with("8.8.8.8")


def test_both_providers_failure_returns_none():
    with patch(
        "backend.app.services.geo.get_geo_from_ip_api",
        return_value=None,
    ), patch(
        "backend.app.services.geo.get_geo_from_ipapi",
        return_value=None,
    ):

        result = get_geo_location("8.8.8.8")

        assert result is None


def test_private_ip_returns_none():
    with patch(
        "backend.app.services.geo.get_geo_from_ip_api"
    ) as provider_a, patch(
        "backend.app.services.geo.get_geo_from_ipapi"
    ) as provider_b:

        result = get_geo_location("127.0.0.1")

        assert result is None
        provider_a.assert_not_called()
        provider_b.assert_not_called()