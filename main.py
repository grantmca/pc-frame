from operator import add
import build123d as bd
import cadquery as cq

from ocp_vscode import show

BOX_HEIGHT = 50

BOX_WIDTH = 100

RIGHT_ANGLE = 90

EXTRUSION_2020_SIZE = 20


def extrusion_2020(length: float) -> bd.Part:
    prifiles = bd.import_step("vslot-2020_1.step")
    faces = prifiles.faces()

    planer_faces = [f for f in faces if f.is_planar]

    profile_face = max(planer_faces, key=lambda f: f.area)

    with bd.BuildPart() as part:
        with bd.BuildSketch(bd.Plane.XY):
            bd.add(profile_face)
        bd.extrude(amount=length)

    if part.part:
        return part.part
    raise ValueError("Part creation failed")


if __name__ == "__main__":
    slot = cq.importers.importDXF("vslot-2020_1.dxf").wires()

    solid = slot.toPending().extrude(1)

    cq.exporters.export(solid, "vslot-2020_1.step")

    left = extrusion_2020(
        BOX_HEIGHT - EXTRUSION_2020_SIZE
    )  # Vertical extrusion for left side
    right = extrusion_2020(
        BOX_HEIGHT - EXTRUSION_2020_SIZE
    )  # Vertical extrusion for right side

    top = extrusion_2020(BOX_WIDTH)  # Horizontal extrusion for top
    bottom = extrusion_2020(BOX_WIDTH)  # Horizontal extrusion for bottom

    top.label = "top"
    bottom.label = "bottom"
    left.label = "left"
    right.label = "right"

    left.location = bd.Location((EXTRUSION_2020_SIZE / 2, 0, 0), (0, 0, 0))

    right.location = bd.Location((BOX_WIDTH - EXTRUSION_2020_SIZE / 2, 0, 0), (0, 0, 0))

    top.location = bd.Location(
        (0, 0, BOX_HEIGHT - EXTRUSION_2020_SIZE / 2), (0, RIGHT_ANGLE, 0)
    )

    bottom.location = bd.Location((0, 0, -EXTRUSION_2020_SIZE / 2), (0, RIGHT_ANGLE, 0))

    frame = bd.Compound(
        label="frame",
        children=[top, bottom, left, right],
    )

    show(frame)
