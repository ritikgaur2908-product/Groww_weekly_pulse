import typer
import logging
from datetime import datetime

from pulse.pipeline import run_pulse_pipeline

app = typer.Typer(help="Weekly Product Review Pulse CLI")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.callback()
def callback():
    """
    Weekly Product Review Pulse CLI
    """
    pass

@app.command()
def run(
    product: str = typer.Option(..., help="The product name, e.g., 'groww'"),
    week: str = typer.Option(..., help="The ISO week to run the report for, e.g., '2026-W24'")
):
    """
    Run the pulse pipeline for a specific product and ISO week.
    """
    typer.echo(f"Starting pipeline for product: {product}, week: {week}")
    run_pulse_pipeline(product=product, week=week)

if __name__ == "__main__":
    app()
