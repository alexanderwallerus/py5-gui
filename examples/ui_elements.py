import py5
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # insert and use the local py5gui package in the python path before an environment install
import py5gui as ui

confirm_click = lambda : print('triggered button')
print_text = lambda text, end='' : print(f'{text}{end}')
change_background = lambda : py5.background(py5.random(255), py5.random(255), py5.random(255))
print_input = lambda text : print(text)

def setup():
    py5.size(500, 500, py5.P2D)
    py5.background(0)
    #instead of using globals, the buttons can be stored within the sketch instance
    py5.get_current_sketch().buttons = [
        ui.Button(py5=py5, label='simple button', pos=(20, 50),
                  on_click=confirm_click),
        ui.Button(py5=py5, label='change background', pos=(50, 0), 
                  on_click=change_background),
        ui.Button(py5=py5, label='print to console', pos=(150, 30), 
                  on_click=print_text,
                  func_args=('first line',), func_kwargs={'end':'\nsecond line :)'})]
    py5.get_current_sketch().text_input = ui.Text_Input(py5=py5, pos=(20, 90), execute_func=print_input)

    with ui.Col(py5=py5, pos=(30, 140), h=150) as simple_column:
        simple_column.add(ui.Button(py5=py5, label='a', on_click=lambda:print('a')))
        simple_column.add(ui.Button(py5=py5, label='b', on_click=lambda:print('b')))
        simple_column.add(ui.Button(py5=py5, label='button c', on_click=lambda:print('pressed button c')))
    py5.get_current_sketch().simple_column = simple_column

    with ui.Row(py5=py5, pos=(150, 140), w=220) as nested_row:
        with ui.Col(py5=py5, pos=(50, 140), h=200) as first_col:
            first_col.add(ui.Button(py5=py5, label='a', on_click=lambda:print('a')))
            first_col.add(ui.Button(py5=py5, label='b', on_click=lambda:print('b')))
            first_col.add(ui.Button(py5=py5, label='cdefgh', on_click=lambda:print('cdefgh')))
            nested_row.add(first_col)
        with ui.Col(py5=py5, h=200) as second_col:
            second_col.add(ui.Button(py5=py5, label='d', on_click=lambda:print('d')))
            second_col.add(ui.Button(py5=py5, label='e', on_click=lambda:print('e')))
            nested_row.add(second_col)
            with ui.Row(py5=py5, w=100) as inner_row:   # TODO: too large nested elements break organization
                inner_row.add(ui.Button(py5=py5, label='f', on_click=lambda:print('f')))
                inner_row.add(ui.Button(py5=py5, label='g', on_click=lambda:print('g')))
                second_col.add(inner_row)
    
    py5.get_current_sketch().nested_row = nested_row

    
def draw():
    [button.run() for button in py5.get_current_sketch().buttons]
    py5.get_current_sketch().text_input.run()
    py5.get_current_sketch().simple_column.run()
    py5.get_current_sketch().nested_row.run()
    #print_coordinates(py5)

py5.run_sketch()