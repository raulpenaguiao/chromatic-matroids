"use strict";

class GraphEditor {
  constructor(canvas) {
    this.canvas  = canvas;
    this.ctx     = canvas.getContext("2d");
    this.vertices = [];   // {id, x, y}
    this.edges    = [];   // {id, u, v}
    this._nextVid = 1;
    this._nextEid = 1;
    this._drag    = null; // {srcId, curX, curY} while drawing an edge
    this._hoverEdge = null;

    this._resize();
    window.addEventListener("resize", () => this._resize());

    canvas.addEventListener("mousedown",  e => this._onDown(e));
    canvas.addEventListener("mousemove",  e => this._onMove(e));
    canvas.addEventListener("mouseup",    e => this._onUp(e));
    canvas.addEventListener("contextmenu",e => { e.preventDefault(); this._onRightClick(e); });
  }

  // ── public ──────────────────────────────────────────────────────────────

  clear() {
    this.vertices = []; this.edges = [];
    this._nextVid = 1; this._nextEid = 1;
    this._drag = null; this._hoverEdge = null;
    this._draw();
  }

  getData() {
    return {
      vertices: this.vertices.map(v => v.id),
      edges:    this.edges.map(e => [e.u, e.v]),
    };
  }

  // ── internal ─────────────────────────────────────────────────────────────

  _resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width  = rect.width  || 420;
    this.canvas.height = rect.height || 300;
    this._draw();
  }

  _pos(e) {
    const r = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width  / r.width;
    const scaleY = this.canvas.height / r.height;
    return { x: (e.clientX - r.left) * scaleX, y: (e.clientY - r.top) * scaleY };
  }

  _vertexAt(x, y, radius = 16) {
    return this.vertices.find(v => Math.hypot(v.x - x, v.y - y) <= radius) || null;
  }

  _edgeAt(x, y, tol = 7) {
    for (const e of this.edges) {
      const a = this.vertices.find(v => v.id === e.u);
      const b = this.vertices.find(v => v.id === e.v);
      if (!a || !b) continue;
      const d = this._ptSegDist(x, y, a.x, a.y, b.x, b.y);
      if (d <= tol) return e;
    }
    return null;
  }

  _ptSegDist(px, py, ax, ay, bx, by) {
    const dx = bx - ax, dy = by - ay;
    const lenSq = dx * dx + dy * dy;
    if (lenSq === 0) return Math.hypot(px - ax, py - ay);
    const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / lenSq));
    return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
  }

  _onDown(e) {
    if (e.button !== 0) return;
    const { x, y } = this._pos(e);
    const v = this._vertexAt(x, y);
    if (v) {
      this._drag = { srcId: v.id, curX: x, curY: y };
    }
  }

  _onMove(e) {
    const { x, y } = this._pos(e);
    if (this._drag) {
      this._drag.curX = x; this._drag.curY = y;
      this._hoverEdge = null;
    } else {
      this._hoverEdge = this._edgeAt(x, y);
    }
    this._draw();
  }

  _onUp(e) {
    if (e.button !== 0) return;
    const { x, y } = this._pos(e);
    if (this._drag) {
      const src = this._drag.srcId;
      const tgt = this._vertexAt(x, y);
      if (tgt && tgt.id !== src) {
        // add edge (avoid duplicates)
        const exists = this.edges.some(
          ed => (ed.u === src && ed.v === tgt.id) || (ed.u === tgt.id && ed.v === src));
        if (!exists) {
          this.edges.push({ id: this._nextEid++, u: src, v: tgt.id });
        }
      }
      this._drag = null;
      this._draw();
    } else {
      // no drag started: click on empty space → add vertex
      if (!this._vertexAt(x, y)) {
        const edge = this._edgeAt(x, y);
        if (!edge) {
          this.vertices.push({ id: this._nextVid++, x, y });
          this._draw();
        }
      }
    }
  }

  _onRightClick(e) {
    const { x, y } = this._pos(e);
    const v = this._vertexAt(x, y);
    if (v) {
      this.vertices = this.vertices.filter(w => w.id !== v.id);
      this.edges    = this.edges.filter(ed => ed.u !== v.id && ed.v !== v.id);
      this._draw(); return;
    }
    const edge = this._edgeAt(x, y);
    if (edge) {
      this.edges = this.edges.filter(ed => ed.id !== edge.id);
      this._draw();
    }
  }

  _draw() {
    const ctx = this.ctx;
    const W = this.canvas.width, H = this.canvas.height;
    ctx.clearRect(0, 0, W, H);

    // edges
    for (const e of this.edges) {
      const a = this.vertices.find(v => v.id === e.u);
      const b = this.vertices.find(v => v.id === e.v);
      if (!a || !b) continue;
      const hover = this._hoverEdge && this._hoverEdge.id === e.id;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = hover ? "#dc2626" : "#6b7280";
      ctx.lineWidth   = hover ? 2.5 : 1.5;
      ctx.stroke();
      // edge index label at midpoint
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      ctx.fillStyle = hover ? "#dc2626" : "#374151";
      ctx.font = "11px system-ui";
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(String(e.id), mx, my - 7);
    }

    // rubber-band edge while dragging
    if (this._drag) {
      const src = this.vertices.find(v => v.id === this._drag.srcId);
      if (src) {
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(this._drag.curX, this._drag.curY);
        ctx.strokeStyle = "#93c5fd";
        ctx.lineWidth = 1.5;
        ctx.setLineDash([5, 3]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // vertices
    for (const v of this.vertices) {
      ctx.beginPath();
      ctx.arc(v.x, v.y, 14, 0, 2 * Math.PI);
      ctx.fillStyle   = "#eff6ff";
      ctx.strokeStyle = "#2563eb";
      ctx.lineWidth   = 2;
      ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#1e40af";
      ctx.font = "bold 12px system-ui";
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(String(v.id), v.x, v.y);
    }
  }
}
