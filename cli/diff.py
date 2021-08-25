import click


@click.command()
@click.argument('secid1')
@click.argument('secid2')
def diff(secid1, secid2):
    print(f'Hello {secid1} {secid2}')
