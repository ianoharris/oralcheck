"""
Mouth Notes, math lane prototype (22 Nov 2026): what happens to mouth-cancer
risk after you quit smoking. 3Blue1Brown-style motion (Manim) on the house paper.

Run by anim.py with the narration's timing (env MN_PLAN = plan json path):
    MN_PLAN=plan.json manim -r 1080,1000 --fps 30 manim/quit.py Quit

Source: CDC, Benefits of Quitting Smoking: "5 to 10 years: added risk of cancers
of the mouth, throat, and voice box drops by half"; "20 years: risk of cancers of
the mouth, throat, and voice box drops to close to that of someone who does not
smoke." Shown: the extra risk smoking adds, 100% at quitting, a half-way band from
5 to 10 years (the source gives a range, so the curve passes through a band, not a
point), close to zero by 20. The curve's shape between those points is drawn
smooth and is illustrative; the on-screen note says so.
"""
import json, os
from manim import *

PAPER, INK, TEAL, CORAL, MUTED = "#f5f3f0", "#15201f", "#0d7377", "#e8634a", "#8a9796"
config.background_color = PAPER
plan = json.load(open(os.environ["MN_PLAN"]))
T = {s["key"]: s["t0"] for s in plan["shots"]}
TOTAL = plan["total"]
SERIF = "DM Serif Display"


class Quit(Scene):
    def at(self, t):
        """wait until scene time t (seconds from the start)."""
        dt = t - self.renderer.time
        if dt > 0.02:
            self.wait(dt)

    def construct(self):
        ax = Axes(x_range=[0, 20, 5], y_range=[0, 1.05, 0.5], x_length=7.4, y_length=5.6,
                  axis_config={"color": MUTED, "stroke_width": 3, "include_ticks": True},
                  tips=False).shift(DOWN * 0.1 + RIGHT * 0.35)
        xl = VGroup(*[Text(f"{v}", font="Source Sans 3", color=MUTED, font_size=26).next_to(ax.c2p(v, 0), DOWN, buff=0.18) for v in (0, 5, 10, 15, 20)])
        xt = Text("years after quitting", font="Source Sans 3", color=MUTED, font_size=26).next_to(ax.x_axis, DOWN, buff=0.7)
        yt = Text("extra risk from smoking", font="Source Sans 3", color=MUTED, font_size=26).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)

        # frame 0: a tall bar, the extra risk on the day you quit, already growing
        bar = Rectangle(width=1.1, height=5.0, fill_color=CORAL, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(0.9, 0.5))
        lab0 = Text("100%", font=SERIF, color=CORAL, font_size=64).next_to(bar, UP, buff=0.2)   # placed against the full-height bar
        bar.stretch(0.55, 1, about_edge=DOWN)
        self.add(bar)
        self.play(bar.animate.stretch(1 / 0.55, 1, about_edge=DOWN), FadeIn(lab0, shift=UP * 0.2), run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.at(T["axes"] - 0.1)

        # the bar becomes the curve's first point: Transform, the 3Blue1Brown move
        self.play(Create(ax), FadeIn(xl), FadeIn(xt), FadeIn(yt), run_time=1.0)
        dot = Dot(ax.c2p(0, 1.0), radius=0.13, color=CORAL)
        self.play(Transform(bar, dot), lab0.animate.next_to(ax.c2p(0, 1.0), UR, buff=0.15).scale(0.7), run_time=1.0)

        # the half-way band, 5 to 10 years, and the curve through it
        f = lambda x: 1.0 / (1.0 + (x / 7.0) ** 2.2)    # illustrative shape: 1 at 0, 0.5 at 7 (inside 5 to 10), near 0.12 by 20
        self.at(T["half"] - 0.1)
        band = Rectangle(width=ax.c2p(10, 0)[0] - ax.c2p(5, 0)[0], height=ax.c2p(0, 1.05)[1] - ax.c2p(0, 0)[1],
                         fill_color=TEAL, fill_opacity=0.12, stroke_width=0).move_to(ax.c2p(7.5, 0.525))
        half_line = DashedLine(ax.c2p(0, 0.5), ax.c2p(20, 0.5), color=TEAL, stroke_width=3, dash_length=0.12)
        half_lab = Text("half", font=SERIF, color=TEAL, font_size=48).next_to(ax.c2p(20, 0.5), UP, buff=0.12).shift(LEFT * 0.4)
        curve = ax.plot(f, x_range=[0, 10], color=TEAL, stroke_width=7)
        tracker = ValueTracker(0)
        rider = always_redraw(lambda: Dot(ax.c2p(tracker.get_value(), f(tracker.get_value())), radius=0.13, color=CORAL))
        self.remove(bar); self.add(rider)
        self.play(FadeIn(band), Create(half_line), FadeIn(half_lab), run_time=0.8)
        self.play(Create(curve), tracker.animate.set_value(10), run_time=max(1.5, T["twenty"] - self.renderer.time - 0.4), rate_func=rate_functions.ease_in_out_sine)
        self.remove(lab0)   # no running percentage: only the CDC's own points are labelled

        # to twenty years: close to someone who never smoked
        self.at(T["twenty"])
        curve2 = ax.plot(f, x_range=[10, 20], color=TEAL, stroke_width=7)
        never = DashedLine(ax.c2p(0, 0.0), ax.c2p(20, 0.0), color=INK, stroke_width=3)
        never_lab = Text("never smoked", font="Source Sans 3", weight=BOLD, color=INK, font_size=30).next_to(ax.c2p(17, 0), UP, buff=0.15)
        self.play(Create(curve2), tracker.animate.set_value(20), FadeIn(never_lab), run_time=2.6, rate_func=rate_functions.ease_in_out_sine)
        self.play(Indicate(never_lab, color=TEAL), run_time=1.0)
        note = Text("Points from CDC; the curve's shape between them is illustrative.", font="Source Sans 3", color=MUTED, font_size=22).to_edge(UP, buff=0.25)
        self.play(FadeIn(note), run_time=0.5)

        # never too late: the whole curve glows once, then holds and breathes to the end
        self.at(T["never"])
        self.play(curve.animate.set_stroke(width=11), curve2.animate.set_stroke(width=11), run_time=0.6, rate_func=there_and_back)
        self.at(TOTAL - 0.05)
