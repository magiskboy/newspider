import click
import asyncio
import uvicorn
from newspider.runner import Runner
from newspider.runner import SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, default_config
from newspider import create_app


app = create_app()

delay_mapping = {
    'SECOND': SECOND,
    'MINUTE': MINUTE,
    'HOUR': HOUR,
    'DAY': DAY,
    'WEEK': WEEK,
    'MONTH': MONTH,
}

@click.group()
def cli():
    pass


@cli.command()
@click.option('--config', type=click.STRING, default=None)
def clone(config):
    cnf = default_config
    if config:
        cnf = {}
        for sp in config.split(';'):
            name, delay = sp.split('=')
            cnf[name] = {'delay': delay_mapping[delay]}

    runner = Runner(cnf)
    loop = asyncio.get_event_loop()
    loop.create_task(runner.run())
    click.echo(f'Custom configure:\n{cnf}')
    click.echo('Cloner is running...')
    loop.run_forever()


@cli.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8000)
@click.option('--reload', default=False)
@click.option('--workers', default=1)
def web(host, port, reload, workers):
    uvicorn.run('__main__:app', host=host,
                port=port, reload=reload, workers=workers)



if __name__ == '__main__':
    cli()
