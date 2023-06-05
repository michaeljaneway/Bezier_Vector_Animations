![svgbezier logo](https://github.com/michaeljaneway/Wiki-Anims/blob/master/assets/B%C3%A9zier%205%20big.svg)

# Animated SVG Bezier Curve Generator

A small library designed to help vectorize animated .gif files located on this Wikipedia page
https://en.wikipedia.org/wiki/B%C3%A9zier_curve

# Examples:
![svgbezier logo](https://github.com/michaeljaneway/Wiki-Anims/blob/master/assets/B%C3%A9zier%201%20big.svg)

```python
b1_bpoints = [280+20j,
              380+100j]

BezierAnimation("Bézier 1 big.svg", 6.0, b1_bpoints,
                    resolution=1000, frame_count=100)
```

![svgbezier logo](https://github.com/michaeljaneway/Wiki-Anims/blob/master/assets/B%C3%A9zier%202%20big.svg)
```python
b2_bpoints = [200+100j,
              280+20j,
              320+100j]

BezierAnimation("Bézier 2 big.svg", 10.0, b2_bpoints,
                    resolution=1000, frame_count=100)

```
![svgbezier logo](https://github.com/michaeljaneway/Wiki-Anims/blob/master/assets/B%C3%A9zier%203%20big.svg)
```python
b3_bpoints = [200+100j,
              180+20j,
              280+20j,
              320+100j]

BezierAnimation("Bézier 3 big.svg", 10.0, b3_bpoints,
                    resolution=1000, frame_count=100)

```
![svgbezier logo](https://github.com/michaeljaneway/Wiki-Anims/blob/master/assets/B%C3%A9zier%204%20big.svg)
```python
b4_bpoints = [200+100j,
              180+20j,
              280+20j,
              320+100j,
              360+40j]

BezierAnimation("Bézier 4 big.svg", 10.0, b4_bpoints,
                    resolution=1000, frame_count=100)

```

# Dependencies
- svgdraw (https://github.com/cduck/drawsvg)
- svgpathtools (https://github.com/mathandy/svgpathtools)
