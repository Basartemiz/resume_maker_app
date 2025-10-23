# to_pdf.py
from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

def create_pdf(html_dict: Dict[str, Any], template_name: str, css_name: str) -> Path:
    cwd = Path.cwd()
    # Paths
    html_file = cwd / "templates" / f"{template_name}.html"
    out_html  = cwd / "resume.html"
    out_pdf   = cwd / "resume.pdf"

    css_custom    = cwd / "templates" / "assets" / f"{css_name}.css"

    # Sanity checks
    if not html_file.exists():
        raise FileNotFoundError(f"Template not found: {html_file}")
    if not css_custom.exists():
        raise FileNotFoundError(f"Custom CSS not found: {css_custom}")

    # Render HTML via Jinja2
    env = Environment(
        loader=FileSystemLoader(str(html_file.parent)),
        autoescape=select_autoescape(["html", "xml"])
    )
    tpl = env.get_template(html_file.name)
    rendered_html = tpl.render(**html_dict)

    # (Optional) write the intermediate HTML for debugging
    out_html.write_text(rendered_html, encoding="utf-8")

    # Convert to PDF with WeasyPrint
    # IMPORTANT: base_url is the folder containing the template so relative CSS/asset paths resolve.
    HTML(string=rendered_html).write_pdf(
        target=str(out_pdf),
        stylesheets=[CSS(filename=str(css_custom))]
    )

    print(f"Built HTML -> {out_html.resolve()}")
    print(f"Built PDF  -> {out_pdf.resolve()}")
    return out_pdf

def main():
    # Load the already-normalized context your template expects
    # (This is the file produced by your normalize/render script)
    cwd = Path.cwd()
    normalized_path = cwd / "templates" / "assets" / "normalized_dict.json"
    print(normalized_path)
    if not normalized_path.exists():
        raise FileNotFoundError("normalized_dict.json not found. Create it first (your normalize script writes it).")

    with normalized_path.open("r", encoding="utf-8") as f:
        html_dict = json.load(f)

    create_pdf(html_dict, template_name="harward_style", css_name="harward")

if __name__ == "__main__":
    main()
