from rich import print
from rich.align import Align
from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from rich.console import Console, RenderGroup
from rich import box

def build_ui(type: str, source, dest, fields, accounts, ports) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )
    layout["upper"].update(build_main_ui(type, source, dest, fields, accounts, ports))
    # layout["lower"].update()
    return layout

def build_main_ui(type: str, source, dest, fields, accounts, ports) -> Panel:
    main_ui = Table.grid(padding=1)
    main_ui.add_column(justify='right')
    main_ui.add_column(no_wrap=True)
    main_ui.add_row(
        "Mode:",
        type
    )
    main_ui.add_row(
        "Source:",
        source
    )
    
    main_ui.add_row(
        "Destination:",
        dest if dest != None else 'None specified'
    )
    
    main_ui.add_row(
        "Fields:",
        fields if len(fields) or fields != None else 'None specified'
    )
    
    main_ui.add_row(
        "Accounts:",
        accounts if len(accounts) != 0 or accounts != None else 'None specified'
    )

    main_ui.add_row(
        "Ports:",
        ports if len(ports) != 0 or ports != None else 'None specified'
    )
    main_panel = Panel(
        Align.center(
            main_ui
        ),
        box=box.ROUNDED,
        padding=(1,2),
        title="Information",
        border_style="bright_blue"
    )
    return main_panel
