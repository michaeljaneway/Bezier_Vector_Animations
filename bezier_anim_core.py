import drawsvg as draw
import svgpathtools as svgtools
from bezier_anim_tools import path_to_rounded_d, path_from_polybezier
from typing import *
from random import randint


class BezierAnimation:
    def __init__(self, filename: str, dur: float, bpoints: List[complex], resolution: int = 10, frame_count: int = 100, bg: str = "white", order_colours: List[str] = []) -> None:
        if len(order_colours) == 0:
            self.ORDER_COLOURS = {
                7: "brown",
                6: "magenta",
                5: "#008B8B",
                4: "#D16587",
                3: "blue",
                2: "green"
            }
        else:
            self.ORDER_COLOURS = order_colours

        self.bpoints: List[complex] = bpoints
        self.filename: str = filename
        self.dur: float = dur
        self.resolution: int = resolution
        self.frame_count: int = frame_count

        self.calculate_drawingsize()

        self.d: draw.Drawing = draw.Drawing(
            self.WIDTH, self.HEIGHT, self.ORIGIN)

        # Background
        self.d.append(draw.Rectangle(
            self.ORIGIN[0], self.ORIGIN[1], self.WIDTH, self.HEIGHT, fill=bg))

        self.render()

    def render(self):
        self.generate_greys()
        self.generate_points()

        self.generate_structure()

        self.generate_main_bezier()
        self.generate_counter()

        self.d.save_svg(self.filename)

    def generate_greys(self):
        """
        Generates grey lines between bpoints
        """
        for point_i, bpoint in enumerate(self.bpoints):
            if not point_i >= len(self.bpoints) - 1:
                grey_line = draw.Line(
                    bpoint.real, bpoint.imag, self.bpoints[point_i + 1].real, self.bpoints[point_i + 1].imag, stroke="#D3D3D3", stroke_width=4, pathLength="10", stroke_linecap="round")
                self.d.append(grey_line)

    def generate_points(self):
        """
        Generates circles and labels (P0, P1, etc..) for bpoints  
        """
        for point_i, bpoint in enumerate(self.bpoints):
            p_circle = draw.Circle(bpoint.real, bpoint.imag, 5, stroke="black",
                                   stroke_width=2, fill="none")
            p_text = draw.Text("P", 15, x=bpoint.real + 10, y=bpoint.imag)
            p_text.append_line(
                "%d" % (point_i), baseline_shift="sub", font_size="10")

            self.d.append(p_circle)
            self.d.append(p_text)

    def generate_counter(self):
        """
        Generates the 't' counter using key frames for visibility
        """
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
        """
        Generates an animated structure of the background 'builder' circles and lines for the main bezier
        """
        def recursive_generate(b_points):
            order = len(b_points) - 1

            # Base case: Order <= 1 so nothing needs to be generated
            if order <= 1:
                return

            # Call recursive function
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
                "", fill="none", stroke=self.ORDER_COLOURS[order], stroke_opacity="60%", stroke_width=1, pathLength="10", stroke_linecap="round")
            line.add_attribute_key_sequence("d", times, d_vals, animation_args={
                "repeatCount": "indefinite"})

            first_circle = draw.Circle(
                0, 0, 3, fill="none", stroke=self.ORDER_COLOURS[order], stroke_width=0.5)
            first_circle.add_attribute_key_sequence("cx", times, first_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            first_circle.add_attribute_key_sequence("cy", times, first_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            second_circle = draw.Circle(
                0, 0, 3, fill="none", stroke=self.ORDER_COLOURS[order], stroke_width=0.5)
            second_circle.add_attribute_key_sequence("cx", times, second_circle_positions_x, animation_args={
                "repeatCount": "indefinite"})
            second_circle.add_attribute_key_sequence("cy", times, second_circle_positions_y, animation_args={
                "repeatCount": "indefinite"})

            self.d.append(first_circle)
            self.d.append(second_circle)
            self.d.append(line)

        recursive_generate(self.bpoints)

    def generate_main_bezier(self):
        """
        Generates the main Bezier curve using the given bpoints
        """
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

    def calculate_drawingsize(self):
        """
        Calculates the size of the drawing based on the min and max x and y
        values in the bpoints
        """
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
    b5_bpoints = [0+200j,
                  60+10j,
                  110+160j,
                  170+70j,
                  230+110j,
                  170+160j]

    BezierAnimation("Bézier 1 big.svg", 6.0, b1_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 2 big.svg", 10.0, b2_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 3 big.svg", 10.0, b3_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 4 big.svg", 10.0, b4_bpoints,
                    resolution=1000, frame_count=100)
    BezierAnimation("Bézier 5 big.svg", 10.0, b5_bpoints,
                    resolution=1000, frame_count=100)
