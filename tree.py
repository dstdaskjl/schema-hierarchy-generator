from PIL import ImageFont
from kivy.clock import Clock
from kivy.graphics import Line, Color
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from schema import *


class Tree(Screen):
    def __init__(self, **kwargs):
        super(Tree, self).__init__(**kwargs)
        lines = File('obj-schemas.txt').get()
        self.struct = Struct(lines).get()
        self.tree_map = dict()

    def on_release_search_item_button(self, item_button):
        schema_name = item_button.text
        self.ids.search.pos_hint = {'x': 1, 'y': 0}
        self.ids.search_input.text = ''
        self.ids.search_result.clear_widgets()
        self.ids.tree_layout.clear_widgets()
        self.ids.tree.pos_hint = {'x': 0, 'y': 0}

        schema = self.struct.search_by_name(schema_name)
        family = self._get_family_by_schema(schema)
        family = self._sort_family_by_height(family)

        self.tree_map = dict()
        max_depth = self._get_max_depth(family)
        self._add_gridlayouts_to_treelayout(count=max_depth + 1)
        for member in family:
            color = (1,0,0,1) if member.name == schema_name else (0,0,0,1)
            self._add_button_to_tree(level=max_depth - member.depth, name=member.name, color=color)
        Clock.schedule_once(callback=lambda *_: self._add_lines_to_tree(schema), timeout=0.5)

    def on_text_search_input(self, text_input):
        if self._search_input_is_valid(text_input):
            search_result = self._get_schemas_by_keyword(text_input.text.lower())
            search_result.sort()
            self._set_search_result(search_result)

    def _add_gridlayouts_to_treelayout(self, count):
        for _ in range(count):
            gridlayout = GridLayout(rows=1, size_hint=(None, None), height=50, pos_hint={'x': 0, 'y': 0})
            gridlayout.width = gridlayout.minimum_width
            gridlayout.spacing = 10
            self.ids.tree_layout.add_widget(gridlayout)

    def _add_button_to_tree(self, level, name, color):
        layout = self.ids.tree_layout.children[level]
        short_name = name[name.find(' ') + 1 : -1]
        button = Button(
            text=short_name,
            font_name='Montserrat-Medium.ttf',
            font_size=20,
            color=color,
            background_normal='',
            size_hint=(None, 1),
            width=ImageFont.truetype(font='Montserrat-Medium.ttf', size=20).getlength(text=short_name) + 20, pos_hint={'x': 0, 'y': 0},
            on_release=lambda *_: self._create_popup(name=name)
        )
        layout.add_widget(button)
        layout.width = sum([widget.width for widget in layout.children]) + (layout.spacing[0] * (len(layout.children) - 1))
        self.tree_map[name] = button

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

    def _create_popup(self, name):
        schema = self.struct.search_by_name(name)
        description = str()
        description += 'Types:\n'
        for type in schema.types:
            description += '        ' + type + '\n\n'
        for key, value in schema.descriptions.items():
            description += key.capitalize() + ':\n'
            for item in value:
                description += '        ' + item + '\n'
            description += '\n'

        scrollview = ScrollView(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            do_scroll_x=True,
            do_scroll_y=True
        )
        gridlayout = GridLayout(
            size_hint=(None, 1),
            cols=1,
            rows=1
        )
        label = Label(text=description, size_hint=(None, 1), width=800)
        gridlayout.add_widget(label)
        gridlayout.minimum_width = gridlayout.minimum_width
        gridlayout.minimum_height = gridlayout.minimum_height
        Clock.schedule_once(lambda *_: print(gridlayout.width, gridlayout.height), timeout=1)

        scrollview.add_widget(gridlayout)

        popup = Popup(
            title=name,
            content=scrollview,
            size_hint=(0.8, 0.8)
        )
        popup.open()

    def _get_center_point_by_name(self, name):
        button = self.tree_map[name]
        x = button.x + button.width / 2
        y = button.y + button.height / 2
        return x, y

    def _get_family_by_schema(self, schema):
        family = list()
        family.append(schema)
        self._get_parents_by_schema(schema, family)
        self._get_children_by_schema(schema, family)
        return family

    def _get_parents_by_schema(self, schema, family):
        if schema.parents:
            for parent in schema.parents:
                if parent not in family:
                    family.append(parent)
                    self._get_parents_by_schema(schema=parent, family=family)

    def _get_children_by_schema(self, schema, family):
        if schema.children:
            for child in schema.children:
                if child not in family:
                    family.append(child)
                    self._get_children_by_schema(schema=child, family=family)

    def _get_max_depth(self, schemas):
        max = 0
        for schema in schemas:
            if schema.depth > max:
                max = schema.depth
        return max

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