import copy
from dataclasses import dataclass, field

import build123d as bd
from ocp_vscode import show

# =============================================================================
# CONFIGURATION - Edit these values to customize your frame
# =============================================================================


@dataclass
class FrameConfig:
    """Configuration for the PC frame dimensions and bridge placement."""

    # Box dimensions (in mm)
    width: float = 400  # X-axis dimension
    height: float = 200  # Z-axis dimension
    depth: float = 300  # Y-axis dimension

    # Bottom bridges - positions are distance from left edge (X offset from left frame)
    # Each value is the X position where the bridge center will be placed
    bottom_bridge_positions: list[float] = field(default_factory=lambda: [50, 200])

    # Top bridges - positions are distance from left edge (X offset from left frame)
    top_bridge_positions: list[float] = field(default_factory=list)

    def __post_init__(self):
        """Validate configuration parameters."""
        # Calculate usable width (accounting for frame extrusions on both sides)
        usable_width = self.width - 2 * EXTRUSION_2020_SIZE

        # Validate bottom bridge positions
        for i, pos in enumerate(self.bottom_bridge_positions):
            assert pos >= 0, (
                f"Bottom bridge {i + 1} position ({pos}mm) cannot be negative"
            )
            assert pos <= usable_width, (
                f"Bottom bridge {i + 1} position ({pos}mm) exceeds usable width "
                f"({usable_width}mm). Max position = width ({self.width}mm) - "
                f"2 * extrusion size ({EXTRUSION_2020_SIZE}mm)"
            )

        # Validate top bridge positions
        for i, pos in enumerate(self.top_bridge_positions):
            assert pos >= 0, f"Top bridge {i + 1} position ({pos}mm) cannot be negative"
            assert pos <= usable_width, (
                f"Top bridge {i + 1} position ({pos}mm) exceeds usable width "
                f"({usable_width}mm). Max position = width ({self.width}mm) - "
                f"2 * extrusion size ({EXTRUSION_2020_SIZE}mm)"
            )

        # Validate minimum dimensions
        min_dimension = 2 * EXTRUSION_2020_SIZE
        assert self.width >= min_dimension, (
            f"Width ({self.width}mm) must be at least {min_dimension}mm"
        )
        assert self.height >= min_dimension, (
            f"Height ({self.height}mm) must be at least {min_dimension}mm"
        )
        assert self.depth >= min_dimension, (
            f"Depth ({self.depth}mm) must be at least {min_dimension}mm"
        )

    def calculate_extrusion_lengths(self) -> dict:
        """Calculate the length of each extrusion type and total material needed."""
        vertical_length = self.height - EXTRUSION_2020_SIZE
        horizontal_length = self.width
        bridge_length = self.depth - EXTRUSION_2020_SIZE

        num_verticals = 4  # 2 front + 2 back
        num_horizontals = 4  # 2 front + 2 back
        num_bottom_bridges = len(self.bottom_bridge_positions)
        num_top_bridges = len(self.top_bridge_positions)
        num_bridges = num_bottom_bridges + num_top_bridges

        total_vertical = num_verticals * vertical_length
        total_horizontal = num_horizontals * horizontal_length
        total_bridges = num_bridges * bridge_length
        total_length = total_vertical + total_horizontal + total_bridges

        return {
            "vertical": {
                "length": vertical_length,
                "count": num_verticals,
                "total": total_vertical,
            },
            "horizontal": {
                "length": horizontal_length,
                "count": num_horizontals,
                "total": total_horizontal,
            },
            "bridge": {
                "length": bridge_length,
                "count": num_bridges,
                "total": total_bridges,
                "bottom_count": num_bottom_bridges,
                "top_count": num_top_bridges,
            },
            "total_length_mm": total_length,
            "total_length_m": total_length / 1000,
        }

    def print_material_summary(self) -> None:
        """Print a summary of 2020 extrusion material needed."""
        lengths = self.calculate_extrusion_lengths()

        print("\n" + "=" * 60)
        print("2020 EXTRUSION MATERIAL SUMMARY")
        print("=" * 60)
        print(f"\nFrame Dimensions: {self.width}mm x {self.height}mm x {self.depth}mm")
        print("\nExtrusion Breakdown:")
        print("-" * 40)
        print(
            f"  Vertical pieces:   {lengths['vertical']['count']} x "
            f"{lengths['vertical']['length']:.0f}mm = {lengths['vertical']['total']:.0f}mm"
        )
        print(
            f"  Horizontal pieces: {lengths['horizontal']['count']} x "
            f"{lengths['horizontal']['length']:.0f}mm = {lengths['horizontal']['total']:.0f}mm"
        )
        print(
            f"  Bridge pieces:     {lengths['bridge']['count']} x "
            f"{lengths['bridge']['length']:.0f}mm = {lengths['bridge']['total']:.0f}mm"
        )
        print(f"    - Bottom bridges: {lengths['bridge']['bottom_count']}")
        print(f"    - Top bridges:    {lengths['bridge']['top_count']}")
        print("-" * 40)
        print(
            f"\nTOTAL 2020 EXTRUSION NEEDED: "
            f"{lengths['total_length_mm']:.0f}mm ({lengths['total_length_m']:.2f}m)"
        )
        print("=" * 60 + "\n")


# =============================================================================
# CONSTANTS
# =============================================================================

RIGHT_ANGLE = 90
EXTRUSION_2020_SIZE = 20


# =============================================================================
# FUNCTIONS
# =============================================================================


def extrusion_2020(length: float) -> bd.Part:
    prifiles = bd.import_step("2020_t_slot.step")
    faces = prifiles.faces()

    planer_faces = [f for f in faces if f.is_planar and f.length == f.width]

    profile_face = min(planer_faces, key=lambda f: f.area)

    with bd.BuildPart() as part:
        with bd.BuildSketch(bd.Plane.XY):
            bd.add(profile_face)
        bd.extrude(amount=length)

    if not part.part:
        raise ValueError("Part creation failed")

    return part.part


def create_frame(config: FrameConfig) -> bd.Compound:
    """Create a PC frame based on the provided configuration."""

    vertical_extrusion = extrusion_2020(config.height - EXTRUSION_2020_SIZE)
    horizontal_extrusion = extrusion_2020(config.width)
    bridge_extrusion = extrusion_2020(config.depth - EXTRUSION_2020_SIZE)

    left1 = copy.copy(vertical_extrusion)
    right1 = copy.copy(vertical_extrusion)
    top1 = copy.copy(horizontal_extrusion)
    bottom1 = copy.copy(horizontal_extrusion)

    left1.label = "front_left"
    right1.label = "front_right"
    top1.label = "front_top"
    bottom1.label = "front_bottom"

    left1.location = bd.Location((0, 0, 0), (0, 0, 0))
    right1.location = bd.Location((config.width - EXTRUSION_2020_SIZE, 0, 0), (0, 0, 0))
    top1.location = bd.Location((0, 0, config.height), (0, RIGHT_ANGLE, 0))
    bottom1.location = bd.Location((0, 0, 0), (0, RIGHT_ANGLE, 0))

    frame1 = bd.Compound(
        label="front_frame",
        children=[top1, bottom1, left1, right1],
    )

    # Frame 2 (back face at Y=depth) - deep copy frame1 and adjust
    frame2 = copy.deepcopy(frame1)
    frame2.label = "back_frame"

    # Update labels and locations for back frame children
    for child in frame2.children:
        # Update labels: "front_*" -> "back_*"
        if child.label.startswith("front_"):
            child.label = child.label.replace("front_", "back_")

        # Update locations: add config.depth to Y coordinate
        if child.location:
            current_pos = child.location.position
            current_rot = child.location.orientation

            # Convert position to tuple if needed (handles Vector or tuple)
            pos_tuple = (
                tuple(current_pos)
                if hasattr(current_pos, "__iter__")
                else (current_pos.x, current_pos.y, current_pos.z)
            )
            rot_tuple = (
                tuple(current_rot)
                if hasattr(current_rot, "__iter__")
                else (current_rot.x, current_rot.y, current_rot.z)
            )

            # Create new position with Y offset
            new_pos = (pos_tuple[0], pos_tuple[1] + config.depth, pos_tuple[2])
            child.location = bd.Location(new_pos, rot_tuple)

    # Create bottom bridges
    bottom_bridges = []
    for i, x_pos in enumerate(config.bottom_bridge_positions):
        bridge = copy.copy(bridge_extrusion)
        bridge.label = f"bottom_bridge_{i + 1}"
        bridge.location = bd.Location(
            (
                x_pos,
                config.depth,
                -EXTRUSION_2020_SIZE,
            ),
            (RIGHT_ANGLE, 0, 0),
        )
        bottom_bridges.append(bridge)

    top_bridges = []
    for i, x_pos in enumerate(config.top_bridge_positions):
        bridge = copy.copy(bridge_extrusion)
        bridge.label = f"top_bridge_{i + 1}"
        bridge.location = bd.Location(
            (
                x_pos,
                config.depth,
                config.height - EXTRUSION_2020_SIZE,
            ),
            (RIGHT_ANGLE, 0, 0),
        )
        top_bridges.append(bridge)

    all_children = [frame1, frame2] + bottom_bridges + top_bridges

    return bd.Compound(label="pc_frame", children=all_children)


if __name__ == "__main__":
    # ==========================================================================
    # CONFIGURE YOUR FRAME HERE
    # ==========================================================================
    config = FrameConfig(
        # Box dimensions
        width=500,  # mm
        height=270,  # mm
        depth=353.3,  # mm
        # Bottom bridge X positions (distance from left edge)
        # Example: [50, 200] places bridges at 50mm and 200mm from left
        bottom_bridge_positions=[100, 200, 300, 400],
        # Top bridge X positions (distance from left edge)
        # Example: [100, 300] places bridges at 100mm and 300mm from left
        top_bridge_positions=[50, 350],
    )
    # ==========================================================================

    config.print_material_summary()

    box = create_frame(config)
    show(box)
