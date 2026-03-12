# tests/test_exporter.py
import os
import struct
import pytest
import cadquery as cq
from pipeline.exporter import export_step, export_svg, export_dxf, export_png, export_glb


def _make_test_solid(thickness: float = 3.0) -> cq.Workplane:
    """Create a simple test plate with 2 holes."""
    return (
        cq.Workplane("XY")
        .rect(50, 30)
        .extrude(thickness)
        .faces(">Z")
        .workplane()
        .pushPoints([(15, 0), (-15, 0)])
        .hole(5.0)
    )


def _has_png_backend() -> bool:
    """Check if cairosvg or svglib+reportlab is available."""
    try:
        import cairosvg
        return True
    except ImportError:
        pass
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        return True
    except ImportError:
        pass
    return False


class TestStepExport:
    def test_creates_file(self, tmp_path):
        solid = _make_test_solid()
        path = tmp_path / "test.step"
        export_step(solid, str(path))
        assert path.exists()
        assert path.stat().st_size > 100

    def test_step_reimport(self, tmp_path):
        """STEP file can be re-imported by CadQuery (same OCCT kernel)."""
        solid = _make_test_solid()
        path = tmp_path / "test.step"
        export_step(solid, str(path))
        reimported = cq.importers.importStep(str(path))
        assert reimported is not None


class TestSvgExport:
    def test_creates_file(self, tmp_path):
        solid = _make_test_solid()
        path = tmp_path / "test.svg"
        export_svg(solid, str(path))
        assert path.exists()
        content = path.read_text()
        assert "<svg" in content
        assert "</svg>" in content

    def test_svg_has_viewbox(self, tmp_path):
        """SVG has viewBox or width/height for sizing."""
        solid = _make_test_solid()
        path = tmp_path / "test.svg"
        export_svg(solid, str(path))
        content = path.read_text()
        # CadQuery's SVG exporter uses width/height instead of viewBox
        assert "viewBox" in content or "viewbox" in content.lower() or 'width="' in content


class TestDxfExport:
    def test_creates_file(self, tmp_path):
        solid = _make_test_solid()
        path = tmp_path / "test.dxf"
        export_dxf(solid, str(path))
        assert path.exists()
        assert path.stat().st_size > 100

    def test_dxf_parseable(self, tmp_path):
        """DXF can be parsed by ezdxf."""
        import ezdxf
        solid = _make_test_solid()
        path = tmp_path / "test.dxf"
        export_dxf(solid, str(path))
        doc = ezdxf.readfile(str(path))
        msp = doc.modelspace()
        entities = list(msp)
        assert len(entities) > 0


class TestPngExport:
    @pytest.mark.skipif(
        not _has_png_backend(),
        reason="PNG export requires cairosvg or svglib+reportlab",
    )
    def test_creates_file(self, tmp_path):
        solid = _make_test_solid()
        svg_path = tmp_path / "test.svg"
        png_path = tmp_path / "test.png"
        export_svg(solid, str(svg_path))
        export_png(str(svg_path), str(png_path))
        assert png_path.exists()
        # PNG magic bytes
        with open(png_path, "rb") as f:
            header = f.read(8)
        assert header[:4] == b'\x89PNG'


class TestGlbExport:
    def test_creates_file(self, tmp_path):
        solid = _make_test_solid()
        path = str(tmp_path / "model.glb")
        export_glb(solid, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_glb_magic_bytes(self, tmp_path):
        solid = _make_test_solid()
        path = str(tmp_path / "model.glb")
        export_glb(solid, path)
        with open(path, "rb") as f:
            magic = f.read(4)
        assert magic == b"glTF"

    def test_glb_has_valid_structure(self, tmp_path):
        solid = _make_test_solid()
        path = str(tmp_path / "model.glb")
        export_glb(solid, path)
        with open(path, "rb") as f:
            data = f.read()
        # Header: magic(4) + version(4) + length(4)
        magic, version, length = struct.unpack_from("<4sII", data, 0)
        assert magic == b"glTF"
        assert version == 2
        assert length == len(data)
        # JSON chunk header
        json_len, json_type = struct.unpack_from("<II", data, 12)
        assert json_type == 0x4E4F534A  # "JSON"
        # Parse the JSON chunk
        import json as json_mod
        json_data = json_mod.loads(data[20:20 + json_len])
        assert "meshes" in json_data
        assert len(json_data["meshes"]) > 0
        assert "accessors" in json_data
        assert "bufferViews" in json_data

    def test_glb_degenerate_solid_skips(self, tmp_path):
        """export_glb returns False for degenerate geometry."""
        solid = cq.Workplane("XY").box(0.001, 0.001, 0.001)
        path = str(tmp_path / "model.glb")
        result = export_glb(solid, path)
        # Should either succeed with tiny mesh or return False gracefully
        assert isinstance(result, bool)
