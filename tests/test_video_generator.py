import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from videogen.core.video_generator import VideoGenerator
from videogen.models.project import Project, Slide

def test_generate_raises_on_none_duration(tmp_path):
    # 创建 slides 目录并添加测试图片
    slides_dir = tmp_path / "slides"
    slides_dir.mkdir()
    (slides_dir / "fake.png").write_bytes(b'fake image content')

    project = Project(
        name="test",
        slides=[Slide(id=1, image="fake.png", duration=None)]
    )

    generator = VideoGenerator(str(tmp_path))

    with pytest.raises(ValueError, match="duration 未设置"):
        generator.generate_final_video(project.slides, str(tmp_path / "output.mp4"))
