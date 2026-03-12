# pipeline/exporter.py
"""Export CadQuery solids to STEP, SVG, DXF, PNG, and glTF."""
import os
import struct
import json as json_mod

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


def export_glb(solid: cq.Workplane, path: str) -> bool:
    """Export a CadQuery solid to binary glTF (.glb) format.

    Uses CadQuery's tessellate() to get vertices and triangles,
    then packs them into a glTF 2.0 binary container.

    Returns True on success, False if tessellation fails.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    try:
        shape = solid.val()
        vertices, triangles = shape.tessellate(0.1, 0.1)
    except Exception:
        return False

    if not vertices or not triangles:
        return False

    # Convert to flat arrays
    vert_data = bytearray()
    min_pos = [float("inf")] * 3
    max_pos = [float("-inf")] * 3
    for v in vertices:
        x, y, z = float(v.x), float(v.y), float(v.z)
        vert_data.extend(struct.pack("<fff", x, y, z))
        for i, val in enumerate((x, y, z)):
            min_pos[i] = min(min_pos[i], val)
            max_pos[i] = max(max_pos[i], val)

    # Use UNSIGNED_INT if vertex count exceeds UNSIGNED_SHORT range
    use_uint32 = len(vertices) > 65535

    idx_data = bytearray()
    for tri in triangles:
        if use_uint32:
            idx_data.extend(struct.pack("<III", tri[0], tri[1], tri[2]))
        else:
            idx_data.extend(struct.pack("<HHH", tri[0], tri[1], tri[2]))

    # Pad to 4-byte alignment
    while len(vert_data) % 4:
        vert_data.append(0)
    while len(idx_data) % 4:
        idx_data.append(0)

    bin_data = bytes(idx_data) + bytes(vert_data)
    idx_byte_len = len(idx_data)
    vert_byte_len = len(vert_data)

    num_vertices = len(vertices)
    num_indices = len(triangles) * 3

    # Build glTF JSON
    gltf = {
        "asset": {"version": "2.0", "generator": "easelos-pipeline"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 1},
                "indices": 0,
                "mode": 4,  # TRIANGLES
            }]
        }],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5125 if use_uint32 else 5123,  # UNSIGNED_INT or UNSIGNED_SHORT
                "count": num_indices,
                "type": "SCALAR",
                "max": [num_indices - 1],
                "min": [0],
            },
            {
                "bufferView": 1,
                "componentType": 5126,  # FLOAT
                "count": num_vertices,
                "type": "VEC3",
                "max": max_pos,
                "min": min_pos,
            },
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": len(triangles) * (12 if use_uint32 else 6),  # 3 indices * (4 or 2) bytes
                "target": 34963,  # ELEMENT_ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": idx_byte_len,
                "byteLength": num_vertices * 12,  # 3 floats * 4 bytes
                "target": 34962,  # ARRAY_BUFFER
            },
        ],
        "buffers": [{"byteLength": len(bin_data)}],
    }

    json_str = json_mod.dumps(gltf, separators=(",", ":"))
    # Pad JSON to 4-byte alignment
    while len(json_str) % 4:
        json_str += " "
    json_bytes = json_str.encode("utf-8")

    # Assemble glb
    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_data)

    with open(path, "wb") as f:
        # Header
        f.write(struct.pack("<4sII", b"glTF", 2, total_length))
        # JSON chunk
        f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        f.write(json_bytes)
        # BIN chunk
        f.write(struct.pack("<II", len(bin_data), 0x004E4942))
        f.write(bin_data)

    return True
