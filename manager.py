import click
import asyncio
import uvicorn
from newspider.runner import Runner
from newspider import create_app


app = create_app()


@click.group()
def cli():
    pass


@cli.command()
def clone():
    runner = Runner()
    loop = asyncio.get_event_loop()
    loop.create_task(runner.run())
    click.echo('Cloner is running...')
    loop.run_forever()

@cli.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8000)
@click.option('--reload', default=False)
@click.option('--workers', default=1)
def web(host, port, reload, workers):
    uvicorn.run('__main__:app', host=host, port=port, reload=reload, workers=workers)



if __name__ == '__main__':
    cli()
