import drawsvg as draw
import svgpathtools as svgtools
import numpy as np
from typing import *

# Init drawing
d = draw.Drawing(360, 150)

# Constants
ANIM_DURATION = 10

# POINTS
P0: Dict[str, float] = {"x": 50, "y": 120}
P1: Dict[str, float] = {"x": 20, "y": 20}
P2: Dict[str, float] = {"x": 150, "y": 20}
P3: Dict[str, float] = {"x": 250, "y": 120}

times = [(i/100) * ANIM_DURATION for i in range(0, 101)]

# LINES BETWEEN POINTS
P0_P1_Line = draw.Line(
    P0["x"], P0["y"], P1["x"], P1["y"], stroke="#D3D3D3", stroke_width=4, pathLength="10", stroke_linecap="round")
P1_P2_Line = draw.Line(
    P1["x"], P1["y"], P2["x"], P2["y"], stroke="#D3D3D3", stroke_width=4, pathLength="10", stroke_linecap="round")
P2_P3_Line = draw.Line(
    P2["x"], P2["y"], P3["x"], P3["y"], stroke="#D3D3D3", stroke_width=4, pathLength="10", stroke_linecap="round")

d.append(P0_P1_Line)
d.append(P1_P2_Line)
d.append(P2_P3_Line)

# Create and Add P0, P1 Circles
P0_circle = draw.Circle(P0["x"], P0["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P0_text = draw.Text("P", 15, x=P0["x"] + 10, y=P0["y"])
P0_text.append_line("0", baseline_shift="sub", font_size="10")

P1_circle = draw.Circle(P1["x"], P1["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P1_text = draw.Text("P", 15, x=P1["x"] + 10, y=P1["y"])
P1_text.append_line("1", baseline_shift="sub", font_size="10")

P2_circle = draw.Circle(P2["x"], P2["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P2_text = draw.Text("P", 15, x=P2["x"] + 10, y=P2["y"])
P2_text.append_line("2", baseline_shift="sub", font_size="10")

P3_circle = draw.Circle(P3["x"], P3["y"], 5, stroke="black",
                        stroke_width=2, fill_opacity=0)

P3_text = draw.Text("P", 15, x=P3["x"] + 10, y=P3["y"])
P3_text.append_line("3", baseline_shift="sub", font_size="10")

d.append(P0_circle)
d.append(P0_text)

d.append(P1_circle)
d.append(P1_text)

d.append(P2_circle)
d.append(P2_text)

d.append(P3_circle)
d.append(P3_text)

# Create Green line and circles

P0_P1_GreenCircle = draw.Circle(P0["x"], P0["y"], 4, fill="LightGreen")
P0_P1_GreenCircle.add_key_frame(0, cx=P0["x"], cy=P0["y"], animation_args={
                                "repeatCount": "indefinite"})
P0_P1_GreenCircle.add_key_frame(ANIM_DURATION, cx=P1["x"], cy=P1["y"])

P1_P2_GreenCircle = draw.Circle(P1["x"], P1["y"], 4, fill="LightGreen")
P1_P2_GreenCircle.add_key_frame(0, cx=P1["x"], cy=P1["y"], animation_args={
                                "repeatCount": "indefinite"})
P1_P2_GreenCircle.add_key_frame(ANIM_DURATION, cx=P2["x"], cy=P2["y"])

P2_P3_GreenCircle = draw.Circle(P2["x"], P2["y"], 4, fill="LightGreen")
P2_P3_GreenCircle.add_key_frame(0, cx=P2["x"], cy=P2["y"], animation_args={
                                "repeatCount": "indefinite"})
P2_P3_GreenCircle.add_key_frame(ANIM_DURATION, cx=P3["x"], cy=P3["y"])

P0_P2_GreenLine_StartPath = "M%d,%d L%d,%d" % (P0["x"], P0["y"], P1["x"], P1["y"])
P0_P2_GreenLine_EndPath = "M%d,%d L%d,%d" % (P1["x"], P1["y"], P2["x"], P2["y"])

P0_P2_GreenLine = draw.Path(d=P0_P2_GreenLine_StartPath, stroke="LightGreen",
                      stroke_width=2, fill="none", stroke_linecap="round")
P0_P2_GreenLine.add_key_frame(0, d=P0_P2_GreenLine_StartPath, animation_args={
    "repeatCount": "indefinite"})
P0_P2_GreenLine.add_key_frame(ANIM_DURATION, d=P0_P2_GreenLine_EndPath, animation_args={
    "repeatCount": "indefinite"})

P1_P3_GreenLine_StartPath = "M%d,%d L%d,%d" % (P1["x"], P1["y"], P2["x"], P2["y"])
P1_P3_GreenLine_EndPath = "M%d,%d L%d,%d" % (P2["x"], P2["y"], P3["x"], P3["y"])

P1_P3_GreenLine = draw.Path(d=P1_P3_GreenLine_StartPath, stroke="LightGreen",
                      stroke_width=2, fill="none", stroke_linecap="round")
P1_P3_GreenLine.add_key_frame(0, d=P1_P3_GreenLine_StartPath, animation_args={
    "repeatCount": "indefinite"})
P1_P3_GreenLine.add_key_frame(ANIM_DURATION, d=P1_P3_GreenLine_EndPath, animation_args={
    "repeatCount": "indefinite"})

d.append(P0_P1_GreenCircle)
d.append(P1_P2_GreenCircle)
d.append(P2_P3_GreenCircle)
d.append(P0_P2_GreenLine)
d.append(P1_P3_GreenLine)

# Create Blue circles and line

blue_path_1_str = "M%d,%d Q%d,%d %d,%d" % (
    P0["x"], P0["y"], P1["x"], P1["y"], P2["x"], P2["y"])
blue_path_2_str = "M%d,%d Q%d,%d %d,%d" % (
    P1["x"], P1["y"], P2["x"], P2["y"], P3["x"], P3["y"])

blue1_circle_path = draw.Path(blue_path_1_str)
blue2_circle_path = draw.Path(blue_path_2_str)

blue_1_circle = draw.Circle(0, 0, 4, fill="blue")
blue_1_circle.append_anim(draw.AnimateMotion(
    blue1_circle_path, '%ds' % (ANIM_DURATION), repeatCount='indefinite'))

blue_2_circle = draw.Circle(0, 0, 4, fill="blue")
blue_2_circle.append_anim(draw.AnimateMotion(
    blue2_circle_path, '%ds' % (ANIM_DURATION), repeatCount='indefinite'))

blue_line_vals = []

blue_line = draw.Path(stroke="blue",
                     stroke_width=2, fill="none", stroke_linecap="round")

d.append(blue_1_circle)
d.append(blue_2_circle)

# Create and Redline
bezier_path_str = "M%d,%d C%d,%d %d,%d %d,%d" % (
    P0["x"], P0["y"], P1["x"], P1["y"], P2["x"], P2["y"], P3["x"], P3["y"])

b = svgtools.Path(svgtools.CubicBezier(complex(P0["x"],P0["y"]), complex(P1["x"], P1["y"]), complex(P2["x"], P2["y"]), complex(P3["x"], P3["y"])))
print(b.d())

red_line = draw.Path(d=b.d(), stroke="red",stroke_width=2, fill="none", stroke_dasharray="100", stroke_dashoffset="100", pathLength="100", stroke_linecap="round")
red_line.add_key_frame(0, stroke_dashoffset="100", animation_args={"repeatCount": "indefinite"})
red_line.add_key_frame(ANIM_DURATION, stroke_dashoffset="0")

d.append(red_line)

# Create and Add Moving Circle
blue1_circle_path = draw.Path(bezier_path_str)

black_circle = draw.Circle(0, 0, 4, fill="black")
black_circle.append_anim(draw.AnimateMotion(
    blue1_circle_path, '%ds' % (ANIM_DURATION), repeatCount='indefinite'))

d.append(black_circle)

# COUNTER

# Create times and values lists

counter_values = ["t=" + str(i/100).removeprefix("0")for i in range(0, 101)]

# Counter x should be in the middle between the farmost point on the L/R sides
counter_x = P0["x"] + abs((P0["x"] - P2["x"])/2)

# Animate counter
draw.native_animation.animate_text_sequence(d, times,
                                            counter_values,
                                            10, counter_x, 140, fill='black', center=True, looping_anim=True)

d.save_svg('Bézier 3 big.svg')
