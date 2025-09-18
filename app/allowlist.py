import yaml
import ipaddress

class Allowlist:
    def __init__(self, path: str = "allowlist.yaml"):
        with open(path, "r") as f:
            doc = yaml.safe_load(f) or {}
        self.cameras = doc.get("cameras", {})

    def check(self, camera_id: str, *, asn: int | None, rdns: str | None, ip: str) -> bool:
        rules = self.cameras.get(camera_id, {})
        # If no rules, default to allow (user decides policy)
        if not rules:
            return True

        # ASN allow
        allowed_asns = set(rules.get("allowed_asns", []) or [])
        if allowed_asns and (asn is None or asn not in allowed_asns):
            return False

        # Domain allow (substring match on RDNS)
        allowed_domains = set(rules.get("allowed_domains", []) or [])
        if allowed_domains:
            if not rdns or not any(dom in rdns for dom in allowed_domains):
                return False

        # CIDR allow
        allowed_cidrs = rules.get("allowed_cidrs", []) or []
        if allowed_cidrs:
            try:
                ip_obj = ipaddress.ip_address(ip)
                ok = any(ip_obj in ipaddress.ip_network(cidr) for cidr in allowed_cidrs)
                if not ok:
                    return False
            except Exception:
                return False

        return True
