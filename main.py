from build123d import (
    BuildPart,
    BuildSketch,
    Compound,
    Location,
    Plane,
    Rectangle,
    extrude,
    fillet,
)
from ocp_vscode import show

BOX_HEIGHT = 50

BOX_WIDTH = 100

RIGHT_ANGLE = 90

EXTRUSION_2020_SIZE = 20

def extrusion_2020(
    length: float,
):
    with BuildPart() as part:
        with BuildSketch(Plane.XY) as sq:
            Rectangle(EXTRUSION_2020_SIZE, EXTRUSION_2020_SIZE)
            fillet(sq.vertices(), radius=1.5)
        extrude(amount=length)
    if part.part is not None:
        return part.part
    raise ValueError("Part creation failed")


if __name__ == "__main__":
    left = extrusion_2020(BOX_HEIGHT - EXTRUSION_2020_SIZE)  # Vertical extrusion for left side
    right = extrusion_2020(BOX_HEIGHT - EXTRUSION_2020_SIZE)  # Vertical extrusion for right side

    top = extrusion_2020(BOX_WIDTH)  # Horizontal extrusion for top
    bottom = extrusion_2020(BOX_WIDTH)  # Horizontal extrusion for bottom

    top.label = "top"
    bottom.label = "bottom"
    left.label = "left"
    right.label = "right"

    left.location = Location((EXTRUSION_2020_SIZE/2, 0, 0), (0, 0, 0))

    right.location = Location((BOX_WIDTH - EXTRUSION_2020_SIZE/2, 0, 0), (0, 0, 0))

    top.location = Location((0, 0, BOX_HEIGHT - EXTRUSION_2020_SIZE/2), (0, RIGHT_ANGLE, 0))

    bottom.location = Location((0, 0, -EXTRUSION_2020_SIZE/2), (0, RIGHT_ANGLE, 0))

    frame = Compound(
        label="frame",
        children=[top, bottom, left, right],
    )
    print(frame.show_topology())
    show(frame)

