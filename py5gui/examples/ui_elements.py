import py5
import sys, os
# insert into path before the installed package to directly see code updates
sys.path.insert(1, os.path.join(sys.path[0], '..'))

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
    
def draw():
    [button.run() for button in py5.get_current_sketch().buttons]
    py5.get_current_sketch().text_input.run()
    #print_coordinates(py5)

py5.run_sketch()