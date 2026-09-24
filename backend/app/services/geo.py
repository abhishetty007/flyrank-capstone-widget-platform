import ipaddress

import requests


def is_private_ip(ip_address: str) -> bool:
    try:
        return ipaddress.ip_address(ip_address).is_private
    except ValueError:
        return False


def get_geo_from_ip_api(ip_address: str) -> dict | None:
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=3,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("status") != "success":
            return None

        return {
            "country": data.get("country"),
            "city": data.get("city"),
            "provider": "ip-api",
        }

    except requests.RequestException:
        return None


def get_geo_from_ipapi(ip_address: str) -> dict | None:
    try:
        response = requests.get(
            f"https://ipapi.co/{ip_address}/json/",
            timeout=3,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("error"):
            return None

        return {
            "country": data.get("country_name"),
            "city": data.get("city"),
            "provider": "ipapi.co",
        }

    except requests.RequestException:
        return None


def get_geo_location(ip_address: str) -> dict | None:
    """
    Try geo providers in order.

    Provider A: ip-api.com
    Provider B: ipapi.co

    If the IP is private/invalid, or both providers fail,
    return None so the submission can still be stored.
    """

    if not ip_address or is_private_ip(ip_address):
        return None

    # Provider A
    location = get_geo_from_ip_api(ip_address)

    if location:
        return location

    # Provider B fallback
    location = get_geo_from_ipapi(ip_address)

    if location:
        return location

    # Both providers failed.
    # Submission processing should continue without geo data.
    return None