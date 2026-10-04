#!/usr/bin/env python3
"""
一键流水线：串联 Stage 1-5，从作业文件到 PDF。

用法:
    python pipeline.py <输入文件> <输出目录> [选项]

示例:
    python pipeline.py examples/sample_homework.md output/
    python pipeline.py homework.pdf output/ --compile
    python pipeline.py homework.docx output/ --course "Linear Algebra" --student "张三"

选项:
    --compile           编译 PDF（需要 LaTeX 环境）
    --course NAME       课程名称（默认: Mathematics）
    --student NAME      学生姓名（默认: Student）
    --title TITLE       作业标题（默认: Homework Solutions）
    --verbose           显示详细输出
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ── Windows 控制台编码兜底：避免 emoji/中文在 GBK 终端下崩溃 ──
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 添加 scripts 目录到 path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

# ── Auto-install dependencies if missing ──────────────
from bootstrap import ensure_dependencies, SKILL_ROOT
ensure_dependencies()

from ingest import ingest
from parse_problems import parse_problems
from solve import solve_all
from render_latex import render_document, compile_pdf


def run_pipeline(
    input_path: str,
    output_dir: str,
    course: str = "Mathematics",
    student: str = "Student",
    title: str = "Homework Solutions",
    do_compile: bool = False,
    do_pdf: bool = False,
    do_verify: bool = True,
    provider: str = None,
    model: str = None,
    api_key: str = None,
    verbose: bool = False,
):
    """
    执行完整的作业求解流水线。

    Stage 1: 文档摄入 → 1_ingested.json
    Stage 2: 题目解析 → 2_parsed.json
    Stage 3: 自动求解 → 3_solutions.json（SymPy + 国产 LLM 回退）
    Stage 4: LaTeX 生成 → homework.tex
    Stage 5: PDF 生成 → homework.pdf（matplotlib，无需 TeX；--compile 走 LaTeX）
    Stage 5b: 独立核验 → verification.json
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    print("=" * 60)
    print("🚀 作业自动求解流水线")
    print(f"   输入: {input_path}")
    print(f"   输出: {output_dir}")
    print("=" * 60)

    # ── Stage 1: 文档摄入 ──────────────────────
    print("\n📄 Stage 1: 文档摄入")
    try:
        ingested = ingest(input_path)
        ingested_path = output_dir / "1_ingested.json"
        with open(ingested_path, "w", encoding="utf-8") as f:
            json.dump(ingested, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 格式: {ingested['format']}, 分段: {len(ingested['sections'])}")
    except Exception as e:
        print(f"   ❌ 摄入失败: {e}")
        sys.exit(1)

    # ── Stage 2: 题目解析 ──────────────────────
    print("\n🔍 Stage 2: 题目解析")
    try:
        problems = parse_problems(ingested)
        parsed_path = output_dir / "2_parsed.json"
        with open(parsed_path, "w", encoding="utf-8") as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 识别题目: {len(problems)} 道")
        for p in problems:
            subs = f" ({len(p['sub_problems'])} 子题)" if p["sub_problems"] else ""
            print(f"      Problem {p['id']}: [{p['type']}]{subs}")
    except Exception as e:
        print(f"   ❌ 解析失败: {e}")
        sys.exit(1)

    if not problems:
        print("\n⚠️ 未识别到任何题目。请检查输入文件格式。")
        print("   支持的题号格式: 'Problem N' / '题 N' / 'N.' / 'N)' / 'Q.N'")
        sys.exit(1)

    # ── Stage 3: 自动求解 ──────────────────────
    print("\n🧮 Stage 3: 自动求解")
    # 配置国产大模型引擎（可选）。未提供 key 时走 offline 确定性回退。
    if provider:
        os.environ["LLM_PROVIDER"] = provider
        if model:
            os.environ["LLM_MODEL"] = model
        if api_key:
            os.environ[{"qwen": "DASHSCOPE_API_KEY", "kimi": "MOONSHOT_API_KEY",
                         "deepseek": "DEEPSEEK_API_KEY"}.get(provider, "LLM_API_KEY")] = api_key
        print(f"   🤖 LLM 引擎: {provider}" + (f" ({model})" if model else "") )
    else:
        print("   🤖 LLM 引擎: offline（SymPy 确定性回退；设置 --provider qwen --api-key sk-... 启用）")
    try:
        solutions = solve_all(problems)
        solutions_path = output_dir / "3_solutions.json"
        with open(solutions_path, "w", encoding="utf-8") as f:
            json.dump(solutions, f, ensure_ascii=False, indent=2)

        solved = sum(1 for s in solutions if s["solved"])
        total = len(solutions)
        print(f"   ✅ 求解完成: {solved}/{total}")
        for s in solutions:
            status = "✅" if s["solved"] else "❌"
            info = s.get("answer_latex", s.get("reason", ""))[:50]
            print(f"      {status} Problem {s['problem_id']}: {info}")
    except Exception as e:
        print(f"   ❌ 求解失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ── Stage 4: LaTeX 生成 ──────────────────────
    print("\n📝 Stage 4: LaTeX 生成")
    try:
        has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in (course + student + title)) or \
            any("\u4e00" <= ch <= "\u9fff" for s in solutions for ch in s.get("problem_text", ""))
        tex_content = render_document(
            solutions,
            course=course,
            student=student,
            title=title,
            chinese=has_chinese,
        )
        tex_path = output_dir / "homework.tex"
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)
        print(f"   ✅ LaTeX 文件: {tex_path}")
    except Exception as e:
        print(f"   ❌ LaTeX 生成失败: {e}")
        sys.exit(1)

    # ── Stage 5: PDF 生成 ──────────────────────
    pdf_path = None
    if do_pdf or do_compile:
        print("\n📑 Stage 5: PDF 生成")
    if do_pdf:
        try:
            from render_pdf import render_document as render_pdf_document
            pdf_path = output_dir / "homework.pdf"
            render_pdf_document(
                solutions, course=course, student=student, title=title,
                out_pdf=str(pdf_path),
            )
            print(f"   ✅ PDF 文件（matplotlib，无需 TeX）: {pdf_path}")
        except Exception as e:
            print(f"   ⚠️ matplotlib PDF 生成失败: {e}")
    if do_compile:
        print("   （尝试 LaTeX 编译）")
        success = compile_pdf(str(tex_path), str(output_dir))
        if success:
            print(f"   ✅ LaTeX 编译 PDF: {output_dir / 'homework.pdf'}")
        else:
            print("   ⚠️ 未安装 LaTeX（pdflatex/xelatex），已用 matplotlib 生成 PDF")
    if not (do_pdf or do_compile):
        print("\n📑 Stage 5: PDF 生成（跳过）")
        print("   添加 --pdf 参数（matplotlib，无需 TeX）或 --compile（需要 LaTeX）")

    # ── Stage 5b: 独立核验 ──────────────────────
    if do_verify:
        print("\n🔬 Stage 5b: 独立核验")
        try:
            from verify import verify
            results = verify(problems, solutions)
            with open(output_dir / "verification.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            passed = sum(1 for r in results if r["ok"])
            print(f"   ✅ 核验通过: {passed}/{len(results)}")
        except Exception as e:
            print(f"   ⚠️ 核验失败: {e}")

    # ── 汇总 ──────────────────────────────────
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 流水线执行完成")
    print(f"   耗时: {elapsed:.1f} 秒")
    print(f"   题目: {total} 道")
    print(f"   已解: {solved} 道 ({100*solved/total:.0f}%)")
    print(f"   输出文件:")
    for f in sorted(output_dir.iterdir()):
        size = f.stat().st_size
        print(f"      {f.name} ({size:,} bytes)")
    print("=" * 60)

    return {
        "total": total,
        "solved": solved,
        "output_dir": str(output_dir),
        "elapsed": elapsed,
        "pdf": str(pdf_path) if pdf_path else None,
    }


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="作业自动求解流水线: 文件 → 解析 → 求解 → LaTeX → PDF"
    )
    parser.add_argument("input", help="输入文件路径 (md/pdf/docx/图片)")
    parser.add_argument("output_dir", help="输出目录")
    parser.add_argument("--compile", action="store_true", help="用 LaTeX 编译 PDF（需本机 TeX）")
    parser.add_argument("--pdf", action="store_true", help="用 matplotlib 生成 PDF（无需 TeX）")
    parser.add_argument("--no-verify", action="store_true", help="跳过独立核验")
    parser.add_argument("--provider", choices=["qwen", "kimi", "deepseek"], help="国产大模型提供商")
    parser.add_argument("--model", help="模型名（如 qwen-plus / moonshot-v1-8k）")
    parser.add_argument("--api-key", help="API key（也可用环境变量）")
    parser.add_argument("--course", default="Mathematics", help="课程名称")
    parser.add_argument("--student", default="Student", help="学生姓名")
    parser.add_argument("--title", default="Homework Solutions", help="作业标题")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误: 输入文件不存在 — {args.input}")
        sys.exit(1)

    run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        course=args.course,
        student=args.student,
        title=args.title,
        do_compile=args.compile,
        do_pdf=args.pdf,
        do_verify=not args.no_verify,
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
