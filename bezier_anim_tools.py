import drawsvg as draw
import svgpathtools as svgtools
from typing import *
from random import randint


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