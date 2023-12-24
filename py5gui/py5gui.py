import os
from .utils.plot import Plot, legend    # the relative . is important for a pip install to find modules (from py5gui.utils.plot import... would also work)
import time

font_loaded, font = False, None

def remap(value, inFrom, inTo, outFrom, outTo):
    if inFrom == inTo:
        # special case where in-values are the same => remap() would zero divide => broadcast center as result
        return (value*0) + ((outFrom + outTo)/2)
    return outFrom + (outTo - outFrom) * ((value - inFrom) / (inTo - inFrom))

class Element:
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

        global font_loaded, font
        if not font_loaded:
            # only create and load the font the first time it is needed
            font_path = os.path.abspath(os.path.join(__file__, '..', 'fonts', 'roboto',  'Roboto-Regular.ttf'))
            font = py5.create_font(font_path, 12)
            font_loaded = True
        self.font = font
        font_loaded = True
        
    def mouse_in(self):
        return True if self.p.mouse_x > self.x and self.p.mouse_x < self.x+self.w and \
               self.p.mouse_y > self.y and self.p.mouse_y < self.y+self.h else False
               
    def set_style(self, highlight=False, pressed=False, align_left=False):
        self.p.stroke(*self.pressed_stroke) if pressed else self.p.stroke(*self.stroke)
        self.p.fill(*self.highlight_fill) if highlight else self.p.fill(0)
        self.p.stroke_weight(self.stroke_weight)
        self.p.text_font(self.font)
        self.p.rect_mode(self.p.CENTER)
        if align_left:
            self.p.text_align(self.p.LEFT, self.p.CENTER)
        else:
            self.p.text_align(self.p.CENTER, self.p.CENTER)
        
    def set_text_style(self):
        self.p.fill(*self.text_fill);   self.p.stroke(*self.text_stroke)

class Button(Element):
    def __init__(self, on_click=None, func_args=None, func_kwargs=None, **kwargs):
        """You can provide a function to be triggered by this button with on_click."""
        w = kwargs['py5'].text_width(kwargs['label']) + 30
        self.func_args, self.func_kwargs = func_args, func_kwargs
        super().__init__(**kwargs, w=w)

        self.on_click = on_click
        self.prev_mouse_pressed = False
    
    def run(self):
        mouse_in = self.mouse_in()
        
        pressed = False
        if mouse_in and self.p.is_mouse_pressed:
            pressed = True
            if not self.prev_mouse_pressed:
                self.on_click( *(self.func_args if self.func_args else ()),
                                  **(self.func_kwargs if self.func_kwargs else {}))
        
        with self.p.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed)
            self.p.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            self.p.text(self.label, self.center[0], self.center[1])
        
        self.prev_mouse_pressed = self.p.is_mouse_pressed

# class Slider(object):
#     # TODO: turn this basic class into a Element
#     def __init__(self, leftCoord, topCoord, min, max, value=None):
#         if value == None:
#             self.value = (max + min) / 2
#         else:
#             self.value = value
#         self.leftCoord=leftCoord; self.topCoord=topCoord; self.min=min; self.max=max
#         self.w = 80; self.h=8
#         self.isDragged = False
        
#     def run(self):
#         py5.push_style()
#         py5.fill(127);  py5.no_stroke()
#         py5.rect(self.leftCoord, self.topCoord, self.w, self.h, 4)   #radius=4
#         py5.ellipse_mode(py5.CENTER)
#         py5.stroke(255);    py5.fill(64)
#         elliPos = py5.remap(self.value, self.min, self.max, 
#                             self.leftCoord, self.leftCoord+self.w)
#         py5.ellipse(elliPos, self.topCoord + self.h/2, 22, 22)
#         if(not self.isDragged and py5.is_mouse_pressed):
#             if(py5.mouse_x >= self.leftCoord and py5.mouse_x <= self.leftCoord + self.w and
#                py5.mouse_y >= self.topCoord-10 and py5.mouse_y <= self.topCoord + 24):
#                 self.isDragged = True
#         if(self.isDragged and not py5.is_mouse_pressed):
#             self.isDragged = False
#         if(self.isDragged):
#             newVal = py5.remap(py5.mouse_x, self.leftCoord, self.leftCoord + self.w,
#                                self.min, self.max)
#             self.value = py5.constrain(newVal, self.min, self.max)
#         py5.pop_style()
#         #print(f'current value: {self.value}')

class Text_Input(Element):
    def __init__(self, w=150, execute_func=None, func_args=None, func_kwargs=None, **kwargs):
        """A minimal text input field. Click to select and write a text input.
        Please note that the writing speed is limited by the set framerate, 
        which typically will be below accustomed keyboard writing speed.
        You can provide a function to be triggered when pressing enter with execute_func.
        This function will receive the written input text as its first argument"""
        super().__init__(**kwargs, w=w)
        self.active = False
        self.input = ''
        self.prev_key_pressed = False, False
        self.execute_func, self.func_args, self.func_kwargs = execute_func, func_args, func_kwargs

    def run(self):
        mouse_in = self.mouse_in()
        pressed = False
        if self.p.is_mouse_pressed:
            if mouse_in: 
                pressed = True
                self.active = True
            else:
                self.active = False
        
        if self.active:
            if not self.prev_key_pressed and self.p.is_key_pressed:
                if self.p.key == '\n':
                    if self.execute_func != None:
                        self.execute_func(self.input, *(self.func_args if self.func_args else ()),
                                                     **(self.func_kwargs if self.func_kwargs else {}))
                elif self.p.key_code == 8:
                    self.input = self.input[:-1]
                else:
                    self.input += self.p.key
        
        with self.p.push_style():
            self.set_style(highlight=mouse_in, pressed=pressed, align_left=True)
            self.p.rect(self.center[0], self.center[1], 
                        self.w-self.stroke_weight, self.h-self.stroke_weight)
            self.set_text_style()
            if self.input == '':
                if not self.active:
                    self.p.fill(127)
                    self.p.text('enter input', self.x+7, self.center[1])
            else:
                blink = '|' if time.time() % 2 > 1.0 and self.active else ''
                self.p.rect_mode(self.p.CORNER)
                self.p.text(self.input + blink, self.x+7, self.y, self.w-15, self.h)
        
        self.prev_key_pressed = self.p.is_key_pressed

    def get_input(self):
        return self.input

class Col:
    def __init__(self, py5=None, pos=(0,0), w=None, h=None):
        self.p = py5
        self.pos = pos
        self.w = py5.width if not w else 400
        self.h = py5.height if not h else 400
        self.elements = []

    def run(self):
        for element in self.elements:
            element.run()

    def add(self, element:Element):
        self.elements.append(element)

    def organize(self):
        pass    # TODO space elements upon __exit__()


class Selector(Element):
    pass

class Toggle(Element):
    pass

def print_coordinates(py5=None):
    """"print the currently moused over coordinates"""
    print(f'x: {py5.mouse_x} y: {py5.mouse_y}')

if __name__ == '__main__':
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