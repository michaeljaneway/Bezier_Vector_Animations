import drawsvg as draw
import svgpathtools as svgtools
import numpy as np
from typing import *
from random import randint

ORDER_COLOURS = {
    7: "brown",
    6: "magenta",
    5: "yellow",
    4: "#D16587",
    3: "blue",
    2: "green"
}


def path_to_rounded_d(path=svgtools.path,  useSandT=False, use_closed_attrib=False, rel=False):
    """Returns a path d-string for the path object.
    For an explanation of useSandT and use_closed_attrib, see the
    compatibility notes in the README."""
    if len(path) == 0:
        return ''
    if use_closed_attrib:
        self_closed = path.iscontinuous() and path.isclosed()
        if self_closed:
            segments = path[:-1]
        else:
            segments = path[:]
    else:
        self_closed = False
        segments = path[:]

    current_pos = None
    parts = []
    previous_segment = None
    end = path[-1].end

    for segment in segments:
        seg_start = segment.start
        # If the start of this segment does not coincide with the end of
        # the last segment or if this segment is actually the close point
        # of a closed path, then we should start a new subpath here.
        if current_pos != seg_start or \
                (self_closed and seg_start == end and use_closed_attrib):
            if rel:
                _seg_start = seg_start - current_pos if current_pos is not None else seg_start
            else:
                _seg_start = seg_start
            parts.append('M {:.2f},{:.2f}'.format(
                _seg_start.real, _seg_start.imag))

        if isinstance(segment, svgtools.Line):
            if rel:
                _seg_end = segment.end - seg_start
            else:
                _seg_end = segment.end
            parts.append('L {:.2f},{:.2f}'.format(
                _seg_end.real, _seg_end.imag))
        elif isinstance(segment, svgtools.CubicBezier):
            if useSandT and segment.is_smooth_from(previous_segment,
                                                   warning_on=False):
                if rel:
                    _seg_control2 = segment.control2 - seg_start
                    _seg_end = segment.end - seg_start
                else:
                    _seg_control2 = segment.control2
                    _seg_end = segment.end
                args = (_seg_control2.real, _seg_control2.imag,
                        _seg_end.real, _seg_end.imag)
                parts.append('S {:.2f},{:.2f} {:.2f},{:.2f}'.format(*args))
            else:
                if rel:
                    _seg_control1 = segment.control1 - seg_start
                    _seg_control2 = segment.control2 - seg_start
                    _seg_end = segment.end - seg_start
                else:
                    _seg_control1 = segment.control1
                    _seg_control2 = segment.control2
                    _seg_end = segment.end
                args = (_seg_control1.real, _seg_control1.imag,
                        _seg_control2.real, _seg_control2.imag,
                        _seg_end.real, _seg_end.imag)
                parts.append(
                    'C {:.2f},{:.2f} {:.2f},{:.2f} {:.2f},{:.2f}'.format(*args))
        elif isinstance(segment, svgtools.QuadraticBezier):
            if useSandT and segment.is_smooth_from(previous_segment,
                                                   warning_on=False):
                if rel:
                    _seg_end = segment.end - seg_start
                else:
                    _seg_end = segment.end
                args = _seg_end.real, _seg_end.imag
                parts.append('T {:.2f},{:.2f}'.format(*args))
            else:
                if rel:
                    _seg_control = segment.control - seg_start
                    _seg_end = segment.end - seg_start
                else:
                    _seg_control = segment.control
                    _seg_end = segment.end
                args = (_seg_control.real, _seg_control.imag,
                        _seg_end.real, _seg_end.imag)
                parts.append('Q {:.2f},{:.2f} {:.2f},{:.2f}'.format(*args))

        elif isinstance(segment, svgtools.Arc):
            if rel:
                _seg_end = segment.end - seg_start
            else:
                _seg_end = segment.end
            args = (segment.radius.real, segment.radius.imag,
                    segment.rotation, int(segment.large_arc),
                    int(segment.sweep), _seg_end.real, _seg_end.imag)
            parts.append(
                'A {:.2f},{:.2f} {:.2f} {:d},{:d} {:.2f},{:.2f}'.format(*args))
        current_pos = segment.end
        previous_segment = segment

    if self_closed:
        parts.append('Z')

    s = ' '.join(parts)
    return s if not rel else s.lower()


def text_sequence(container: draw.Drawing, times: List[float], values: List[str],
                  *text_args, looping_anim: bool = False, kwargs_list=None, **text_kwargs):
    if kwargs_list is None:
        kwargs_list = [None] * len(values)

    new_elements: List[draw.Text] = []

    for val, current_kw in zip(values, kwargs_list):
        kwargs = dict(text_kwargs)
        if current_kw is not None:
            kwargs.update(current_kw)
        new_elements.append(draw.Text(val, *text_args, **kwargs))

    for i, elem in enumerate(new_elements):
        if elem is None:
            continue

        key_times = []
        values = []

        for j, time in enumerate(times):

            key_times.append(time)

            if i == j:
                values.append("visible")
            else:
                values.append("hidden")

        if looping_anim:
            elem.add_attribute_key_sequence('visibility', key_times, values, animation_args={
                                            "repeatCount": "indefinite"})
        else:
            elem.add_attribute_key_sequence('visibility', key_times, values)

    container.extend(new_elements)


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
        # Counter x should be in the middle between the farmost point on the L/R sides
        counter_x = self.ORIGIN[0] + self.WIDTH/2
        counter_y = self.max_y + 20
        font_size = 10

        # Create times and values lists
        times, counter_values = [], []

        for i in range(0, self.frame_count + 1):
            t = (i/self.frame_count)
            time = t * self.dur
            counter_value = "t=" + str(t).removeprefix("0")

            times.append(time)
            counter_values.append(counter_value)

        for i, value in enumerate(counter_values):
            new_text = draw.Text(value, font_size, counter_x, counter_y)

            new_text.add_key_frame(0, visibility="hidden", animation_args={
                "repeatCount": "indefinite"})
            new_text.add_key_frame(times[i], visibility="visible")
            if i != len(counter_values) - 1:
                new_text.add_key_frame(times[i+1], visibility="hidden")
            new_text.add_key_frame(self.dur, visibility="hidden")

            self.d.append(new_text)

    def generate_structure(self):
        def recursive_generate(b_points):
            order = len(b_points) - 1

            if order <= 1:
                return

            recursive_generate(b_points[:-1])
            recursive_generate(b_points[1:])

            # First Circle Array: b_points[:-1]
            # Second Circle Array: b_points[1:]

            times, d_vals = [], []
            first_circle_positions_x, second_circle_positions_x = [], []
            first_circle_positions_y, second_circle_positions_y = [], []

            for i in range(0, self.frame_count + 1):
                t = (i/self.frame_count)
                time = t * self.dur

                point1: complex = svgtools.bezier_point(b_points[:-1], t)
                point2: complex = svgtools.bezier_point(b_points[1:], t)

                d_val = "M%0.2lf,%0.2lf L%0.2lf,%0.2lf" % (
                    point1.real, point1.imag, point2.real, point2.imag)

                times.append(time)

                d_vals.append(d_val)

                first_circle_positions_x.append("%0.2lf" % (point1.real))
                first_circle_positions_y.append("%0.2lf" % (point1.imag))

                second_circle_positions_x.append("%0.2lf" % (point2.real))
                second_circle_positions_y.append("%0.2lf" % (point2.imag))

            line = draw.Path(
                "", fill="none", stroke=ORDER_COLOURS[order], stroke_opacity="60%", stroke_width=1, pathLength="10", stroke_linecap="round")
            line.add_attribute_key_sequence("d", times, d_vals, animation_args={
                "repeatCount": "indefinite"})

            first_circle = draw.Circle(
                0, 0, 3, fill="none", stroke=ORDER_COLOURS[order], stroke_width=0.5)
            first_circle.add_attribute_key_sequence("cx", times, first_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            first_circle.add_attribute_key_sequence("cy", times, first_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            second_circle = draw.Circle(
                0, 0, 3, fill="none", stroke=ORDER_COLOURS[order], stroke_width=0.5)
            second_circle.add_attribute_key_sequence("cx", times, second_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            second_circle.add_attribute_key_sequence("cy", times, second_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            self.d.append(first_circle)
            self.d.append(second_circle)
            self.d.append(line)

        recursive_generate(self.bpoints)

    def generate_red_bezier(self):
        bezier_path = path_from_polybezier(self.bpoints, self.resolution)

        times, dOffset = [], []
        circle_positions_x, circle_positions_y = [], []

        for i in range(0, self.frame_count + 1):
            t = (i/self.frame_count)
            time = t * self.dur

            times.append(time)

            point: complex = svgtools.bezier_point(self.bpoints, t)

            T = bezier_path.t2T(
                svgtools.closest_point_in_path(point, bezier_path)[2], t)

            percent_line_draw = 100 - \
                (100 * ((bezier_path.length(0, T) / bezier_path.length(0, 1))))

            if t != 0:
                dOffset.append("%0.2lf" % (percent_line_draw))
            else:
                dOffset.append("100.00")

            circle_positions_x.append("%0.2lf" % (point.real))
            circle_positions_y.append("%0.2lf" % (point.imag))

        svg_path = draw.Path(path_to_rounded_d(bezier_path), stroke="red",
                             stroke_width=2, fill="none", stroke_dasharray="100", stroke_dashoffset="100", pathLength="100", stroke_linecap="round")

        svg_path.add_attribute_key_sequence("stroke-dashoffset", times, dOffset, animation_args={
            "repeatCount": "indefinite"})

        circle = draw.Circle(0, 0, 2.5, fill="black")
        circle.add_attribute_key_sequence("cx", times, circle_positions_x, animation_args={
            "repeatCount": "indefinite"})
        circle.add_attribute_key_sequence("cy", times, circle_positions_y, animation_args={
            "repeatCount": "indefinite"})

        self.d.append(svg_path)
        self.d.append(circle)

    def calculate_windowsize(self):
        self.WIDTH: float = 0
        self.HEIGHT: float = 0
        self.ORIGIN: Tuple[float, float] = (0, 0)

        self.min_x, self.min_y = None, None
        self.max_x, self.max_y = None, None

        for bpoint in self.bpoints:
            if self.min_x == None or float(bpoint.real) < self.min_x:
                self.min_x = float(bpoint.real)
            if self.min_y == None or float(bpoint.imag) < self.min_y:
                self.min_y = float(bpoint.imag)
            if self.max_x == None or float(bpoint.real) > self.max_x:
                self.max_x = float(bpoint.real)
            if self.max_y == None or float(bpoint.imag) > self.max_y:
                self.max_y = float(bpoint.imag)

        self.ORIGIN = (self.min_x - 50, self.min_y - 50)
        self.WIDTH = abs(self.max_x - self.min_x) + 100
        self.HEIGHT = abs(self.max_y - self.min_y) + 100


if __name__ == "__main__":
    b1_bpoints = [280+20j,
                  380+100j]
    b2_bpoints = [200+100j,
                  280+20j,
                  320+100j]
    b3_bpoints = [200+100j,
                  180+20j,
                  280+20j,
                  320+100j]
    b4_bpoints = [200+100j,
                  180+20j,
                  280+20j,
                  320+100j,
                  360+40j]

    BezierAnimation("Bézier 1 big.svg", 6.0, b1_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 2 big.svg", 10.0, b2_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 3 big.svg", 10.0, b3_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 4 big.svg", 10.0, b4_bpoints,
                    resolution=1000, frame_count=100)
