
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from hockey_rink import IIHFRink


def create_rink_plot(players, shot_x, shot_y):

    rink = IIHFRink()

    fig, ax = plt.subplots(figsize=(11, 5))

    rink.draw(ax=ax)

    print("X-Achse:", ax.get_xlim())
    print("Y-Achse:", ax.get_ylim())
    print("Linien auf dem Spielfeld:")
    for line in ax.lines:
     print("X:", line.get_xdata(), "Y:", line.get_ydata())

    scale = 100 / 30

    def format_meters(value, pos):
        meters = value / scale

        if abs(meters) < 0.5:
            meters = 0

        return f"{meters:.0f}"

    ax.xaxis.set_major_formatter(FuncFormatter(format_meters))
    ax.yaxis.set_major_formatter(FuncFormatter(format_meters))

    teams = list(dict.fromkeys(
        player["team"] for player in players
        if player["team"] is not None
    ))

    colors = ["blue", "gold"]

    team_colors = {
        team: colors[index % len(colors)]
        for index, team in enumerate(teams)
    }

    for player in players:

        rink_x = player["x"] * scale
        rink_y = player["y"] * scale

        color = team_colors.get(player["team"], "gray")

        ax.scatter(
            rink_x,
            rink_y,
            color=color,
            s=40,
            edgecolors="white",
            linewidths=1.5,
            zorder=5
        )

        ax.annotate(
            f'{player["jersey"]}',
            xy=(rink_x, rink_y),
            color="white",
            fontsize=6,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=6
        )

    shooter_x = shot_x * scale
    shooter_y = shot_y * scale

    ax.scatter(
        shooter_x,
        shooter_y,
        facecolors="none",
        edgecolors="red",
        s=60,
        linewidths=2,
        label="Shooter",
        zorder=7
    )

    goal_x = (26 if shot_x >= 0 else -26) * scale
    goal_y = 0

    ax.plot(
        [shooter_x, goal_x],
        [shooter_y, goal_y],
        linestyle="--",
        color="red",
        linewidth=2,
        label="Shot path",
        zorder=4
    )

    for team, color in team_colors.items():

        ax.scatter(
            [],
            [],
            color=color,
            s=30,
            label=f"{team}"
        )

    ax.set_aspect("equal")
    ax.legend()

    return fig
