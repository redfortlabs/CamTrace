# src/camtrace/ip_enricher.py
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

import dns.resolver
import dns.reversename

# Load .env once on import
load_dotenv()

# ---- Config from environment ----
ASN_DB_PATH = os.getenv("MAXMIND_ASN_DB", "./data/maxmind/GeoLite2-ASN.mmdb")
CITY_DB_PATH = os.getenv("MAXMIND_CITY_DB", "./data/maxmind/GeoLite2-City.mmdb")
DNS_RESOLVER = os.getenv("DNS_RESOLVER", "").strip()  # e.g., "1.1.1.1" or blank for system default

# ---- Pydantic return model ----
class EnrichedIP(BaseModel):
    ip: str
    ptr: Optional[str] = None

    asn: Optional[int] = None
    as_org: Optional[str] = None

    country_iso: Optional[str] = None
    country_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


def _build_resolver() -> dns.resolver.Resolver:
    r = dns.resolver.Resolver()
    # If user specifies a resolver, use it; else rely on system config
    if DNS_RESOLVER:
        r.nameservers = [DNS_RESOLVER]
    # Reasonable timeouts for single lookups
    r.timeout = 2.0
    r.lifetime = 3.0
    return r


class IPEnricher:
    """
    Reusable, process-wide readers + DNS resolver.
    Keeping one instance around and call .resolve(ip).
    """

    def __init__(self, asn_db_path: str = ASN_DB_PATH, city_db_path: str = CITY_DB_PATH):
        # Validate files exist early with friendly errors
        for label, path in (("ASN DB", asn_db_path), ("City DB", city_db_path)):
            if path and not os.path.isfile(path):
                raise FileNotFoundError(
                    f"{label} not found at '{path}'. "
                    f"Set MAXMIND_ASN_DB / MAXMIND_CITY_DB or place files correctly."
                )

        # Open readers (these are safe to reuse across lookups)
        self._asn_reader = Reader(asn_db_path) if asn_db_path else None
        self._city_reader = Reader(city_db_path) if city_db_path else None

        self._resolver = _build_resolver()

    def close(self) -> None:
        if self._asn_reader:
            self._asn_reader.close()
        if self._city_reader:
            self._city_reader.close()

    # ---- Internal helpers ----
    def _ptr_lookup(self, ip: str) -> Optional[str]:
        try:
            rev = dns.reversename.from_address(ip)
            ans = self._resolver.resolve(rev, "PTR")
            # Return the first PTR name as a string without trailing dot
            return str(ans[0]).rstrip(".") if ans and len(ans) else None
        except Exception:
            return None

    def _asn_lookup(self, ip: str) -> tuple[Optional[int], Optional[str]]:
        if not self._asn_reader:
            return None, None
        try:
            rec = self._asn_reader.asn(ip)
            return rec.autonomous_system_number, rec.autonomous_system_organization
        except AddressNotFoundError:
            return None, None
        except Exception:
            return None, None

    def _city_lookup(self, ip: str):
        if not self._city_reader:
            return None, None, None, None, None, None
        try:
            rec = self._city_reader.city(ip)
            country_iso = rec.country.iso_code
            country_name = rec.country.name
            region = rec.subdivisions.most_specific.name or None
            city = rec.city.name
            lat = rec.location.latitude
            lon = rec.location.longitude
            return country_iso, country_name, region, city, lat, lon
        except AddressNotFoundError:
            return None, None, None, None, None, None
        except Exception:
            return None, None, None, None, None, None

    # ---- Public API (one-shot resolver) ----
    def resolve(self, ip: str) -> EnrichedIP:
        asn_num, as_org = self._asn_lookup(ip)
        country_iso, country_name, region, city, lat, lon = self._city_lookup(ip)
        ptr = self._ptr_lookup(ip)

        return EnrichedIP(
            ip=ip,
            ptr=ptr,
            asn=asn_num,
            as_org=as_org,
            country_iso=country_iso,
            country_name=country_name,
            region=region,
            city=city,
            latitude=lat,
            longitude=lon,
        )


# ---- Convenient module-level cached function ----
# This gives easy caching without managing an instance elsewhere.
# Keep one global enrich er + LRU over IPs.
_enricher_singleton = IPEnricher()


@lru_cache(maxsize=8192)
def resolve_ip(ip: str) -> EnrichedIP:
    """
    Cached convenience wrapper: EnrichedIP for a single IP.
    """
    return _enricher_singleton.resolve(ip)
