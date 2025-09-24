from __future__ import annotations
import os, sys, stat, subprocess
from importlib import resources

def _script_path() -> str:
    with resources.as_file(resources.files("camtrace").joinpath("bin/pcap_to_camtrace.sh")) as p:
        return str(p)

def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    script = _script_path()
    try:
        st = os.stat(script)
        os.chmod(script, st.st_mode | stat.S_IXUSR)
    except Exception:
        pass
    return subprocess.run([script] + argv).returncode

if __name__ == "__main__":
    raise SystemExit(main())
