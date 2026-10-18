"""Render a 30-second video showing geometrically why (a+b)^2 = a^2 + 2ab + b^2.

Usage: python3 make_video.py  ->  writes binomial_square.mp4
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Rectangle

FPS = 30
DURATION = 30
A, B = 3.0, 2.0
S = A + B

BG = "#0f172a"
FG = "#f8fafc"
MUTED = "#94a3b8"
C_A2 = "#3b82f6"
C_B2 = "#f59e0b"
C_AB = "#10b981"

fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def prog(t, start, length=1.0):
    return ease((t - start) / length)


# Square sits on the left; text panel on the right.
OX, OY = 1.0, 1.0


def region(x, y, w, h, color, alpha, label, label_alpha):
    if alpha > 0:
        ax.add_patch(Rectangle((OX + x, OY + y), w, h, facecolor=color,
                               alpha=0.85 * alpha, edgecolor=FG, lw=2))
    if label_alpha > 0:
        ax.text(OX + x + w / 2, OY + y + h / 2, label, color=FG, alpha=label_alpha,
                ha="center", va="center", fontsize=30, fontweight="bold")


def text(x, y, s, alpha, size=28, color=FG, **kw):
    if alpha > 0:
        ax.text(x, y, s, color=color, alpha=alpha, fontsize=size,
                ha=kw.pop("ha", "left"), va="center", **kw)


def draw(frame):
    t = frame / FPS
    ax.clear()
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_facecolor(BG)
    ax.axis("off")

    # 0-4s: title
    title_in = prog(t, 0.2, 1.0)
    title_out = 1 - prog(t, 3.2, 0.8)
    text(8, 5.2, r"Why is $(a+b)^2 = a^2 + 2ab + b^2$ ?", title_in * title_out,
         size=40, ha="center")
    text(8, 3.9, "Let's see it with a picture.", title_in * title_out,
         size=24, color=MUTED, ha="center")
    if t < 4:
        return

    # 4-8s: big square of side a+b
    sq = prog(t, 4, 1.5)
    ax.add_patch(Rectangle((OX, OY), S * sq, S * sq, fill=False, edgecolor=FG, lw=3))
    lab = prog(t, 5.5, 1)
    # side labels: a then b along bottom and left edges
    text(OX + A / 2, OY - 0.4, r"$a$", lab, size=30, ha="center", color=C_A2)
    text(OX + A + B / 2, OY - 0.4, r"$b$", lab, size=30, ha="center", color=C_B2)
    text(OX - 0.4, OY + S - A / 2, r"$a$", lab, size=30, ha="center", color=C_A2)
    text(OX - 0.4, OY + B / 2, r"$b$", lab, size=30, ha="center", color=C_B2)
    text(9, 7.6, "A square with side  $a + b$", prog(t, 4.5, 1), size=28)
    text(9, 6.6, r"Area $= (a+b)^2$", prog(t, 6, 1), size=30)

    # 8-10s: cut lines
    cut = prog(t, 8, 1.5)
    if cut > 0:
        ax.plot([OX + A, OX + A], [OY + S, OY + S - S * cut], color=FG, lw=2, ls="--")
        ax.plot([OX, OX + S * cut], [OY + B, OY + B], color=FG, lw=2, ls="--")
    text(9, 5.6, "Cut it into 4 pieces:", prog(t, 8.5, 1), size=26, color=MUTED)

    # 10-13s: a^2 (top-left), 13-16s: b^2 (bottom-right), 16-21s: two ab
    region(0, B, A, A, C_A2, prog(t, 10.5, 1), r"$a^2$", prog(t, 11, 1))
    text(9.3, 4.7, r"$a \times a = a^2$", prog(t, 11, 1), size=28, color=C_A2)

    region(A, 0, B, B, C_B2, prog(t, 13.5, 1), r"$b^2$", prog(t, 14, 1))
    text(9.3, 3.9, r"$b \times b = b^2$", prog(t, 14, 1), size=28, color=C_B2)

    region(A, B, B, A, C_AB, prog(t, 16.5, 1), r"$ab$", prog(t, 17, 1))
    region(0, 0, A, B, C_AB, prog(t, 18.5, 1), r"$ab$", prog(t, 19, 1))
    text(9.3, 3.1, r"$a \times b = ab$  (twice!)", prog(t, 17.5, 1), size=28, color=C_AB)

    # 21-30s: add the pieces up
    text(9, 2.1, r"$(a+b)^2 = a^2 + ab + ab + b^2$", prog(t, 21.5, 1.2), size=28)
    final = prog(t, 24.5, 1.2)
    text(9, 1.2, r"$(a+b)^2 = a^2 + 2ab + b^2$", final, size=31, color="#fde047",
         fontweight="bold")
    if final > 0:
        ax.add_patch(Rectangle((8.75, 0.7), 7.1, 1.0, fill=False, edgecolor="#fde047",
                               lw=2.5, alpha=prog(t, 26, 1)))
    text(OX + S / 2, 8.4, r"Example: $a=3,\ b=2 \Rightarrow 25 = 9 + 12 + 4$",
         prog(t, 27, 1), size=18, color=MUTED, ha="center")


anim = FuncAnimation(fig, draw, frames=FPS * DURATION)
anim.save("binomial_square.mp4", writer=FFMpegWriter(fps=FPS, bitrate=4000,
          extra_args=["-pix_fmt", "yuv420p"]), savefig_kwargs={"facecolor": BG})
print("wrote binomial_square.mp4")
