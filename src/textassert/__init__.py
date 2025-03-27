import click
import json
from textassert.schema.project import ProjectFile, PROJECT_FILENAME, Project, Criterion, Settings, SETTINGS_FILEPATH
from textassert.ai import send_request
from pathlib import Path
import asyncio
from textassert.render import render_criterion_panel
from rich.console import Console

@click.group()
@click.pass_context
def cli(ctx):
    if not SETTINGS_FILEPATH.exists():
        settings = Settings(openrouter_api_key="")
    else:
        with open(SETTINGS_FILEPATH, "r") as f:
            settings = Settings.model_validate_json(f.read())
    ctx.ensure_object(dict)
    ctx.obj['settings'] = settings

def _flush_project_file(project_file: ProjectFile, filename: str):
    with open(Path(filename).parent / PROJECT_FILENAME, "w") as f:
        json.dump(project_file.model_dump(), f)

def _flush_settings(settings: Settings):
    if not SETTINGS_FILEPATH.parent.exists():
        SETTINGS_FILEPATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILEPATH, "w") as f:
        json.dump(settings.model_dump(), f)

@cli.group()
@click.argument('filename', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.pass_context
def file(ctx, filename: str):
    """CLI tool that takes a filename as first argument"""
    ctx.ensure_object(dict)
    ctx.obj['filename'] = Path(filename).name

    filename = ctx.obj['filename']
    if not Path(filename).exists():
        print(f"File {filename} does not exist")
        return
    if not (Path(filename).parent / PROJECT_FILENAME).exists():
        project_file = ProjectFile(projects=[])
    else:
        with open(Path(filename).parent / PROJECT_FILENAME, "r") as f:
            project_file = ProjectFile.model_validate_json(f.read())
    if filename not in [p.file for p in project_file.projects]:
        project_file.projects.append(Project(file=filename, criteria=[]))
    ctx.obj['project_file'] = project_file

settings = click.Group("settings")
cli.add_command(settings)

@file.command()
@click.pass_context
def evaluate(ctx):
    if ctx.obj['settings'].openrouter_api_key == "":
        print("No OpenRouter API key found. Please set one using `textassert settings set-api-key`")
        return
    project_file: ProjectFile = ctx.obj['project_file']
    console = Console()

    async def run_requests_for_project(project: Project):
        tasks = []
        for criterion in project.criteria:
            tasks.append(send_request(criterion, project, ctx.obj['settings']))
        return await asyncio.gather(*tasks)

    for project in project_file.projects:
        if project.file == ctx.obj['filename']:
            responses = asyncio.run(run_requests_for_project(project))
            criterion_response_map = {r["criterion"]: r["response"] for r in responses}
        
            for criterion in project.criteria:
                criterion.passed = criterion_response_map[criterion.name].passed
                criterion.feedbacks = criterion_response_map[criterion.name].feedbacks
                console.print(render_criterion_panel(criterion))
            _flush_project_file(project_file, ctx.obj['filename'])


@settings.command()
@click.pass_context
def set_api_key(ctx):
    settings = ctx.obj['settings']
    settings.openrouter_api_key = click.prompt("Enter your OpenRouter API key. This will be stored in plaintext in at ~/.textassert/settings.json")
    _flush_settings(settings)

c_group = click.Group(name="criteria")
file.add_command(c_group)

@c_group.command()
@click.pass_context
def add(ctx):
    project_file = ctx.obj['project_file']
    name = click.prompt("Enter the name of the criterion you want your text to be evaluated on")
    description = click.prompt("Enter the description of the criterion you want your text to be evaluated on")
    project_file.projects[0].criteria.append(Criterion(name=name, description=description, passed=False, feedbacks=[]))
    _flush_project_file(project_file, ctx.obj['filename'])


