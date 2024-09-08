import py5
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # insert and use the local py5gui package in the python path before an environment install
import py5gui as ui

background_color = (0,)
def change_background():
    global background_color
    background_color = (py5.random(255), py5.random(255), py5.random(255))

confirm_click = lambda : print('triggered button')
print_text = lambda text, end='' : print(f'{text}{end}')
print_input = lambda value : print(value)

def setup():
    py5.size(500, 500, py5.P2D)
    py5.background(0)
    ui.Button(label='simple button', pos=(20, 50), on_click=confirm_click),
    # the sketch instance can optionally be provided for multi-sketch py5-class-mode applications
    ui.Button(sketch=py5.get_current_sketch(), label='change background', pos=(50, 0), on_click=change_background),
    # ui.run() will run all created elements
    ui.Button(label='print to console', pos=(150, 30), on_click=print_text, func_args=('first line',), 
                                           func_kwargs={'end':'\nsecond line :)'})
    ui.Text_Input(pos=(20, 90), on_enter=print_input, label='enter to print', default='my input')
    # elements can can be stored within the sketch instance to .run() just a subselection instead of all elements
    py5.get_current_sketch().my_inputs = [ui.Text_Input(pos=(320, 90), on_enter=print_input)]

    with ui.Col(pos=(30, 140), max_h=200, max_w=None) as simple_column:
        simple_column.add(ui.Button(label='a', on_click=lambda:print('a')))
        simple_column.add(ui.Button(label='b', on_click=lambda:print('b')))
        simple_column.add(ui.Button(label='button c', on_click=lambda:print('pressed button c')))
        simple_column.add(ui.Button(label='c', on_click=lambda:print('c')))
        simple_column.add(ui.Button(label='d', on_click=lambda:print('d')))

    with ui.Row(pos=(120, 140), max_h=None, max_w=160) as simple_row:
        simple_row.add(ui.Button(label='a', on_click=lambda:print('a')))
        simple_row.add(ui.Button(label='b', on_click=lambda:print('b')))
    # if an organizer used max_w or max_h allowing for additional space, further elements can still be added
    simple_row.add(ui.Button(label='c', on_click=lambda:print('c')))
    # additional elements exceeding the organizer's length won't be added
    simple_row.add(ui.Button(label='d', on_click=lambda:print('d')))

    with ui.Row(pos=(220, 200), max_w=None, max_h=None) as nested_row:
        with ui.Col(max_h=None) as first_col:
            a_button = first_col.add(ui.Button(label='a', on_click=lambda:print('a')))
            first_col.add(ui.Button(label='b', on_click=lambda:print('b')))
        nested_row.add(first_col)
        with ui.Col() as second_col:
            with ui.Row(pos=(220, 200), max_w=None, max_h=None) as nested_nested_row:
                nested_nested_row.add(ui.Button(label='c', on_click=lambda:print('c')))
                nested_nested_row.add(ui.Button(label='d', on_click=lambda:print('d')))
            second_col.add(nested_nested_row)
            second_col.add(ui.Button(label='efghij', on_click=lambda:print('efghij')))
        nested_row.add(second_col)
    # change something on the stored button after creation
    a_button.label = 'A!'

    with ui.Col(pos=(20, 350)) as sliders:
        sliders.add(ui.Slider())
        sliders.add(ui.Slider(min=-40_000, max=40_000, value=4000))
        sliders.add(ui.Slider(min=0.000_05, max=0.000_10, label='small number'))
    ui.Slider(pos=(20, 460), width=200, step_decimals=1, on_change=lambda value: print(value))
    ui.Slider(pos=(230, 460), width=85, step_decimals=0, value=1)

    with ui.Col(pos=(190, 350)) as linked_sliders:
        recipient = linked_sliders.add(ui.Slider())
        def set_recipient_value(value):
            recipient.value = value
        linked_sliders.add(ui.Slider(on_change=set_recipient_value))

    with ui.Col(pos=(365, 350)) as toggles:
        toggles.add(ui.Toggle(labels='click me'))
        toggles.add(ui.Toggle(labels=('off', 'on'), on_click=lambda value: print(f'turned toggle to {value}')))

    
def draw():
    global background_color
    py5.background(*background_color)
    ui.run()
    
    # use the following line instead to just run the element stored in my_inputs[0]
    # py5.get_current_sketch().my_inputs[0].run()

    #print_coordinates(py5.get_current_sketch())

def key_pressed(e):
    ui.connect_keyboard(e)

def exit():
    print('closing')

py5.run_sketch()