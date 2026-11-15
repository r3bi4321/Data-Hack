"""
movePlayer.py

Zeichnet das Eisfeld und macht die Spieler-Bubbles per Drag & Drop
verschiebbar. Die neuen Positionen werden an Streamlit zurückgegeben.

Verwendung in app.py:

    from movePlayer import draw_movable_rink

    players = draw_movable_rink(players, shot_x, shot_y,
      key=f"rink_{selected_index}")
"""

import base64
import io
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components
from hockey_rink import IIHFRink


SCALE = 100 / 30 
TEAM_COLORS = ["blue", "white"]

_FRONTEND_DIR = Path(__file__).resolve().parent / "movePlayer_frontend"


_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; font-family: sans-serif; }
  #wrap { width: 100%; }
  svg { width: 100%; display: block; touch-action: none; }
  .player { cursor: grab; }
  .player.dragging { cursor: grabbing; }
  #legend { font-size: 13px; padding: 4px 0; display: flex; gap: 14px; }
  .dot { display: inline-block; width: 11px; height: 11px;
         border-radius: 50%; margin-right: 4px; border: 1px solid #888; }
</style>
</head>
<body>
<div id="wrap">
  <svg id="svg"></svg>
  <div id="legend"></div>
</div>

<script>
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("svg");
let args = null;
let state = [];   
let sig = null;   
let shotLine = null;

function send(type, extra) {
  window.parent.postMessage(
    Object.assign({isStreamlitMessage: true, type: type}, extra), "*");
}
function setHeight() {
  send("streamlit:setFrameHeight", {height: document.body.scrollHeight + 4});
}


function toPx(x, y) {
  const b = args.box;
  return [
    b.x0 + (x - args.xlim[0]) / (args.xlim[1] - args.xlim[0]) * b.w,
    b.y0 + (args.ylim[1] - y) / (args.ylim[1] - args.ylim[0]) * b.h
  ];
}
function toRink(px, py) {
  const b = args.box;
  px = Math.min(Math.max(px, b.x0), b.x0 + b.w);
  py = Math.min(Math.max(py, b.y0), b.y0 + b.h);
  return [
    args.xlim[0] + (px - b.x0) / b.w * (args.xlim[1] - args.xlim[0]),
    args.ylim[1] - (py - b.y0) / b.h * (args.ylim[1] - args.ylim[0])
  ];
}

function el(name, attrs) {
  const e = document.createElementNS(NS, name);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  return e;
}

const colorCtx = document.createElement("canvas").getContext("2d");
function isLight(color) {
  colorCtx.fillStyle = "#000";
  colorCtx.fillStyle = color;
  const hex = colorCtx.fillStyle;          
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.6;
}

function render() {
  svg.setAttribute("viewBox", "0 0 " + args.width + " " + args.height);
  svg.innerHTML = "";

  const img = el("image", {href: "data:image/png;base64," + args.image,
                           x: 0, y: 0, width: args.width, height: args.height});
  svg.appendChild(img);

  shotLine = el("line", {x1: 0, y1: 0, x2: 0, y2: 0, stroke: "red",
                         "stroke-width": 3, "stroke-dasharray": "10 6"});
  svg.appendChild(shotLine);

  state.forEach((p, i) => {
    const [px, py] = toPx(p.x, p.y);
    const g = el("g", {class: "player"});
    const light = isLight(p.color);
    g.appendChild(el("circle", {cx: px, cy: py, r: 13, fill: p.color,
                                stroke: light ? "#333" : "white",
                                "stroke-width": 2.5}));
    const t = el("text", {x: px, y: py, "text-anchor": "middle",
                          "dominant-baseline": "central",
                          fill: light ? "black" : "white",
                          "font-size": 13, "font-weight": "bold",
                          "pointer-events": "none"});
    t.textContent = p.jersey;
    g.appendChild(t);
    g.setAttribute("data-i", i);
    svg.appendChild(g);
  });

  const legend = document.getElementById("legend");
  legend.innerHTML = "";
  args.teams.forEach(t => {
    legend.innerHTML += '<span><span class="dot" style="background:' + t.color +
                        '"></span>' + t.name + '</span>';
  });

  updateShot();
  setHeight();
}

function shooterPos() {
  const i = args.shooterIndex;
  if (i !== null && i >= 0 && state[i]) return [state[i].x, state[i].y];
  return args.shooter;
}

function updateShot() {
  const [shx, shy] = shooterPos();
  const [sx, sy] = toPx(shx, shy);
  const [gx, gy] = toPx(args.goal[0], args.goal[1]);
  shotLine.setAttribute("x1", sx); shotLine.setAttribute("y1", sy);
  shotLine.setAttribute("x2", gx); shotLine.setAttribute("y2", gy);
}

let dragging = null;

function playerEl(i) {
  return svg.querySelector('.player[data-i="' + i + '"]');
}

svg.addEventListener("pointerdown", ev => {
  const g = ev.target.closest(".player");
  if (!g) return;
  dragging = parseInt(g.getAttribute("data-i"));
  svg.setPointerCapture(ev.pointerId);
  g.classList.add("dragging");
  ev.preventDefault();
});

svg.addEventListener("pointermove", ev => {
  if (dragging === null) return;
  const pt = svg.createSVGPoint();
  pt.x = ev.clientX; pt.y = ev.clientY;
  const loc = pt.matrixTransform(svg.getScreenCTM().inverse());
  const [rx, ry] = toRink(loc.x, loc.y);
  state[dragging].x = rx; state[dragging].y = ry;
  const [px, py] = toPx(rx, ry);
  const g = playerEl(dragging);
  g.querySelector("circle").setAttribute("cx", px);
  g.querySelector("circle").setAttribute("cy", py);
  g.querySelector("text").setAttribute("x", px);
  g.querySelector("text").setAttribute("y", py);
  updateShot();
});

function endDrag(ev) {
  if (dragging === null) return;
  const g = playerEl(dragging);
  if (g) g.classList.remove("dragging");
  dragging = null;
  send("streamlit:setComponentValue",
       {value: state.map(p => ({x: p.x, y: p.y})), dataType: "json"});
}
svg.addEventListener("pointerup", endDrag);
svg.addEventListener("pointercancel", endDrag);

window.addEventListener("message", ev => {
  if (ev.data.type !== "streamlit:render") return;
  args = ev.data.args;
  const newSig = JSON.stringify(args.players) + args.image.length;
  if (newSig !== sig) {
    sig = newSig;
    state = args.players.map(p => Object.assign({}, p));
  }
  render();
});
window.addEventListener("resize", setHeight);

send("streamlit:componentReady", {apiVersion: 1});
</script>
</body>
</html>
"""


def _ensure_frontend():
    """Legt den Frontend-Ordner der Komponente an (einmalig)."""
    _FRONTEND_DIR.mkdir(exist_ok=True)
    index = _FRONTEND_DIR / "index.html"
    if not index.exists() or index.read_text(encoding="utf-8") != _HTML:
        index.write_text(_HTML, encoding="utf-8")


_ensure_frontend()

_component = components.declare_component(
    "movable_rink",
    path=str(_FRONTEND_DIR)
)

@st.cache_data
def _render_rink():
    """Rendert nur das leere Eisfeld als PNG und liefert die Achsen-Geometrie."""

    rink = IIHFRink()

    fig, ax = plt.subplots(figsize=(11, 5), dpi=100)
    rink.draw(ax=ax)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.canvas.draw()

    width, height = fig.canvas.get_width_height()
    bbox = ax.get_window_extent()

    info = {
        "width": width,
        "height": height,
        "box": {
            "x0": bbox.x0,
            "y0": height - bbox.y1,   
            "w": bbox.width,
            "h": bbox.height,
        },
        "xlim": list(ax.get_xlim()),
        "ylim": list(ax.get_ylim()),
    }

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    plt.close(fig)

    image = base64.b64encode(buffer.getvalue()).decode("ascii")

    return image, info

def draw_movable_rink(
    players, shot_x, shot_y, key="rink", shooter_index=None, goal_x=None
):
    """
    Zeigt das Eisfeld mit verschiebbaren Spielern.

    players: Liste von Dicts (id, jersey, team, x, y) in Daten-Koordinaten
    shooter_index: Index des Schützen in `players`. Rote Schusslinie und
                   Ring folgen diesem Spieler beim Verschieben.
    Rückgabe: dieselbe Liste, aber mit den vom Nutzer verschobenen x/y.
    """

    image, info = _render_rink()

    teams = list(dict.fromkeys(
        p["team"] for p in players if p["team"] is not None
    ))

    team_color = {
        team: TEAM_COLORS[i % len(TEAM_COLORS)]
        for i, team in enumerate(teams)
    }

    js_players = [
        {
            "jersey": str(p["jersey"]),
            "color": team_color.get(p["team"], "gray"),
            "x": p["x"] * SCALE,
            "y": p["y"] * SCALE,
        }
        for p in players
    ]

    if goal_x is None:
        goal_x = 26 if shot_x >= 0 else -26

    goal_x = goal_x * SCALE

    result = _component(
        image=image,
        width=info["width"],
        height=info["height"],
        box=info["box"],
        xlim=info["xlim"],
        ylim=info["ylim"],
        players=js_players,
        teams=[{"name": str(t), "color": team_color[t]} for t in teams],
        shooter=[shot_x * SCALE, shot_y * SCALE],
        goal=[goal_x, 0],
        shooterIndex=shooter_index,
        key=key,
        default=None,
    )

    if not result or len(result) != len(players):
        return players

    moved = []

    for player, new_pos in zip(players, result):
        updated = dict(player)
        updated["x"] = new_pos["x"] / SCALE
        updated["y"] = new_pos["y"] / SCALE
        moved.append(updated)

    return moved