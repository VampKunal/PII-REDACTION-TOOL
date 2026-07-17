from src.models import TextSpan

def extract_spans(doc) -> list[TextSpan]:
    spans = []
    # 1. Body paragraphs
    for p_idx, para in enumerate(doc.paragraphs):
        for r_idx, run in enumerate(para.runs):
            if run.text:
                spans.append(TextSpan(run.text, "paragraph", p_idx, r_idx, run))

    # 2. Tables
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                for p_idx, para in enumerate(cell.paragraphs):
                    for rn_idx, run in enumerate(para.runs):
                        if run.text:
                            spans.append(TextSpan(
                                run.text, "table",
                                p_idx, rn_idx, run,
                                table_idx=t_idx, row_idx=r_idx, col_idx=c_idx
                            ))

    # 3. Headers and footers
    for section in doc.sections:
        for part in [section.header, section.footer]:
            if part:
                for p_idx, para in enumerate(part.paragraphs):
                    for r_idx, run in enumerate(para.runs):
                        if run.text:
                            spans.append(TextSpan(run.text, "header_footer", p_idx, r_idx, run))

    return spans
