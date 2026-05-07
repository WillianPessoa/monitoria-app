#!/usr/bin/env python3
"""Converts docs/sprints/sprint-0.md to a formatted PDF using fpdf2."""

import re
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

BASE_DIR  = Path(__file__).parent
MD_FILE   = BASE_DIR / "docs" / "sprints" / "sprint-0.md"
PDF_FILE  = BASE_DIR / "docs" / "sprints" / "sprint-0.pdf"
IMG_DIR   = BASE_DIR / "docs" / "imagens"

MARGIN      = 22
LINE_HEIGHT = 6.5
FONT_BODY   = 11
FONT_H1     = 18
FONT_H2     = 13
FONT_H3     = 12
FONT_H4     = 11

FONT_UNICODE = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_BOLD    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC  = "/System/Library/Fonts/SFNSItalic.ttf"


class Report(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("regular", size=9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def clean(text: str) -> str:
    return (text
        .replace("—", " - ")   # em dash
        .replace("–", "-")      # en dash
        .replace("‘", "'")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
        .replace("•", "*")
    )


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    return text


def render_paragraph(pdf: FPDF, text: str, indent: float = 0):
    parts = re.split(r"(\*\*.+?\*\*|\*.+?\*)", text)
    x_start = MARGIN + indent
    pdf.set_x(x_start)

    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("bold", size=FONT_BODY)
            content = part[2:-2]
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            pdf.set_font("italic", size=FONT_BODY)
            content = part[1:-1]
        else:
            pdf.set_font("regular", size=FONT_BODY)
            content = part

        if not content:
            continue

        for word in content.split(" "):
            if not word:
                continue
            word_w = pdf.get_string_width(word + " ")
            remaining = pdf.w - MARGIN - pdf.get_x()
            if word_w > remaining and pdf.get_x() > x_start + 1:
                pdf.ln(LINE_HEIGHT)
                pdf.set_x(x_start)
            pdf.cell(pdf.get_string_width(word + " "), LINE_HEIGHT, word + " ")

    pdf.ln(LINE_HEIGHT)


def render_image(pdf: FPDF, md_line: str):
    """Render a markdown image line: ![alt](path)"""
    m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", md_line)
    if not m:
        return
    alt  = m.group(1)
    path = m.group(2)

    # Resolve relative path from IMG_DIR, trying any extension if exact not found
    stem = Path(path).stem
    img_path = (IMG_DIR / Path(path).name).resolve()
    if not img_path.exists():
        for ext in (".gif", ".png", ".jpg", ".jpeg"):
            candidate = (IMG_DIR / (stem + ext)).resolve()
            if candidate.exists():
                img_path = candidate
                break
    if not img_path.exists():
        pdf.set_font("italic", size=FONT_BODY - 1)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, LINE_HEIGHT, f"[imagem nao encontrada: {Path(path).name}]",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        return

    max_w = pdf.w - MARGIN * 2
    pdf.ln(2)
    pdf.image(str(img_path), x=MARGIN, w=max_w)
    if alt:
        pdf.set_font("italic", size=FONT_BODY - 1)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, LINE_HEIGHT, alt, align="C",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(4)


def build_pdf(md_text: str) -> None:
    pdf = Report(format="A4")
    pdf.set_margins(MARGIN, 20, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=18)

    pdf.add_font("regular", style="", fname=FONT_UNICODE)
    pdf.add_font("bold",    style="", fname=FONT_BOLD)
    pdf.add_font("italic",  style="", fname=FONT_ITALIC)

    pdf.add_page()
    pdf.set_font("regular", size=FONT_BODY)

    lines = md_text.splitlines()
    i = 0
    in_list      = False
    pending_blank = False
    in_table     = False
    table_rows   = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            return

        ncols  = len(table_rows[0])
        col_w  = (pdf.w - MARGIN * 2) / ncols
        lh     = LINE_HEIGHT
        fsz    = FONT_BODY - 2   # 9pt — gives room to breathe
        pad    = 1.5             # vertical padding inside cell

        def count_lines(text, font):
            pdf.set_font(font, size=fsz)
            n, w = 1, 0
            for word in text.strip().split():
                ww = pdf.get_string_width(word + " ")
                if w + ww > col_w - 3 and w > 0:
                    n += 1
                    w = ww
                else:
                    w += ww
            return n

        for r_idx, row in enumerate(table_rows):
            is_hdr = (r_idx == 0)
            font   = "bold" if is_hdr else "regular"

            # Row height = tallest cell
            max_lines = max(count_lines(c, font) for c in row)
            row_h = max_lines * lh + pad * 2

            y0 = pdf.get_y()
            x  = MARGIN
            for cell_text in row:
                # Background + border via rect
                if is_hdr:
                    pdf.set_fill_color(230, 233, 250)
                    pdf.rect(x, y0, col_w, row_h, style="FD")
                else:
                    pdf.rect(x, y0, col_w, row_h, style="D")
                # Text
                pdf.set_font(font, size=fsz)
                pdf.set_xy(x + 1.5, y0 + pad)
                pdf.multi_cell(col_w - 3, lh, cell_text.strip(),
                               new_x=XPos.RIGHT, new_y=YPos.TOP)
                x += col_w

            pdf.set_y(y0 + row_h)

        pdf.ln(3)
        table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i]
        raw  = clean(line.rstrip())

        # Image
        if re.match(r"!\[", raw):
            if in_table: flush_table()
            if in_list:  pdf.ln(2); in_list = False
            render_image(pdf, raw)
            i += 1
            continue

        # Table row
        if raw.startswith("|") and raw.endswith("|"):
            if re.match(r"^\|[-| :]+\|$", raw):
                i += 1
                in_table = True
                continue
            in_table = True
            cells = [c for c in raw.split("|") if c != ""]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            flush_table()

        # H1
        if re.match(r"^# [^#]", raw):
            if in_list: pdf.ln(2); in_list = False
            pdf.set_font("bold", size=FONT_H1)
            pdf.set_text_color(20, 20, 60)
            pdf.multi_cell(0, 12, strip_md(raw[2:]), align="C",
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # H2
        elif raw.startswith("## "):
            if in_list: pdf.ln(2); in_list = False
            pdf.ln(3)
            pdf.set_font("bold", size=FONT_H2)
            pdf.set_fill_color(230, 233, 250)
            pdf.set_text_color(20, 20, 100)
            pdf.cell(0, 9, strip_md(raw[3:]), fill=True,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # H3
        elif raw.startswith("### "):
            if in_list: pdf.ln(2); in_list = False
            pdf.ln(3)
            pdf.set_font("bold", size=FONT_H3)
            pdf.set_text_color(30, 30, 110)
            pdf.cell(0, LINE_HEIGHT + 1, strip_md(raw[4:]),
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(180, 185, 220)
            pdf.line(MARGIN, pdf.get_y(), pdf.w - MARGIN, pdf.get_y())
            pdf.set_draw_color(0, 0, 0)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # H4
        elif raw.startswith("#### "):
            if in_list: pdf.ln(2); in_list = False
            pdf.ln(1)
            pdf.set_font("bold", size=FONT_H4)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, LINE_HEIGHT, strip_md(raw[5:]),
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)

        # Blockquote
        elif raw.startswith("> "):
            if in_list: pdf.ln(2); in_list = False
            pdf.set_fill_color(245, 245, 252)
            pdf.set_draw_color(180, 185, 220)
            content = strip_md(raw[2:])
            pdf.set_font("italic", size=FONT_BODY)
            x0 = pdf.get_x()
            pdf.set_x(MARGIN + 4)
            pdf.multi_cell(pdf.w - MARGIN * 2 - 8, LINE_HEIGHT, content,
                           border="L", fill=True,
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
            pdf.ln(1)

        # Bold-only label line
        elif re.match(r"^\*\*[^*]+\*\*$", raw):
            if in_list: pdf.ln(2); in_list = False
            pdf.ln(1)
            pdf.set_font("bold", size=FONT_BODY)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(0, LINE_HEIGHT, strip_md(raw),
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(0.5)

        # Horizontal rule
        elif raw.startswith("---"):
            if in_list: pdf.ln(2); in_list = False
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(MARGIN, pdf.get_y(), pdf.w - MARGIN, pdf.get_y())
            pdf.set_draw_color(0, 0, 0)
            pdf.ln(4)

        # Bullet
        elif raw.startswith("- "):
            if not in_list:
                pdf.ln(1)
                in_list = True
            pending_blank = False
            content = strip_md(raw[2:])
            pdf.set_font("regular", size=FONT_BODY)
            pdf.set_x(MARGIN + 5)
            pdf.cell(5, LINE_HEIGHT, "-")
            pdf.set_x(MARGIN + 10)
            pdf.multi_cell(pdf.w - MARGIN * 2 - 10, LINE_HEIGHT, content,
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Empty line
        elif raw == "":
            if in_list:
                in_list = False
                pdf.ln(2)
            elif not pending_blank:
                pdf.ln(3)
                pending_blank = True

        # Normal paragraph
        else:
            if in_list: in_list = False; pdf.ln(2)
            pending_blank = False
            pdf.set_font("regular", size=FONT_BODY)
            render_paragraph(pdf, raw)

        i += 1

    if in_table:
        flush_table()

    pdf.output(str(PDF_FILE))
    print(f"PDF gerado: {PDF_FILE}")


if __name__ == "__main__":
    text = MD_FILE.read_text(encoding="utf-8")
    build_pdf(text)
