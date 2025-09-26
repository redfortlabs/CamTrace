from camtrace.ip_enricher import resolve_ip


def test_google_asn():
    r = resolve_ip("8.8.8.8")
    assert r.asn in (15169,)  # Google ASN
    assert r.as_org and "GOOGLE" in r.as_org.upper()
