import importlib.util
from pathlib import Path

BUILD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build.py"
SPEC = importlib.util.spec_from_file_location("build", BUILD_PATH)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


def test_build_main_wraps_fragment_into_document(tmp_path, monkeypatch):
    source = """<title>Demo</title>
<style>
body { color: #fff; }
</style>
<div>neuromorphic webcam</div>
<script>console.log('ok')</script>
"""
    src = tmp_path / "app.html"
    out = tmp_path / "index.html"
    src.write_text(source, encoding="utf-8")

    monkeypatch.setattr(build, "ROOT", tmp_path)
    monkeypatch.setattr(build, "SRC", src)
    monkeypatch.setattr(build, "OUT", out)

    split = source.index("</style>") + len("</style>")
    expected = build.SKELETON.format(
        head=source[:split].strip(),
        body=source[split:].strip(),
    )

    build.main()

    assert out.read_text(encoding="utf-8") == expected
