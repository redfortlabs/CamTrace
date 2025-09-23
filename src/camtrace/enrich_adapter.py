# src/camtrace/enrich_adapter.py
from __future__ import annotations

from typing import Dict, Any
import ipaddress

from camtrace.ip_enricher import resolve_ip


def _is_public(ip: str | None) -> bool:
    try:
        return ip is not None and ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def _apply(prefix: str, ip: str | None, rec: Dict[str, Any]) -> None:
    # Skip enrichment for private/reserved/invalid IPs,
    # but ensure columns exist (set to None) for CSV.
    if not _is_public(ip):
        for key in (
            "ptr", "asn", "as_org",
            "country_iso", "country_name", "region", "city",
            "latitude", "longitude",
        ):
            rec.setdefault(f"{prefix}{key}", None)
        return

    e = resolve_ip(ip)
    rec[f"{prefix}ptr"] = e.ptr
    rec[f"{prefix}asn"] = e.asn
    rec[f"{prefix}as_org"] = e.as_org
    rec[f"{prefix}country_iso"] = e.country_iso
    rec[f"{prefix}country_name"] = e.country_name
    rec[f"{prefix}region"] = e.region
    rec[f"{prefix}city"] = e.city
    rec[f"{prefix}latitude"] = e.latitude
    rec[f"{prefix}longitude"] = e.longitude


def enrich_flow_record(flow: Dict[str, Any], src_key: str = "src_ip", dst_key: str = "dst_ip") -> Dict[str, Any]:
    _apply("src_", flow.get(src_key), flow)
    _apply("dst_", flow.get(dst_key), flow)
    return flow
