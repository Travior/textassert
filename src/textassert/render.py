from rich.panel import Panel
from rich.markdown import Markdown
from textassert.schema.project import Criterion

def render_criterion_panel(criterion: Criterion) -> Panel:
    has_passed = "[green]Passed[/green]" if criterion.passed else "[red]Failed[/red]"
    
    content = ""
    if criterion.feedbacks:
        for fb in criterion.feedbacks:
            if fb.quote:
                content += f"\n> {fb.quote}\n"
            if fb.feedback:
                content += f"\n{fb.feedback}\n"
            renderable = Markdown(content.strip())
    else:
        renderable = "[gray] No issues found.[/gray]"

    panel = Panel(
        title=f"[bold]{criterion.name}[/bold] - [bold]{has_passed}[/bold]",
        renderable=renderable
    )
    return panel
