# import argparse, sys
# parser = argparse.ArgumentParser(description='Drop-Down List Parser')
# parser.add_argument('-u', type=str, required=True, help='URL for files')
# args = parser.parse_args()
# sys.argv = [sys.argv[0]]
#
# url = args.u


from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'fullscreen', 'False')

from tree import Tree
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang.builder import Builder
Builder.load_file('tree.kv')
screen_manager = ScreenManager(transition=NoTransition())
screen_manager.add_widget(screen=Tree(name='tree'))

from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger

class Application(App):
    def build(self):
        # Window.bind(mouse_pos=lambda w, p: print(p))
        return screen_manager

def main():
    try:
        Application().run()
    except (KeyboardInterrupt, SystemExit):
        Logger.exception(msg='Exception:')
    finally:
        Logger.info(msg='Exit: HMI has been closed')

if __name__ == '__main__':
    main()