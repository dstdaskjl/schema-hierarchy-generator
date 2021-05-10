from PIL import ImageFont
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Line, Color, Rectangle
from kivy.storage.dictstore import DictStore
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from schema import *


TIMEOUT = 1


def schedule(timeout):
    def decorate(func):
        def wrap(*args):
            Clock.schedule_once(callback=lambda *_: func(*args), timeout=timeout)
        return wrap
    return decorate


class Tree(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        lines = File(DictStore(filename='shared_var').get(key='args')['file_path']).get()
        self.struct = Struct(lines)
        self.tree_map = dict()  # name : button_widget
        self.timeout = 1  # Line UI creation timeout

    def on_release_search_item_button(self, item_button):
        schema_name = item_button.text
        schema = self.struct.get_schema_by_name(schema_name)
        family = self.struct.get_family_by_schema(schema)

        self._show_tree()
        self._add_gridlayouts_to_tree(count=family.get_max_depth() + 1)
        self._add_buttons_to_tree(schema, family)
        self._center_layouts()
        self._add_lines_to_tree(schema)

    @schedule(timeout=TIMEOUT)
    def _center_layouts(self):
        max_width = self.ids.tree_layout.width
        for layout in self.ids.tree_layout.children:
            left_padding = (max_width - layout.width) / 2
            layout.padding = (left_padding, 0, 0, 0)



    def on_release_tree_node(self, name):
        schema = self.struct.get_schema_by_name(name)
        description = str()

        # Type
        if schema.types:
            description += 'Types\n'
            for type in schema.types:
                description += '        ' + type + '\n'
            description += '\n\n'

        # Description
        for key, value in schema.descriptions.items():
            description += key.capitalize() + '\n'
            for item in value:
                description += '        ' + item + '\n'
            description += '\n\n'

        # Open popup
        popup = Factory.CustomPopup()
        popup.title = name
        popup.description = description
        popup.open()

    def on_text_search_input(self, text_input):
        if self._search_input_is_valid(text_input):
            search_result = self._get_schemas_by_keyword(text_input.text.lower())
            search_result.sort()
            self._set_search_result(search_result)

    def _add_gridlayouts_to_tree(self, count):
        for _ in range(count):
            gridlayout = GridLayout(rows=1, size_hint=(None, None), height=40, pos_hint={'x': 0, 'y': 0})
            gridlayout.width = gridlayout.minimum_width
            gridlayout.spacing = 10
            self.ids.tree_layout.add_widget(gridlayout)

    def _add_button_to_tree(self, level, name, center):
        layout = self.ids.tree_layout.children[level]
        short_name = name[name.find(' ') + 1: -1]
        button = Button(
            text=short_name,
            font_name='Montserrat-Medium.ttf',
            font_size=20,
            color=(0,0,0,1),
            background_normal='',
            background_color=(1,1,0,1) if center else (0,0,0,0),
            size_hint=(None, 1),
            width=ImageFont.truetype(font='Montserrat-Medium.ttf', size=20).getlength(text=short_name) + 20,
            pos_hint={'x': 0, 'y': 0},
            on_release=lambda *_: self.on_release_tree_node(name=name)
        )
        layout.add_widget(button)
        layout.width = sum([widget.width for widget in layout.children]) + (layout.spacing[0] * (len(layout.children) - 1))
        self.tree_map[name] = button

    def _add_buttons_to_tree(self, schema, family):
        self.tree_map = dict()
        for member in family.members:
            self._add_button_to_tree(
                level=family.get_max_depth() - member.depth,
                name=member.name,
                center=member.name == schema.name
            )

    @schedule(timeout=TIMEOUT * 2)
    def _add_lines_to_tree(self, schema):
        self._add_line_to_parents(schema)
        self._add_line_to_children(schema)

    def _add_line_to_parents(self, schema):
        if schema.parents:
            my_point = self._get_center_point_by_name(schema.name)
            for parent in schema.parents:
                parent_point = self._get_center_point_by_name(parent.name)
                with self.tree_map[schema.name].canvas:
                    Color(rgba=[0,0,0,1])
                    Line(points=[my_point[0], my_point[1] + 20, parent_point[0], parent_point[1] - 20], width=1)
                self._add_line_to_parents(schema=parent)

    def _add_line_to_children(self, schema):
        if schema.children:
            my_point = self._get_center_point_by_name(schema.name)
            for child in schema.children:
                child_point = self._get_center_point_by_name(child.name)
                with self.tree_map[schema.name].canvas:
                    Color(rgba=[0,0,0,1])
                    Line(points=[my_point[0], my_point[1] - 20, child_point[0], child_point[1] + 20], width=1)
                self._add_line_to_children(schema=child)

    def _get_center_point_by_name(self, name):
        button = self.tree_map[name]
        x = button.x + button.width / 2
        y = button.y + button.height / 2
        return x, y

    def _get_schemas_by_keyword(self, keyword):
        search_result = list()
        for schema in self.struct.schemas:
            if keyword in schema.name:
                search_result.append(schema.name)
        return search_result

    def _search_input_is_valid(self, text_input):
        text = text_input.text.lower()
        if not text:
            return False
        if text == ' ' or text[-1] == '\t':
            text_input.text = text[:-1]
            return False
        return True

    def _set_search_result(self, search_result: list):
        self.ids.search_result.clear_widgets()
        for item in search_result:
            button = Button(
                text=item,
                color=(0, 0, 0, 1),
                font_size=20,
                background_normal='',
                background_color=(0, 0, 0, 0),
                size_hint=(1, None),
                height=100,
                pos_hint={'x': 0, 'y': 0},
                on_release=lambda *bound_args: self.on_release_search_item_button(bound_args[0])
            )
            self.ids.search_result.add_widget(button)

    def _show_tree(self):
        self.ids.search.pos_hint = {'x': 1, 'y': 0}
        self.ids.search_input.text = ''
        self.ids.search_result.clear_widgets()
        self.ids.tree_layout.clear_widgets()
        self.ids.tree.pos_hint = {'x': 0, 'y': 0}

    def _sort_family_by_height(self, family):
        sorted_family = list()
        for member in family:
            if not sorted_family:
                sorted_family.append(member)
            else:
                for i in range(len(sorted_family)):
                    if member.height >= sorted_family[i].height:
                        sorted_family.insert(i, member)
                        break
                if member not in sorted_family:
                    sorted_family.append(member)
        return sorted_family