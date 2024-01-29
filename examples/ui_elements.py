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

    with ui.Col(py5=py5, pos=(30, 140), max_h=200, max_w=None) as simple_column:
        simple_column.add(ui.Button(py5=py5, label='a', on_click=lambda:print('a')))
        simple_column.add(ui.Button(py5=py5, label='b', on_click=lambda:print('b')))
        simple_column.add(ui.Button(py5=py5, label='button c', on_click=lambda:print('pressed button c')))
        simple_column.add(ui.Button(py5=py5, label='c', on_click=lambda:print('c')))
        simple_column.add(ui.Button(py5=py5, label='d', on_click=lambda:print('d')))
    py5.get_current_sketch().simple_column = simple_column

    with ui.Row(py5=py5, pos=(120, 140), max_h=None, max_w=160) as simple_row:
        simple_row.add(ui.Button(py5=py5, label='a', on_click=lambda:print('a')))
        simple_row.add(ui.Button(py5=py5, label='b', on_click=lambda:print('b')))
    py5.get_current_sketch().simple_row = simple_row
    # if an organizer used max_w or max_h allowing for additional space, further elements can still be added
    simple_row.add(ui.Button(py5=py5, label='c', on_click=lambda:print('c')))
    # additional elements exceeding the organizer's length won't be added
    simple_row.add(ui.Button(py5=py5, label='d', on_click=lambda:print('d')))

    with ui.Row(py5=py5, pos=(220, 200), max_w=None, max_h=None) as nested_row:
        with ui.Col(py5=py5, max_h=None) as first_col:
            first_col.add(ui.Button(py5=py5, label='a', on_click=lambda:print('a')))
            first_col.add(ui.Button(py5=py5, label='b', on_click=lambda:print('b')))
        nested_row.add(first_col)
        with ui.Col(py5=py5) as second_col:
            with ui.Row(py5=py5, pos=(220, 200), max_w=None, max_h=None) as nested_nested_row:
                nested_nested_row.add(ui.Button(py5=py5, label='c', on_click=lambda:print('c')))
                nested_nested_row.add(ui.Button(py5=py5, label='d', on_click=lambda:print('d')))
            second_col.add(nested_nested_row)
            second_col.add(ui.Button(py5=py5, label='efghij', on_click=lambda:print('efghij')))
        nested_row.add(second_col)
    py5.get_current_sketch().nested_row = nested_row

    
def draw():
    [button.run() for button in py5.get_current_sketch().buttons]
    py5.get_current_sketch().text_input.run()
    py5.get_current_sketch().simple_column.run()
    py5.get_current_sketch().simple_row.run()
    py5.get_current_sketch().nested_row.run()
    #print_coordinates(py5)

def exit():
    print('closing')

py5.run_sketch()