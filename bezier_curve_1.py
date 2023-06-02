import drawsvg as draw
from typing import *

# Init drawing
d = draw.Drawing(150, 150)

# Constants
ANIM_DURATION = 10

P0: Dict[str, float] = {"x": 30, "y": 30}
P1: Dict[str, float] = {"x": 110, "y": 110}

# Create light grey line between points P0 and P1
light_grey_line = draw.Line(
    P0["x"], P0["y"], P1["x"], P1["y"], stroke="#D3D3D3", stroke_width=4)
d.append(light_grey_line)

# Create and Add P0, P1 Circles
P0_circle = draw.Circle(P0["x"], P0["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P0_text = draw.Text("P0", 15, x=P0["x"] + 10, y = P0["y"])

P1_circle = draw.Circle(P1["x"], P1["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P1_text = draw.Text("P1", 15, x=P1["x"] + 10, y = P1["y"])

d.append(P0_circle)
d.append(P0_text)

d.append(P1_circle)
d.append(P1_text)


# Create and Add Moving Line
red_line = draw.Line(P0["x"], P0["y"],
                        P0["x"], P0["y"], stroke="red", stroke_width=4)

red_line_initial_pos = "M%d,%d L%d,%d " % (
    P0["x"], P0["y"], P0["x"], P0["y"])
red_line_final_pos = "M%d,%d L%d,%d " % (
    P0["x"], P0["y"], P1["x"], P1["y"])

red_line.add_key_frame(0, d=red_line_initial_pos, animation_args={"repeatCount": "indefinite"})
red_line.add_key_frame(ANIM_DURATION, d=red_line_final_pos)
d.append(red_line)

# Create and Add Moving Circle
black_circle = draw.Circle(
    P0["x"], P0["y"], 4, fill_color="black")
black_circle.add_key_frame(0, cx=P0["x"], cy=P0["y"], animation_args={
                            "repeatCount": "indefinite"})
black_circle.add_key_frame(
    ANIM_DURATION, cx=P1["x"], cy=P1["y"])

d.append(black_circle)

# Create times and values lists
times = [(i/100) * ANIM_DURATION for i in range(0,101)]
values = ["t=" + str(i/100).removeprefix("0")for i in range(0, 101)]

# Animate counter
counter_x = P0["x"] + abs((P0["x"] - P1["x"])/2)
draw.native_animation.animate_text_sequence(d, times,
                                            values,
                                            10, counter_x, 140, fill='black', center=True, looping_anim=True)

d.save_svg('Bézier 1 big.svg')
