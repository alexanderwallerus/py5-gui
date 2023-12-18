from threading import Thread

from pynput.keyboard import Key, Listener

keys = ''

def on_press(key):
    global keys

    try:
        # print(key.char) # alphanumeric key
        try:
            keys += key.char
        except TypeError as e:
            pass
        print(keys)
    except AttributeError:
        # print(key)
        if key == Key.space:
            keys += ' ' 
        elif key == Key.backspace:
            keys = keys[:-1]
        elif key == Key.enter:
            print('enter')
        print(keys)

def readKeyboard():
  with Listener(on_press=on_press) as listener:
      listener.join()

Thread(target=readKeyboard, daemon=True).start()

# keeping visible true may provide a higher more stable framerate at the cost of more cpu compute - one core maxed out. py5.HIDDEN actually seems even worse in performance
import py5
a = []
def setup():
    py5.size(200, 200)#, py5.HIDDEN)
    py5.window_move(-50_000, 0)
    # py5.get_surface().set_visible(False)
    py5.frame_rate(10_000)

def draw():
    a.append(py5.get_frame_rate())
    if py5.frame_count % 5_000 == 0:
        print(py5.get_frame_rate())
        py5.background(0)
        py5.fill(255)
        py5.text(py5.get_frame_rate(), 20, 20)

    if py5.key == 'q':
        py5.exit_sketch()

py5.run_sketch(block=True)
