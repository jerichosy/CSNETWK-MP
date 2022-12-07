import click


@click.group()
def cli():
    pass

@cli.command()
def create():
    click.echo('create called')
    # os.system('curl http://127.0.0.1:5000/create')

@cli.command()
def conn():
    click.echo('conn called')
    # os.system('curl http://127.0.0.1:5000/')

def main():
    value = click.prompt('Select a command to run', type=click.Choice(list(cli.commands.keys()) + ['exit']))
    while value != 'exit':
        cli.commands[value]()

if __name__ == "__main__":
    main()
