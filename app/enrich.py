import socket
from typing import Optional
from geoip2.database import Reader
from .config import MAXMIND_ASN_DB, MAXMIND_CITY_DB

asn_reader: Optional[Reader] = None
city_reader: Optional[Reader] = None

def init_geoip():
    global asn_reader, city_reader
    try:
        asn_reader = Reader(MAXMIND_ASN_DB)
    except Exception:
        asn_reader = None
    try:
        city_reader = Reader(MAXMIND_CITY_DB)
    except Exception:
        city_reader = None

def close_geoip():
    global asn_reader, city_reader
    if asn_reader:
        asn_reader.close()
    if city_reader:
        city_reader.close()

def rdns_lookup(ip: str) -> Optional[str]:
    try:
        host, *_ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return None

def geo_enrich(ip: str):
    # Returns dict: rdns, asn, as_org, country, region, city, lat, lon
    result = {
        "rdns": rdns_lookup(ip),
        "asn": None,
        "as_org": None,
        "country": None,
        "region": None,
        "city": None,
        "latitude": None,
        "longitude": None,
    }
    try:
        if asn_reader:
            asn = asn_reader.asn(ip)
            result["asn"] = asn.autonomous_system_number
            result["as_org"] = asn.autonomous_system_organization
    except Exception:
        pass
    try:
        if city_reader:
            city = city_reader.city(ip)
            result["country"] = city.country.iso_code
            result["region"] = city.subdivisions.most_specific.name if city.subdivisions else None
            result["city"] = city.city.name
            result["latitude"] = city.location.latitude
            result["longitude"] = city.location.longitude
    except Exception:
        pass
    return result
