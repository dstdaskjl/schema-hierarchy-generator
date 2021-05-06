class DFS:
    stack = 0

    def __init__(self):
        DFS.stack = 0

    def get_depth(self, node, depth):
        if not node.parents:
            if depth > DFS.stack:
                DFS.stack = depth
        else:
            for parent in node.parents:
                self.get_depth(parent, depth + 1)
        return DFS.stack

    def get_height(self, node, height):
        if not node.children:
            if height > DFS.stack:
                DFS.stack = height
        else:
            for child in node.children:
                self.get_height(child, height + 1)
        return DFS.stack


class File:
    def __init__(self, filePath):
        self.filePath = filePath

    def get(self):
        with open(self.filePath, 'r') as infile:
            lines = infile.readlines()
        lines = list(map(self._remove_comments, lines))
        lines = list(map(str.strip, lines))
        lines = list(map(lambda s: s.replace('  ', ''), lines))
        lines = list(filter(None, lines))
        lines = self._remove_linebreaks(lines)
        return lines

    def _remove_comments(self, line):
        if ';' in line:
            line = line[:line.find(';')]
        return line

    def _remove_linebreaks(self, lines):
        newLines = list()
        for line in lines:
            if line[:len('obj-schema')] == 'obj-schema' or line[:1] in {':', '!', '?'}:
                newLines.append(line)
            else:
                if newLines[-1][:1] in {'!', '?'}:
                    newLines[-1] += ' ' + line
                else:
                    newLines.append(line)
        return newLines


class Schema:
    def __init__(self, name):
        self.name = name
        self.types = list()
        self.descriptions = dict()
        self.parents = list()
        self.children = list()
        self.depth = 0
        self.height = 0

    def find_depth(self):
        self.depth = DFS().get_depth(node=self, depth=0)

    def find_height(self):
        self.height = DFS().get_height(node=self, height=0)

    def get_parent_names(self):
        names = list()
        blood_type = self.name[2]
        for type in self.types:
            idx = type.find('?')
            if type[idx + 1: idx + 2] == blood_type:
                names.append(type[idx - 1:])
        return names

    def move_types(self):
        types = self.descriptions['types']
        self.types = types
        del self.descriptions['types']


class Struct:
    def __init__(self, lines):
        self.lines = lines
        self.schemas = list()
        self.roots = list()

    def get(self):
        self._set_schema()
        [schema.move_types() for schema in self.schemas]
        self._make_family()
        self._find_depth()
        self._find_height()
        return self

    def get_max_depth(self):
        max = 0
        for schema in self.schemas:
            if schema.stack > max:
                max = schema.stack
        return max

    def search_by_name(self, name):
        for schema in self.schemas:
            if schema.name == name:
                return schema

    def _find_depth(self):
        for schema in self.schemas:
            schema.find_depth()

    def _find_height(self):
        for schema in self.schemas:
            schema.find_height()

    def _make_family(self):
        for schema in self.schemas:
            self._set_relationship(schema)
        for schema in self.schemas:
            if not schema.parents:
                self.roots.append(schema)

    def _set_relationship(self, schema):
        parent_names = schema.get_parent_names()
        for parent_name in parent_names:
            for potential_parent in self.schemas:
                if potential_parent.name == parent_name:
                    schema.parents.append(potential_parent)
                    potential_parent.children.append(schema)
                    break

    def _set_schema(self):
        schema = None
        key = str()

        for line in self.lines:
            if line[:len('obj-schema')] == 'obj-schema':
                schema = Schema(name=line[line.find('('):])
                self.schemas.append(schema)

            elif line[:1] == ':':
                key = line[1:]
                schema.descriptions[key] = list()

            else:
                if line[:1] in {'!', '?'}:
                    schema.descriptions[key].append(line[line.find('('):])
                else:
                    schema.descriptions[key].append(line)


