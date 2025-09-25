from dotenv import load_dotenv
load_dotenv()

# src/camtrace/__main__.py
from .cli import main
if __name__ == "__main__":
    raise SystemExit(main())
