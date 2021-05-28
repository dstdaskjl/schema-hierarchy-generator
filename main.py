import argparse, sys
parser = argparse.ArgumentParser(description='Schema hierarchy generator parser')
parser.add_argument('-p', type=str, required=True, help='Schema file path')
parser.add_argument('-f', type=int, required=False, help='Font size. 20 by default')
parser.add_argument('-s', type=int, required=False, help='Spacing between levels. 100 by default')
args = parser.parse_args()
sys.argv = [sys.argv[0]]


from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'fullscreen', 'False')


from hierarchy import Hierarchy
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang.builder import Builder
Builder.load_file('hierarchy.kv')
screen_manager = ScreenManager(transition=NoTransition())
screen_manager.add_widget(screen=Hierarchy(args, name='hierarchy'))


from kivy.app import App
from kivy.logger import Logger


class Application(App):
    def build(self):
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