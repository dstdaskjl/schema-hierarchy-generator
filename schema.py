import copy


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

    def copy(self):
        copy_schema = Schema(self.name)
        copy_schema.types = copy.deepcopy(self.types)
        copy_schema.descriptions = copy.deepcopy(self.descriptions)
        return copy_schema

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
        if 'types' in self.descriptions:
            types = self.descriptions['types']
            self.types = types
            del self.descriptions['types']


class Struct:
    def __init__(self, lines):
        self.lines = lines
        self.schemas = self._get_schemas()
        self._set_relationships()

    def get_family_by_schema(self, schema):
        members = list()
        members.append(schema)
        self._get_children_by_schema(schema, members)
        self._get_parents_by_schema(schema, members)
        return Family(members)

    def get_schema_by_name(self, name):
        for schema in self.schemas:
            if schema.name == name:
                return schema

    def _get_children_by_schema(self, schema, family):
        if schema.children:
            for child in schema.children:
                if child not in family:
                    family.append(child)
                    self._get_children_by_schema(schema=child, family=family)

    def _get_parents_by_schema(self, schema, family):
        if schema.parents:
            for parent in schema.parents:
                if parent not in family:
                    family.append(parent)
                    self._get_parents_by_schema(schema=parent, family=family)

    def _get_schemas(self):
        schemas = self._get_schemas_from_lines()
        [schema.move_types() for schema in schemas]
        return schemas

    def _get_schemas_from_lines(self):
        schemas = list()
        schema = None
        key = str()

        for line in self.lines:
            if line[:len('obj-schema')] == 'obj-schema':
                schema = Schema(name=line[line.find('('):])
                schemas.append(schema)

            elif line[:1] == ':':
                key = line[1:]
                schema.descriptions[key] = list()

            else:
                if line[:1] in {'!', '?'}:
                    schema.descriptions[key].append(line[line.find('('):])
                else:
                    schema.descriptions[key].append(line)

        return schemas

    def _set_relationships(self):
        for schema in self.schemas:
            parent_names = schema.get_parent_names()
            for parent_name in parent_names:
                for potential_parent in self.schemas:
                    if potential_parent.name == parent_name:
                        schema.parents.append(potential_parent)
                        potential_parent.children.append(schema)
                        break


class Family:
    def __init__(self, members):
        self.members = [member.copy() for member in members]
        self._set_relationships()
        self._find_depth()
        self._find_height()
        self._sort()

    def get_max_depth(self):
        max = 0
        for member in self.members:
            if member.depth > max:
                max = member.depth
        return max

    def _balance_tree(self, groups):
        group_map = dict()
        for group in groups:
            if group[0].depth not in group_map:
                group_map[group[0].depth] = [group]
            else:
                group_map[group[0].depth].append(group)


        new_groups = list()
        d_groups = list(group_map.values())
        for d_group in d_groups:
            for i in range(len(d_group)):
                if i < int(len(d_group) / 2):
                    new_groups.append(list(reversed(d_group[i])))
                else:
                    new_groups.append(d_group[i])
        return new_groups

    def _find_depth(self):
        for member in self.members:
            member.find_depth()

    def _find_height(self):
        for member in self.members:
            member.find_height()

    def _group_by_depth(self, members):
        depth = -1
        groups = list()

        for member in members:
            if member.depth != depth:
                depth = member.depth
                groups.append(list())
            groups[-1].append(member)

        return groups

    def _group_by_parent(self, members):
        groups = list()
        used_members = set()
        parent_names = [name for member in members for name in member.get_parent_names()]
        for parent_name in parent_names:
            groups.append(list())
            for member in members:
                if member not in used_members and parent_name in member.get_parent_names():
                    groups[-1].append(member)
                    used_members.add(member)
        return list(filter(None, groups))

    def _set_relationships(self):
        for member in self.members:
            parent_names = member.get_parent_names()
            for parent_name in parent_names:
                for potential_parent in self.members:
                    if potential_parent.name == parent_name:
                        member.parents.append(potential_parent)
                        potential_parent.children.append(member)
                        break

    def _sort(self):
        sorted_members = self._sort_by_depth(self.members)
        sorted_groups = self._group_by_depth(sorted_members)
        sorted_groups = [self._sort_by_height(group) for group in sorted_groups]
        sorted_groups = [siblings for group in sorted_groups for siblings in self._group_by_parent(group)]
        # sorted_groups = self._balance_tree(sorted_groups)
        sorted_members = [member for siblings in sorted_groups for member in siblings]
        self.members = sorted_members

    def _sort_by_depth(self, members):
        sorted_members = list()
        for member in members:
            if not sorted_members:
                sorted_members.append(member)
            else:
                for i in range(len(sorted_members)):
                    if member.depth >= sorted_members[i].depth:
                        sorted_members.insert(i, member)
                        break
                if member not in sorted_members:
                    sorted_members.append(member)
        return sorted_members

    def _sort_by_height(self, members):
        sorted_members = list()
        for member in members:
            if not sorted_members:
                sorted_members.append(member)
            else:
                for i in range(len(sorted_members)):
                    if member.height >= sorted_members[i].height:
                        sorted_members.insert(i, member)
                        break
                if member not in sorted_members:
                    sorted_members.append(member)
        return sorted_members