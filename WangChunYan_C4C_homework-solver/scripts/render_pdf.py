#!/usr/bin/env python3
"""
Stage 5'：TeX-free PDF 渲染器（matplotlib）。

背景
----
Starter kit 的 PDF 编译依赖本机 LaTeX（pdflatex/xelatex）。C4C 要求「输出可提交
的 PDF」，但很多同学的机器没有装 TeX Live。本模块用 matplotlib 直接生成 PDF，
**无需任何 LaTeX 环境**，同时仍输出 homework.tex 供 Overleaf 做专业排版。

用法:
    python render_pdf.py solutions.json output.pdf --course "课程" --student "姓名" --title "标题"
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── 中文字体 ────────────────────────────────
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
    "PingFang SC", "Arial Unicode MS", "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

PAGE_W, PAGE_H = 8.27, 11.69          # A4 (inch)
ML, MR, MT, MB = 0.78, 0.78, 0.82, 0.78
CONTENT_W = PAGE_W - ML - MR


# ═══════════════════════════════════════════════
# LaTeX → 可读纯文本（供 PDF 正文/步骤显示）
# ═══════════════════════════════════════════════

def _matrix_ascii(content: str) -> str:
    """把矩阵内部内容转成 [[a, b], [c, d]] 形式。"""
    rows = []
    for row in content.split("\\\\"):
        cells = [c.strip() for c in row.split("&")]
        rows.append("[" + ", ".join(cells) + "]")
    return "[" + ", ".join(rows) + "]"


def latex_to_readable(s: str) -> str:
    """把含 LaTeX 的字符串转成可读的纯文本（近似，供 PDF 显示）。"""
    if not s:
        return s
    # 矩阵 → ASCII
    s = re.sub(
        r"\\begin\{[a-zA-Z]*matrix\}(.*?)\\end\{[a-zA-Z]*matrix\}",
        lambda m: _matrix_ascii(m.group(1)), s, flags=re.DOTALL)
    s = re.sub(r"\\begin\{cases\}(.*?)\\end\{cases\}",
               lambda m: m.group(1).replace("\\\\", "; "), s, flags=re.DOTALL)
    # 分数
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    # 上下标
    s = re.sub(r"\^\{([^{}]*)\}", r"^\1", s)
    s = re.sub(r"_\{([^{}]*)\}", r"_\1", s)
    # 常见命令
    s = s.replace(r"\det", "det").replace(r"\operatorname{rank}", "rank")
    s = s.replace(r"\lambda", "λ").replace(r"\varepsilon", "ε").replace(r"\delta", "δ")
    s = s.replace(r"\cosh", "cosh").replace(r"\sinh", "sinh").replace(r"\tanh", "tanh")
    s = s.replace(r"\ln", "ln").replace(r"\log", "log").replace(r"\exp", "exp")
    s = s.replace(r"\cdot", "·").replace(r"\times", "×").replace(r"\infty", "∞")
    s = s.replace(r"\qquad", "   ").replace(r"\quad", "  ").replace(r"\,", " ")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\text", "").replace(r"\mathrm", "")
    s = s.replace(r"\\", "  ")
    # 去掉美元符与剩余花括号
    s = s.replace("$$", "").replace("$", "")
    s = s.replace("{", "").replace("}", "")
    s = s.replace(r"\'", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _sanitize_mathtext(s: str) -> str:
    """把简单 LaTeX 表达式转成 matplotlib mathtext 能接受的字符串。"""
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\operatorname{rank}", r"\mathrm{rank}")
    s = s.replace(r"\det", r"\mathrm{det}")
    s = s.replace(r"\text", r"\mathrm")
    s = s.replace(r"\qquad", "  ").replace(r"\quad", "  ")
    s = s.replace(r"\,", " ").replace(r"\ ", " ")
    return s


# ═══════════════════════════════════════════════
# PDF 文档与流式排版
# ═══════════════════════════════════════════════

class PDFRenderer:
    def __init__(self, path: str, title: str, course: str, student: str, date_str: str):
        self.pdf = PdfPages(path)
        self.title = title
        self.course = course
        self.student = student
        self.date_str = date_str
        self.fig = None
        self.ax = None
        self.y = 0.0
        self.page_no = 0
        self._new_page()

    def _new_page(self):
        if self.fig is not None:
            self.pdf.savefig(self.fig)
            plt.close(self.fig)
        self.page_no += 1
        self.fig = plt.figure(figsize=(PAGE_W, PAGE_H))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis("off")
        self.ax.set_xlim(0, PAGE_W)
        self.ax.set_ylim(0, PAGE_H)
        self.y = PAGE_H - MT
        self._draw_header()
        self._draw_footer()

    def _draw_header(self):
        ax = self.ax
        ax.text(PAGE_W / 2, PAGE_H - 0.45, self.title,
                ha="center", va="center", fontsize=16, weight="bold")
        ax.text(PAGE_W / 2, PAGE_H - 0.72,
                f"{self.course}", ha="center", va="center", fontsize=11)
        ax.text(PAGE_W / 2, PAGE_H - 0.95,
                f"{self.student}　|　{self.date_str}", ha="center", va="center", fontsize=10)
        ax.plot([ML, PAGE_W - MR], [PAGE_H - 1.12, PAGE_H - 1.12],
                color="black", lw=0.8)

    def _draw_footer(self):
        self.ax.text(PAGE_W / 2, 0.35, f"— {self.page_no} —",
                     ha="center", va="center", fontsize=9, color="0.4")

    def _measure(self, s: str, fontsize: float, weight="normal") -> float:
        """返回字符串在图中的宽度（inch）。"""
        t = self.fig.text(0, 0, s, fontsize=fontsize, weight=weight)
        renderer = self.fig.canvas.get_renderer()
        bbox = t.get_window_extent(renderer=renderer)
        t.remove()
        return bbox.width / self.fig.dpi

    def _newline(self, leading=1.0, fontsize=11.0):
        self.y -= leading * fontsize / 72.0

    def _ensure_space(self, needed_inch: float):
        if self.y - needed_inch < MB:
            self._new_page()

    def text_line(self, s: str, fontsize=10.5, weight="normal", color="black",
                  x=None, ha="left", leading=1.35):
        """绘制一行文本，必要时换页。返回新的 y。"""
        s = str(s)
        x = ML if x is None else x
        self._ensure_space(fontsize / 72.0 * 1.5)
        self.ax.text(x, self.y, s, fontsize=fontsize, weight=weight,
                     color=color, ha=ha, va="top", wrap=False)
        self._newline(leading=leading, fontsize=fontsize)
        return self.y

    def wrapped_text(self, s: str, fontsize=10.5, leading=1.35, weight="normal"):
        """自动换行渲染一段文本。"""
        s = str(s)
        # 按视觉宽度贪婪换行
        para = s.split("\n")
        for line in para:
            line = line.strip()
            if not line:
                self._newline(leading=leading, fontsize=fontsize)
                continue
            words = self._wrap_greedy(line, fontsize, weight)
            for w in words:
                self.text_line(w, fontsize=fontsize, weight=weight, leading=leading)

    def _wrap_greedy(self, line: str, fontsize: float, weight: str):
        """按可用宽度贪婪分词换行（中文按字符，英文按词）。"""
        out = []
        # 先按字符切分
        tokens = list(line)
        cur = ""
        for ch in tokens:
            trial = cur + ch
            if self._measure(trial, fontsize, weight) > CONTENT_W and cur:
                out.append(cur)
                cur = ch
            else:
                cur = trial
        if cur:
            out.append(cur)
        return out

    def hrule(self, color="0.75", lw=0.6):
        self._newline(leading=0.4, fontsize=10)
        self.ax.plot([ML, PAGE_W - MR], [self.y, self.y], color=color, lw=lw)
        self._newline(leading=1.0, fontsize=10)

    def draw_matrix(self, cells, label=None, fontsize=10.5):
        """绘制矩阵表格（带方括号）。cells 为二维列表。"""
        cells = [[str(c) for c in row] for row in cells]
        nrows = len(cells)
        ncols = max(len(r) for r in cells)
        for r in cells:
            while len(r) < ncols:
                r.append("")

        cw = 0.34            # 每列宽
        rh = 0.27            # 每行高
        total_w = ncols * cw
        total_h = nrows * rh

        self._ensure_space(total_h + 0.3)
        x0 = ML
        if label:
            self.ax.text(ML, self.y - 0.05, label, fontsize=fontsize, ha="left", va="top")
            x0 = ML + self._measure(label + " ", fontsize)
        y_top = self.y

        for i in range(nrows):
            for j in range(ncols):
                cx = x0 + j * cw + cw / 2
                cy = y_top - i * rh - rh / 2
                self.ax.text(cx, cy, cells[i][j], ha="center", va="center",
                             fontsize=fontsize)
        # 方括号
        bx0 = x0 - 0.06
        bx1 = x0 + total_w + 0.06
        self.ax.plot([bx0 + 0.06, bx0, bx0, bx0 + 0.06],
                     [y_top, y_top, y_top - total_h, y_top - total_h],
                     color="black", lw=1.2)
        self.ax.plot([bx1 - 0.06, bx1, bx1, bx1 - 0.06],
                     [y_top, y_top, y_top - total_h, y_top - total_h],
                     color="black", lw=1.2)

        self.y = y_top - total_h - 0.18

    def box_answer(self, text: str, fontsize=11):
        """绘制带边框的最终答案（纯文本）。"""
        self._ensure_space(0.5)
        pad_x, pad_y = 0.15, 0.12
        w = min(self._measure(text, fontsize, "bold") + 2 * pad_x, CONTENT_W)
        h = fontsize / 72.0 + 2 * pad_y
        rect = FancyBboxPatch(
            (ML, self.y - h), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            linewidth=1.0, edgecolor="0.15", facecolor="0.97",
            transform=self.fig.transFigure, clip_on=False)
        self.fig.add_artist(rect)
        self.ax.text(ML + w / 2, self.y - h / 2, text, ha="center", va="center",
                     fontsize=fontsize, weight="bold")
        self.y -= h + 0.25

    def math_answer(self, latex_expr: str, fontsize=12):
        """用 mathtext 渲染数学答案（带边框）。失败则回退纯文本。"""
        try:
            s = _sanitize_mathtext(latex_expr)
            self._ensure_space(0.6)
            disp = f"${s}$"
            t = self.fig.text(0, 0, disp, fontsize=fontsize)
            renderer = self.fig.canvas.get_renderer()
            bbox = t.get_window_extent(renderer=renderer)
            t.remove()
            w = bbox.width / self.fig.dpi + 0.3
            h = bbox.height / self.fig.dpi + 0.18
            rect = FancyBboxPatch(
                (ML, self.y - h), min(w, CONTENT_W), h,
                boxstyle="round,pad=0.02,rounding_size=0.03",
                linewidth=1.0, edgecolor="0.15", facecolor="0.97",
                transform=self.fig.transFigure, clip_on=False)
            self.fig.add_artist(rect)
            self.ax.text(ML + min(w, CONTENT_W) / 2, self.y - h / 2, disp,
                         ha="center", va="center", fontsize=fontsize)
            self.y -= h + 0.25
        except Exception:
            self.box_answer(latex_to_readable(latex_expr), fontsize=11)

    def close(self):
        if self.fig is not None:
            self.pdf.savefig(self.fig)
            plt.close(self.fig)
        self.pdf.close()


# ═══════════════════════════════════════════════
# 渲染文档
# ═══════════════════════════════════════════════

def render_answer(renderer: PDFRenderer, sol: dict):
    atype = sol.get("answer_type", "text")
    if atype == "matrix" and sol.get("answer_matrix"):
        renderer.text_line("答案：", fontsize=11, weight="bold")
        renderer.draw_matrix(sol["answer_matrix"])
    elif atype == "scalar" and sol.get("answer_latex"):
        renderer.text_line("答案：", fontsize=11, weight="bold")
        renderer.math_answer(sol["answer_latex"])
    elif sol.get("answer_latex") and sol["solver"] in ("sympy_dsolve", "sympy_eigen"):
        renderer.text_line("答案：", fontsize=11, weight="bold")
        renderer.math_answer(sol["answer_latex"])
    else:
        plain = sol.get("answer_plain") or latex_to_readable(sol.get("answer_latex", ""))
        renderer.text_line("答案：", fontsize=11, weight="bold")
        renderer.box_answer(plain)


def render_document(solutions, course="课程", student="学生", title="作业解答",
                    out_pdf="homework.pdf", date_str=None):
    if date_str is None:
        date_str = date.today().isoformat()

    renderer = PDFRenderer(out_pdf, title, course, student, date_str)

    for sol in solutions:
        pid = sol["problem_id"]
        renderer._ensure_space(1.0)
        renderer.text_line(f"第 {pid} 题", fontsize=13, weight="bold", leading=1.5)

        # 题目原文（可读化）
        problem_text = latex_to_readable(sol.get("problem_text", ""))
        renderer.wrapped_text(problem_text, fontsize=10.5)

        if sol.get("solved"):
            renderer.text_line("解：", fontsize=11, weight="bold", color="0.05")
            for step in sol.get("steps", []):
                step_plain = latex_to_readable(step)
                renderer.wrapped_text(step_plain, fontsize=10.5, leading=1.3)
            renderer._newline(leading=0.5, fontsize=10)
            render_answer(renderer, sol)
        else:
            reason = sol.get("reason", "未求解")
            renderer.text_line(f"（未求解：{reason}）", fontsize=10.5, color="0.7")

        renderer.hrule()

    total = len(solutions)
    solved = sum(1 for s in solutions if s.get("solved"))
    renderer._newline(leading=1.0, fontsize=10)
    renderer.text_line(f"自动求解统计：{solved}/{total} 题（{100 * solved // total}%）。",
                       fontsize=10, color="0.4")
    renderer.close()
    return out_pdf


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="用 matplotlib 生成作业解答 PDF（无需 TeX）")
    parser.add_argument("solutions_json", help="3_solutions.json 路径")
    parser.add_argument("output_pdf", help="输出 PDF 路径")
    parser.add_argument("--course", default="课程", help="课程名称")
    parser.add_argument("--student", default="学生", help="学生姓名")
    parser.add_argument("--title", default="作业解答", help="标题")
    args = parser.parse_args()

    with open(args.solutions_json, "r", encoding="utf-8") as f:
        solutions = json.load(f)

    render_document(solutions, course=args.course, student=args.student,
                    title=args.title, out_pdf=args.output_pdf)
    print(f"✅ PDF 已生成：{args.output_pdf}")


if __name__ == "__main__":
    main()
