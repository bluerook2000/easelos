# pipeline/exporter.py
"""Export CadQuery solids to STEP, SVG, DXF, and PNG."""
import os

import cadquery as cq
import ezdxf


def export_step(solid: cq.Workplane, path: str) -> None:
    """Export a CadQuery solid to STEP format."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cq.exporters.export(solid, path, exportType="STEP")


def export_svg(solid: cq.Workplane, path: str, width: int = 400, height: int = 300) -> None:
    """Export a CadQuery solid to SVG (top-down 2D projection)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cq.exporters.export(
        solid,
        path,
        exportType="SVG",
        opt={
            "width": width,
            "height": height,
            "marginLeft": 10,
            "marginTop": 10,
            "showAxes": False,
            "projectionDir": (0, 0, -1),  # top-down view
            "strokeWidth": 0.5,
            "strokeColor": (0, 0, 0),
            "hiddenColor": (0, 0, 0),
            "showHidden": False,
        },
    )


def export_dxf(solid: cq.Workplane, path: str) -> None:
    """Export the top face profile of a CadQuery solid to DXF via ezdxf.

    Uses CadQuery's DXF export if available (CQ 2.7+), otherwise falls
    back to manual edge extraction with ezdxf.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    # CadQuery 2.7 supports DXF export natively for 2D sections
    try:
        cq.exporters.export(solid, path, exportType="DXF")
        return
    except Exception:
        pass

    # Fallback: extract top face edges manually
    top_face = solid.faces(">Z").val()
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for wire in top_face.Wires():
        for edge in wire.Edges():
            geom_type = edge.geomType()  # returns a string in CQ 2.7

            if geom_type == "CIRCLE":
                center = edge.Center()
                radius = edge.radius()
                msp.add_circle((center.x, center.y), radius)
            elif geom_type == "LINE":
                verts = edge.Vertices()
                if len(verts) == 2:
                    p1 = verts[0].toTuple()
                    p2 = verts[1].toTuple()
                    msp.add_line((p1[0], p1[1]), (p2[0], p2[1]))
            else:
                # ARC or other: tessellate to line segments.
                try:
                    verts = edge.Vertices()
                    start = verts[0].toTuple()
                    end = verts[-1].toTuple()
                    if hasattr(edge, 'tessellate'):
                        tess_result = edge.tessellate(0.1)
                        if isinstance(tess_result, tuple):
                            pts = [(v.x, v.y) for v in tess_result[0]]
                        else:
                            pts = [(v.x, v.y) for v in tess_result]
                        for i in range(len(pts) - 1):
                            msp.add_line(pts[i], pts[i + 1])
                    else:
                        msp.add_line((start[0], start[1]), (end[0], end[1]))
                except Exception:
                    pass

    doc.saveas(path)


def export_png(svg_path: str, png_path: str, width: int = 400) -> None:
    """Convert an SVG file to PNG thumbnail.

    Tries cairosvg first, falls back to a minimal approach if unavailable.
    """
    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)

    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width)
    except ImportError:
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            drawing = svg2rlg(svg_path)
            if drawing:
                renderPM.drawToFile(drawing, png_path, fmt="PNG")
            else:
                raise RuntimeError(f"Failed to parse SVG: {svg_path}")
        except ImportError:
            raise RuntimeError(
                "PNG export requires 'cairosvg' or 'svglib'+'reportlab'. "
                "Install with: pip install cairosvg"
            )
