import drawsvg as draw
import svgpathtools as svgtools
import numpy as np
from typing import *
from random import randint

ORDER_COLOURS = {
    4: "pink",
    3: "blue",
    2: "green"
}


def path_from_polybezier(bpoints: List[complex], resolution: int) -> svgtools.Path:
    curves = [bpoints]

    max_len_sublist = max(map(len, curves))

    while max_len_sublist > 4:
        new_curves = []

        for curve_bpoints in curves:
            left_curve_bpoints, right_curve_bpoints = svgtools.split_bezier(
                curve_bpoints, 0.5)

            new_curves.append(left_curve_bpoints)
            new_curves.append(right_curve_bpoints)

        curves = new_curves

        if len(curves) > resolution:
            for i in range(0, len(curves)):
                while len(curves[i]) > 4:
                    curves[i].pop(randint(1, len(curves[i]) - 2))

        max_len_sublist = max(map(len, curves))

    bezier_path = svgtools.Path()

    for i, curve_bpoints in enumerate(curves):
        bezier_path.insert(i, svgtools.bpoints2bezier(curve_bpoints))

    return bezier_path


class BezierAnimation:
    def __init__(self, filename: str, dur: float, bpoints: List[complex], resolution: int = 10, frame_count: int = 100) -> None:
        self.bpoints: List[complex] = bpoints
        self.filename: str = filename
        self.dur: float = dur
        self.resolution: int = resolution
        self.frame_count: int = frame_count

        self.calculate_windowsize()

        self.d: draw.Drawing = draw.Drawing(
            self.WIDTH, self.HEIGHT, self.ORIGIN)

        self.render()

    def render(self):
        self.generate_greys()
        self.generate_points()

        self.generate_structure()

        self.generate_red_bezier()
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
        times, counter_values = [], []

        for i in range(0, self.frame_count + 1):
            t = (i/self.frame_count)
            time = t * self.dur
            counter_value = "t=" + str(t).removeprefix("0")

            times.append(time)
            counter_values.append(counter_value)

        # Counter x should be in the middle between the farmost point on the L/R sides
        counter_x = self.ORIGIN[0] + abs(self.ORIGIN[0] - self.WIDTH)/2

        # Animate counter
        draw.native_animation.animate_text_sequence(self.d, times,
                                                    counter_values,
                                                    10, counter_x, self.HEIGHT - 50, fill='black', center=True, looping_anim=True)

    def generate_structure(self):
        obj_list = []
        
        def recursive_generate(b_points):
            order = len(b_points) - 1

            if order <= 1:
                return

            # First Circle Array: b_points[:-1]
            # Second Circle Array: b_points[:-1]

            first_tools_path = path_from_polybezier(
                b_points[:-1], self.resolution)
            second_tools_path = path_from_polybezier(
                b_points[1:], self.resolution)

            first_path = draw.Path(first_tools_path.d())
            second_path = draw.Path(second_tools_path.d())

            def d_at_t(t: float):
                point1: complex = first_tools_path.point(t)
                point2: complex = second_tools_path.point(t)

            times, d_vals = [], []
            first_circle_positions_x, second_circle_positions_x = [],[]
            first_circle_positions_y, second_circle_positions_y = [],[]

            for i in range(0, self.frame_count + 1):
                t = (i/self.frame_count)
                time = t * self.dur

                point1: complex = first_tools_path.point(t)
                point2: complex = second_tools_path.point(t)

                d_val = "M%lf,%lf L%lf,%lf" % (
                    point1.real, point1.imag, point2.real, point2.imag)

                times.append(time)
                d_vals.append(d_val)
                
                first_circle_positions_x.append(point1.real)
                first_circle_positions_y.append(point1.imag)
                
                second_circle_positions_x.append(point2.real)
                second_circle_positions_y.append(point2.imag)

            line = draw.Path(d_at_t(
                0), fill="none", stroke=ORDER_COLOURS[order], stroke_opacity="20%", stroke_width=2, pathLength="10", stroke_linecap="round")
            line.add_attribute_key_sequence("d", times, d_vals, animation_args={
                "repeatCount": "indefinite"})

            first_circle = draw.Circle(0, 0, 4, fill=ORDER_COLOURS[order])
            first_circle.add_attribute_key_sequence("cx", times, first_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            first_circle.add_attribute_key_sequence("cy", times, first_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            second_circle = draw.Circle(0, 0, 4, fill=ORDER_COLOURS[order])
            second_circle.add_attribute_key_sequence("cx", times, second_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            second_circle.add_attribute_key_sequence("cy", times, second_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            obj_list.append(first_circle)
            obj_list.append(second_circle)
            obj_list.append(line)

            recursive_generate(b_points[:-1])
            recursive_generate(b_points[1:])

        recursive_generate(self.bpoints)
        
        for drawable in obj_list[::-1]:
            self.d.append(drawable)

    def generate_red_bezier(self):
        bezier_path = path_from_polybezier(self.bpoints, self.resolution)

        svg_path = draw.Path(bezier_path.d(), stroke="red",
                             stroke_width=2, fill="none", stroke_dasharray="100", stroke_dashoffset="100", pathLength="100", stroke_linecap="round")

        svg_path.add_key_frame(0, stroke_dashoffset="100", animation_args={
                               "repeatCount": "indefinite"})
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
    test_bpoints = [50+120j, 20+20j, 150+20j, 250+120j, 300+34j]

    b = BezierAnimation("bezier 4.svg", 10.0, test_bpoints,
                        resolution=1000, frame_count=1000)
