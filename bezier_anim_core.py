import drawsvg as draw
import svgpathtools as svgtools
import numpy as np
from typing import *
from random import randint


class BezierAnimation:
    def __init__(self, filename: str, dur: float, bpoints: List[complex], resolution: int = 10) -> None:
        self.bpoints: List[complex] = bpoints
        self.filename: str = filename
        self.dur: float = dur
        self.resolution = resolution

        self.calculate_windowsize()

        self.d: draw.Drawing = draw.Drawing(
            self.WIDTH, self.HEIGHT, self.ORIGIN)

        self.render()

    def render(self):
        self.generate_greys()
        self.generate_points()

        self.generate_bezier()
        self.generate_counter()

        self.d.save_svg(self.filename)

    def generate_greys(self):
        for point_i, bpoint in enumerate(self.bpoints):
            if not point_i >= len(self.bpoints) - 1:
                grey_line = draw.Line(
                    bpoint.real, bpoint.imag, self.bpoints[point_i + 1].real, self.bpoints[point_i + 1].imag, stroke="#D3D3D3", stroke_width=4, pathLength="10", stroke_linecap="round")
                self.d.append(grey_line)

    def generate_points(self):
        for point_i, bpoint in enumerate(self.bpoints):
            p_circle = draw.Circle(bpoint.real, bpoint.imag, 5, stroke="black",
                                   stroke_width=2, fill="none")
            p_text = draw.Text("P", 15, x=bpoint.real + 10, y=bpoint.imag)
            p_text.append_line(
                "%d" % (point_i), baseline_shift="sub", font_size="10")

            self.d.append(p_circle)
            self.d.append(p_text)

    def generate_counter(self):
        # Create times and values lists
        times = [(i/100) * self.dur for i in range(0, 101)]
        counter_values = ["t=" + str(i/100).removeprefix("0")
                          for i in range(0, 101)]

        # Counter x should be in the middle between the farmost point on the L/R sides
        counter_x = self.ORIGIN[0] + abs(self.ORIGIN[0] - self.WIDTH)/2

        # Animate counter
        draw.native_animation.animate_text_sequence(self.d, times,
                                                    counter_values,
                                                    10, counter_x, self.HEIGHT - 50, fill='black', center=True, looping_anim=True)

    def generate_bezier(self):
        curves = [self.bpoints]

        max_len_sublist = max(map(len, curves))

        while max_len_sublist > 4:
            new_curves = []

            for curve_bpoints in curves:
                left_curve_bpoints, right_curve_bpoints = svgtools.split_bezier(
                    curve_bpoints, 0.5)

                new_curves.append(left_curve_bpoints)
                new_curves.append(right_curve_bpoints)

            curves = new_curves

            if len(curves) > self.resolution:
                for i in range(0, len(curves)):
                    while len(curves[i]) > 4:
                        curves[i].pop(randint(1, len(curves[i]) - 2))

            max_len_sublist = max(map(len, curves))

        bezier_path = svgtools.Path()

        for i, curve_bpoints in enumerate(curves):
            bezier_path.insert(i, svgtools.bpoints2bezier(curve_bpoints))

        svg_path = draw.Path(bezier_path.d(), stroke="red",
                             stroke_width=2, fill="none", stroke_dasharray="100", stroke_dashoffset="100", pathLength="100", stroke_linecap="round")

        svg_path.add_key_frame(0, stroke_dashoffset="100", animation_args={"repeatCount": "indefinite"})
        svg_path.add_key_frame(self.dur, stroke_dashoffset="0")

        self.d.append(svg_path)

    def calculate_windowsize(self):
        self.WIDTH: float = 0
        self.HEIGHT: float = 0
        self.ORIGIN: Tuple[float, float] = (0, 0)

        min_x, min_y = None, None
        max_x, max_y = None, None

        for bpoint in self.bpoints:
            if min_x == None or float(bpoint.real) < min_x:
                min_x = float(bpoint.real)
            if min_y == None or float(bpoint.imag) < min_y:
                min_y = float(bpoint.imag)
            if max_x == None or float(bpoint.real) > max_x:
                max_x = float(bpoint.real)
            if max_y == None or float(bpoint.imag) > max_y:
                max_y = float(bpoint.imag)

        self.ORIGIN = (min_x - 50, min_y - 50)
        self.WIDTH = abs(max_x - min_x) + 100
        self.HEIGHT = abs(max_y - min_y) + 100


if __name__ == "__main__":
    test_bpoints = [50+120j, 20+20j, 150+20j, 250+120j, 100+234j, 50+125j]

    b = BezierAnimation("bezier 4.svg", 10.0, test_bpoints, resolution=1000)
