import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.video_generator import VideoGenerator
from models.project import Project, Slide

def test_generate_raises_on_none_duration(tmp_path):
    project = Project(
        name="test",
        slides=[Slide(id=1, image="fake.png", duration=None)]
    )

    generator = VideoGenerator(str(tmp_path))

    with pytest.raises(ValueError, match="duration 未设置"):
        generator.generate_final_video(project.slides, str(tmp_path / "output.mp4"))
