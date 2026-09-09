import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
