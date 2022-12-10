from math import cos, sin, atan2, sqrt
from typing import Tuple, Optional, List

import pyglet
from pyglet import shapes


def circle_intersections(x0, y0, r0, x1, y1, r1):
    # This was copied from https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles

    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

    # non intersecting
    if d > r0 + r1:
        return None
    # One circle within other
    if d < abs(r0 - r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = sqrt(r0 ** 2 - a ** 2)
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        x3 = x2 + h * (y1 - y0) / d
        y3 = y2 - h * (x1 - x0) / d

        x4 = x2 - h * (y1 - y0) / d
        y4 = y2 + h * (x1 - x0) / d

        return x3, y3, x4, y4


def get_arm_angles(x: float, y: float, arm_lengths: Tuple[float, ...]) \
        -> Optional[List[float]]:
    """Get the angles that each joint of the arm should be oriented to

    The arm is positioned at the origin, and it must reach (x, y).
    The angles are returned in radians between -pi and pi. They are returned in the same
    order that the arms are given in arm_lengths.
    The arm will bend in at most two places
    """
    d = sqrt(x ** 2 + y ** 2)
    if d > sum(arm_lengths):
        return None
    if d == 0:
        return None

    # The arm only needs to bend in at most two places (I think), so we need to find out
    # how long each straight section should be, and what angle they should be at.

    # final position
    x3, y3 = x, y

    # angle of the first joint
    angle_1 = atan2(-y, -x)

    # determine how long the three straight sections should be
    # Keep adding to the first section until the joints are in range of each other. The
    # second straight section only contains one arm.
    arm_length_1 = 0.0
    arm_length_3 = sum(arm_lengths[1:])
    second_arm_index = 0
    while arm_length_3 > d + arm_length_1 + arm_lengths[second_arm_index]:
        arm_length_1 += arm_lengths[second_arm_index]
        arm_length_3 -= arm_lengths[second_arm_index + 1]
        second_arm_index += 1
    arm_length_2 = arm_lengths[second_arm_index]

    # calculate the coordinates of the first joint
    scale_factor = -arm_length_1 / d
    x1, y1 = x * scale_factor, y * scale_factor

    # calculate the coordinates of the second joint
    intersection = circle_intersections(
        x1,
        y1,
        arm_length_2,
        x3,
        y3,
        arm_length_3,
    )
    if intersection is None:
        return None
    x2, y2, *_ = intersection

    # calculate the angles of the second and third joints
    angle_2 = atan2(y2 - y1, x2 - x1)
    angle_3 = atan2(y3 - y2, x3 - x2)

    return (
        [angle_1] * second_arm_index
        + [angle_2]
        + [angle_3] * (len(arm_lengths) - second_arm_index - 1)
    )


def main():
    width, height = 800, 600
    arm_lengths = 200, 200, 150, 150, 200, 200

    window = pyglet.window.Window(width=width, height=height)

    batch = pyglet.graphics.Batch()

    # Lines to represent teh arms
    lines = []
    for length in arm_lengths:
        angle = 0.0
        line = shapes.Line(
            width // 2,
            height // 2,
            width // 2 + int(length * cos(angle)),
            height // 2 + int(length * sin(angle)),
            width=5,
            batch=batch,
        )
        lines.append(line)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        # Calculate arm angles, and update the lines on the screen.

        angles = get_arm_angles(x - width // 2, y - height // 2, arm_lengths)
        if angles is None:
            return

        arm_x, arm_y = width // 2, height // 2
        for line, angle, length in zip(lines, angles, arm_lengths):
            line.x = arm_x
            line.y = arm_y
            line.x2 = arm_x + int(length * cos(angle))
            line.y2 = arm_y + int(length * sin(angle))
            arm_x = line.x2
            arm_y = line.y2

    pyglet.app.run()


if __name__ == "__main__":
    main()
