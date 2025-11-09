import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML  # type: ignore
from weasyprint.text.fonts import FontConfiguration  # type: ignore

from src.utils import format_check_number, format_currency, format_date


def get_template_dir(template_name: str) -> tuple[Path, Path]:
    """Get the template directory and executable directory"""
    if getattr(sys, "frozen", False):
        # If the application is frozen, use the bundle directory
        bundle_dir = Path(sys._MEIPASS)  # type: ignore
        executable_dir = Path(sys.executable).parent
    else:
        # If the application is not frozen, use the current directory
        bundle_dir = Path(__file__).parent.parent.parent
        executable_dir = bundle_dir
    return bundle_dir / "templates" / template_name, executable_dir


def render_template_html(template_name: str, template_data: dict) -> tuple[str, Path]:
    """
    Render a Jinja2 template to HTML string.

    Args:
        template_name: Name of the template directory and file (without extension)
        template_data: Dictionary containing all the data to populate the template

    Returns:
        tuple: (rendered HTML string, template directory path for base_url)

    Raises:
        FileNotFoundError: If the template file is not found
    """
    template_dir, _ = get_template_dir(template_name)
    template_file = template_dir / f"{template_name}.htm"

    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "htm"]),
    )

    # Add custom filters
    env.filters["format_date_short"] = format_date
    env.filters["format_currency"] = format_currency
    env.filters["format_check_number"] = format_check_number

    # Load and render the template
    template = env.get_template(f"{template_name}.htm")
    rendered_html = template.render(**template_data)

    return rendered_html, template_dir


def generate_pdf(
    template_name: str,
    pages_data: list[dict],
    output_path: str,
) -> str:
    """
    Generate a PDF from one or more pages using a specified template.

    Args:
        template_name: Name of the template to use (e.g., "payment_order")
        pages_data: List of dictionaries, each containing data for one page.
                    For single page PDFs, pass a list with one element.
        output_path: Path where the PDF will be saved (relative to executable/project root)

    Returns:
        str: Absolute path to the generated PDF file

    Raises:
        FileNotFoundError: If the template file is not found
        Exception: If PDF generation fails
    """
    if not pages_data:
        raise ValueError("pages_data cannot be empty")

    _, executable_dir = get_template_dir(template_name)
    font_config = FontConfiguration()

    # Render all pages
    documents = []
    for page_data in pages_data:
        rendered_html, template_dir = render_template_html(template_name, page_data)
        html_doc = HTML(string=rendered_html, base_url=str(template_dir))
        documents.append(html_doc.render(font_config=font_config))

    # Combine all pages
    all_pages = []
    for doc in documents:
        all_pages.extend(doc.pages)

    # Write PDF
    pdf_path = executable_dir / output_path
    documents[0].copy(all_pages).write_pdf(str(pdf_path))

    return str(pdf_path.absolute())
