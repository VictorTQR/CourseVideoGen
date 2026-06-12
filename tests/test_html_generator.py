import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.html_generator import HTMLSlideRenderer

def test_render_returns_tuples(tmp_path):
    renderer = HTMLSlideRenderer(str(tmp_path))
    os.makedirs(os.path.join(str(tmp_path), "slides"), exist_ok=True)

    html = """<!DOCTYPE html>
<html><body>
<div class="slide" id="slide-1">Hello World</div>
<div class="slide" id="slide-2">Second Page</div>
</body></html>"""
    html_path = os.path.join(str(tmp_path), "test.html")
    with open(html_path, "w") as f:
        f.write(html)

    results = renderer.render_to_images(html_path)

    assert isinstance(results, list)
    assert len(results) == 2
    for item in results:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], str)
        assert isinstance(item[1], str)
