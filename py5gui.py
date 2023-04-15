import os
from utils.plot import Plot, legend

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

class GUI_Element:
    def __init__(self, py5=None, pos=(0,0), label='', w=30, h=30):
        self.x = pos[0]; self.y = pos[1]
        self.label = label
        self.p = py5
        
        self.h = h;     self.w = w
        self.center = (self.x + self.w/2, self.y + self.h/2)
        
        self.fill = (0,);   self.stroke = (127,);   self.pressed_stroke=(255,)
        self.highlight_fill = (32,)
        self.text_fill = (255,);    self.text_stroke = (127,)
        self.stroke_weight = 3
        
    def mouse_in(self):
        return True if self.p.mouse_x > self.x and self.p.mouse_x < self.x+self.w and \
               self.p.mouse_y > self.y and self.p.mouse_y < self.y+self.h else False
               
    def set_style(self, highlight=False, pressed=False):
        self.p.stroke(*self.pressed_stroke) if pressed else self.p.stroke(*self.stroke)
        self.p.fill(*self.highlight_fill) if highlight else self.p.fill(0)
        self.p.stroke_weight(self.stroke_weight)
        self.p.rect_mode(self.p.CENTER)
        self.p.text_align(self.p.CENTER, self.p.CENTER)
        
    def set_text_style(self):
        self.p.fill(*self.text_fill);   self.p.stroke(*self.text_stroke)

class Button(GUI_Element):
    def __init__(self, execute_func=None, func_args=None, func_kwargs=None, **kwargs):
        """You can provide a function to be triggered by this button with execute_func."""
        w = kwargs['py5'].text_width(kwargs['label']) + 30
        self.func_args, self.func_kwargs = func_args, func_kwargs
        super().__init__(**kwargs, w=w)

        self.execute_func = execute_func
        self.prev_mouse_pressed = False
    
    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.p.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.execute_func( *(self.func_args if self.func_args else ()),
                                  **(self.func_kwargs if self.func_kwargs else {}))
        
        with self.p.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed)
            self.p.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            self.p.text(self.label, self.center[0], self.center[1])
        
        self.prev_mouse_pressed = self.p.is_mouse_pressed

class Text_Input(GUI_Element):
    pass

def print_coordinates(py5=None):
    """"print the currently moused over coordinates"""
    print(f'x: {py5.mouse_x} y: {py5.mouse_y}')

if __name__=='__main__':
    import py5
    
    confirm_click = lambda : print('triggered button')
    print_text = lambda text, end='' : print(f'{text}{end}')
    change_background = lambda : py5.background(py5.random(255), py5.random(255), py5.random(255))
    
    def setup():
        py5.size(500, 500, py5.P2D)
        py5.background(0)
        #instead of using globals, the buttons can be stored within the sketch instance
        py5.get_current_sketch().buttons = [
                    Button(py5=py5, label='simple button', pos=(20, 50),
                           execute_func=confirm_click),
                    Button(py5=py5, label='change background', pos=(50, 0), 
                           execute_func=change_background),
                    Button(py5=py5, label='print to console', pos=(150, 30), 
                           execute_func=print_text,
                           func_args=('first line',), func_kwargs={'end':'\nsecond line :)'})]
        
    def draw():
        [button.run() for button in py5.get_current_sketch().buttons]
        #print_coordinates(py5)
    
    py5.run_sketch()

class Selector(GUI_Element):
    pass

class Toggle(GUI_Element):
    pass

class Slider(GUI_Element):
    pass

class PrintZero:
    """Print zero: An extended print function.
       print0('my text', color=...) can be used as a print() function supporting colors.
       Awailable colors are: white, bright_white, cyan, red, yellow, green, blue, magenta
       
       A call to print0 can also be provided with a priority= and a topic=. If a priority is provided, only a
       print0() call that has a priority <= the priority_threshold or that has a topic among the string list of
       priority_topics will actually get printed.
       This enables using different levels and focus topics of debug information.
       For example print0('mytext', color='red', priority=1) can be used for an important alarm.
       The priority level goes from 1=most important to 3 or above=least important.
       
       You can print0.set_priority_threshold(number) and print0.set_priority_topics(['connection', 'user', ...])
       to define the priority_threshold and priority_topics."""
    
    def __init__(self):
        self.priority_threshold = 2
        self.priority_topics = []
        #Any call to os.system enables printing colors in the command prompt afterwards
        os.system('')
        self.styles = {'white': '\033[37m',
                       'bright_white': '\033[97m',
                       'cyan': '\033[96m',
                       'red': '\033[91m',
                       'yellow': '\033[33m',
                       'green': '\033[92m',
                       'blue': '\033[94m',
                       'magenta': '\033[95m',
                       'reset': '\033[0m'}

    def set_priority_threshold(self, threshold:int):
        """Only print0() with priority <= threshold will be printed"""
        self.priority_threshold = threshold
        return self

    def set_priority_topics(self, topics:tuple|list):
        self.priority_topics = topics
        return self

    def __call__(self, text:str, color:str='white', priority:int=0, topic:str=None):
        if priority <= self.priority_threshold or topic in self.priority_topics:
            print(f'{self.styles[color]}{text}{self.styles["reset"]}')

print0 = PrintZero()