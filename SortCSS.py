import argparse
import re
from pathlib import Path
from typing import List, Union

from pathvalidate import validate_filename, ValidationError, validate_filepath
from pathvalidate.argparse import validate_filepath_arg

_WORK_DIR_ = Path(__file__).parent
_OUTPUT_DIR_ = _WORK_DIR_ / 'sorted'
_SCRIPT_NAME_ = 'SortCSS'  # DO NOT CHANGE THIS, see CssTarget.sort()
_VERSION_ = 'v1.0.1'
_FILE_PREFIX_ = 'sorted_'
_TARGET_EXTENSIONS_ = ['.css', '.scss']
_TEMPLATE_EXTENSION_ = '.scs'

_AFFIRMATIVE_ = ['Y', 'YES', 'OK']
_NEGATIVE_ = ['N', 'NO']

arg_parser = argparse.ArgumentParser(
    description='''Simple attribute sorter for CSS files. The script doesn't rearrange the elements, it only sorts the attributes inside them.''',
    prog=_SCRIPT_NAME_)
arg_parser.add_argument('template', type=validate_filepath_arg, help='''set the reference CSS template/structure file.''')
arg_parser.add_argument('-s', '--source', type=validate_filepath_arg, default=_WORK_DIR_,
                        help='''source directory where to look for targets. Default=script directory.''')
arg_parser.add_argument('-d', '--output-dir', type=validate_filepath_arg, nargs='?', default=None, const=_OUTPUT_DIR_,
                        help='''output directory where to write sorted files. Default=original file location.''')
arg_parser.add_argument('-t', '--target', type=Path, nargs='*', default=[],
                        help='''target specific files or directories. Default=All files in --source but no directories.''')
arg_parser.add_argument('-x', '--exclude', type=Path, nargs='*', default=[],
                        help='''exclude specified files or directories. Default=None.''')
arg_parser.add_argument('-p', '--prefix', nargs='?', default='', const=_FILE_PREFIX_,
                        help='''set the prefix for the sorted file name, if not set it will keep the original name. Default=\'%s\'.''' % _FILE_PREFIX_)
arg_parser.add_argument('-f', '--force', action='store_true', help='overwrite target file without asking.')
arg_parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='look recursively into --source/--targets for valid target files.')
arg_parser.add_argument('--version', action='version', version='%(prog)s {}'.format(_VERSION_),
                        help='''show script version.''')

cmd_args = arg_parser.parse_args()


def validate_arguments():
    """
    One time utility used to group argument validation.
    """

    cmd_args.template = Path(cmd_args.template)

    if cmd_args.source:
        cmd_args.source = Path(cmd_args.source)

    if cmd_args.output_dir:
        cmd_args.output_dir = Path(cmd_args.output_dir)
        cmd_args.output_dir.mkdir(parents=True, exist_ok=True)

    if cmd_args.target:
        for t in cmd_args.target:

            if not t.is_file() and not t.is_dir():  # Check if targets are valid files or directories
                raise NotADirectoryError("Target not found: \'%s\'" % t)

    if cmd_args.exclude:
        for x in cmd_args.exclude:
            if not x.is_file() and not x.is_dir():  # Check if exclusions are valid files or directories
                raise NotADirectoryError("Target not found: \'%s\'" % x)

    try:
        validate_filename(cmd_args.prefix + 'test.css')  # Check if the prefix is valid for a filename
    except ValidationError as e:
        raise ValidationError("Prefix is not a valid filename: %s" % cmd_args.prefix, e)


def join_lists(separator: str, *args):
    """
    Utility used to apply str.join() behaviour to lists.

    :param separator: item to place between lists
    :param args: lists to join together
    :return: joined lists
    """

    m_joined = []

    for m_list in args:
        if m_list:
            m_joined.extend(m_list)

            # Could be .append() but since we are joining lists I prefer returning list[list] only,
            # instead of list[Union[list, str]]
            m_joined.extend(separator)
    m_joined.pop()

    return m_joined


def expand_items(items: Union[Path, List], recursive: bool = True):
    """
    Utility used to find all files with a valid extension (see _TARGET_EXTENSIONS_) inside the specified path, by default
    it looks recursively into directories.

    :param items: a file, directory or list of either. If a list it can contain both directories and files.
    :param recursive: if True it looks into directories if false it stays on top level.
    :return: list of files
    """

    m_all_items = []

    if type(items) is list:
        for item in items:
            if item.is_file() and item.suffix in _TARGET_EXTENSIONS_:
                m_all_items.append(item)
            elif item.is_dir():
                m_all_items.extend(expand_items(item, recursive))

    elif items.is_file() and items.suffix in _TARGET_EXTENSIONS_:
        m_all_items.append(items)

    elif items.is_dir():
        for extension in _TARGET_EXTENSIONS_:
            if recursive:
                m_all_items.extend([m_target for m_target in items.rglob('*' + extension)])
            else:
                m_all_items.extend([m_target for m_target in items.glob('*' + extension)])

    return m_all_items


def startup():
    """
    One time utility for startup duties such as validating arguments and gathering targets.
    It's a function for the sole purpose of making the script cleaner since we want to keep everything in a single file.
    """

    # Print pretty arguments
    m_arg_list = []
    for arg in vars(cmd_args):
        m_arg_list.append(arg + '=' + repr(getattr(cmd_args, arg)))
    print("Launched %s with args: [%s]" % (_SCRIPT_NAME_ + ' ' + _VERSION_,
                                           ', '.join(m_arg_list)))

    # Argument validation
    validate_arguments()

    # Convert targets and exclusions in useful list of files
    if cmd_args.exclude:
        m_exclude = []

        for x in expand_items(cmd_args.exclude, cmd_args.recursive):
            if x.is_absolute():
                m_exclude.append(x)
            else:
                m_exclude.append(cmd_args.source / x)

        cmd_args.exclude = m_exclude

    if cmd_args.target:  # If user specified targets look into them
        m_target = []

        for t in expand_items(cmd_args.target, cmd_args.recursive):
            if t.is_absolute():
                m_target.append(t)
            else:
                m_target.append(cmd_args.source / t)

        cmd_args.target = m_target

    else:
        try:  # If user didn't specify targets find all valid files in the source directory, recursion depends on --recursive
            cmd_args.target = [m_target for m_target in expand_items(cmd_args.source, recursive=cmd_args.recursive) if
                               m_target not in cmd_args.exclude]
        except TypeError:
            raise TypeError("No valid targets found, current supported extensions are {}".format(
                ', '.join(_TARGET_EXTENSIONS_))) from None


class CssTemplate:
    """
    Template that holds the attribute:index pairs based on a _TEMPLATE_EXTENSION_ file.
    """

    def __init__(self, file: Path):
        self.path = file
        self.template = self.__set_indexes()

        if not self.path.is_file() and self.path.suffix == _TEMPLATE_EXTENSION_:
            raise FileNotFoundError("Template file not found: \'%s\'" % self.path)

        # If the template has no entries something must be wrong, no sorting can be performed.
        if len(self.template) == 0:
            raise ImportError("Template file in the wrong format. No valid entries to sort with.")

    def __parse(self):
        """
        Parses a template file and turns it into a dictionary.

        TEMPLATE FILE STRUCTURE:
            # Comment, lorem ipsum dolor sit amet

            # Comment, lorem ipsum dolor sit amet
            [ Section Title]
            attribute1                  description
            # Comment, lorem ipsum dolor sit amet
            attribute2                  description
            ...
            attributeN                  description

        RULES:
        - The section title enclosed in brackets must not have an empty line under it, the attribute list must follow it immediately.
        - At least one empty line must follow the end of the attribute list, the empty line acts as the End-Of-Section.
        - The attribute name must be the first word in the line, everything else is considered the description.
        - Attributes are indexed in descending order. [first-attribute=0, nth-attribute=N, last-attribute=len(attribute_list)-1]

        :return: dictionary { section_titles:[attributes, ...], ... }
        """

        m_template = {}
        with self.path.open('r') as template_file:
            for line in template_file:
                section_title = re.search(r'(?<=\[ ).*?(?= ])', line)
                if section_title:
                    line = template_file.readline()  # Move to first attribute after section title
                    attribute_list = []
                    while line.strip():
                        if line[0] == '#':  # Skip line if comment
                            line = template_file.readline()
                            continue

                        attribute_list.append(line.split(' ', 1)[0].strip())
                        line = template_file.readline()

                    m_template[section_title.group()] = attribute_list

        return m_template

    def __set_indexes(self):
        """
        Set hierarchy of attributes by assigning and index to each one in ascending order (first:0, ..., nth:n-1)

        :return: dictionary {attribute1: 0, ..., attributeN: n-1}
        """

        m_index = 0
        m_indexed_template = {}
        for _, attributes in self.__parse().items():
            for attribute in attributes:
                m_indexed_template[attribute] = m_index
                m_index += 1

        return m_indexed_template

    def __repr__(self):
        return repr(self.template)


class CssTarget:
    """
    Represents a target file. It stores both a raw version of the file (line by line) and a condensed
    one (collapsed nested items).
    """

    def __init__(self, file: Path):
        self.path = file
        self.condensed = self.read()
        self.__raw = []

        if not self.path.is_file():
            raise FileNotFoundError("Target file not found: \'%s\'" % self.path)

    def read_block(self, raw_data: List = None, line_index: int = 0):
        """
        Recursive function used to parse blocks enclosed in curly braces. Collapses children into a single item.
        Parsing rules:
         - starting and closing braces must be on different lines
         - lines containing the starting and closing braces are included in the block
         - if the block contains a child the latter gets appended to the parent as a single line
            visualization: parent = [line, line, [line, line, line], line, line]
                                                    ^ child ^

        :param raw_data: lines where to look for the block
        :param line_index: current line, used for recursion
        :return: list of lines & line index of closing brace relative to raw_data
        """

        if not raw_data:
            raw_data = self.__raw

        m_index = line_index + 1
        m_block = [raw_data[line_index]]

        while m_index < len(raw_data):
            # Check if the line is the start of a block by looking for non balanced open braces
            if raw_data[m_index].count('{') > raw_data[m_index].count('}'):
                child, m_index = self.read_block(raw_data, m_index)  # Read the child
                m_block.append(child)
            # Check if the line is the end of a block by looking for non balanced closed braces
            elif raw_data[m_index].count('}') > raw_data[m_index].count('{'):
                m_block.append(raw_data[m_index])
                return m_block, m_index
            else:
                m_block.append(raw_data[m_index])  # This is where we append the actual normal content of the block

            m_index += 1

        return None

    def read(self):
        """
        Read the whole target file by iterating read_block() until EOF, collapsing blocks as single items.

        :return: list of lines with each block collapsed into one item
        """

        m_index = 0
        m_condensed = []

        with self.path.open('r') as target_file:
            self.__raw = target_file.readlines()  # Files will never be so big that memory runs out

        while m_index < len(self.__raw):  # Until EOF
            # Check if the line is the start of a block by looking for non balanced open braces
            if self.__raw[m_index].count('{') > self.__raw[m_index].count('}'):
                block, m_index = self.read_block(self.__raw, m_index)
                m_condensed.append(block)
            else:
                # This is where we read comments and non-block lines to keep the same overall format of the original file
                m_condensed.append(self.__raw[m_index])

            m_index += 1

        return m_condensed

    def load(self, file: Path):
        """
        Loads a file into an existing CssTarget by re-initializing it with the new file.
        :param file: new target file
        :return: self
        """

        self.__init__(file)
        return self

    def sort_block(self, block: List, template: CssTemplate):
        """
        Where the magic happens. Sorts the attributes by creating an empty copy of the template and inserting the
        block's attribute (with its value) into the corresponding slot according to the template, then removing all
        empty slots.

        Output block format (including newlines and spacing):
         selector (line with opening brace)
            attributes

            extras

            children
        end (line with closing brace)

        :param block: list of lines that contain the block
        :param template: CssTemplate to sort with
        :return: list of lines, sorted block
        """

        m_selector = []
        m_attributes = [None] * len(template.template)
        m_extras = []
        m_children = []
        m_end = None

        for item in block:
            if type(item) is str:
                if item.count('}') > item.count('{'):
                    m_end = [item]
                    break
                elif item.count('{') > item.count('}'):  # May be used in the future to sort selectors as well
                    m_selector = [item]
                else:
                    # Sorting happens here
                    key = item.split(':')[0].strip().strip('//')
                    if not key:
                        continue

                    elif key in template.template.keys():  # If attribute is in template
                        # Workaround, compiler expects attributes to be list[str] but it may also
                        # be list[Union[list[str], str]]
                        m_attributes[template.template[key]] = item if not m_attributes[template.template[key]] else [
                            m_attributes[template.template[key]], item]
                    else:
                        m_extras.append(item)  # If not an attribute

            elif type(item) is list:
                m_children.append(self.sort_block(item, template))

        # Remove all None items from dummy template effectively creating the sorted list of attributes
        m_attributes = [item for item in m_attributes if item is not None]

        if len(m_children) > 1:
            m_spaced_children = []
            for child in m_children:
                m_spaced_children.append(child)
                m_spaced_children.append('\n')
            m_spaced_children.pop()
            m_children = m_spaced_children

        return m_selector + join_lists('\n', m_attributes, m_extras, m_children) + m_end

    def sort(self, template: CssTemplate):
        """
        Sorts recursively every block in CssTarget by iterating read_block() until there are no more blocks to sort,
        includes children.

        :param template: CssTemplate to sort with
        :return: list of lines, sorted and ready to be written to file
        """

        m_sorted_raw = ['// %s %s\n' % (_SCRIPT_NAME_, _VERSION_)]

        for item in self.condensed:
            if type(item) is list:
                m_sorted_raw.append(self.sort_block(item, template))
            else:
                if type(item) is str and item.startswith('// %s v' % _SCRIPT_NAME_):
                    # Overwrite which version of the script sorted this file
                    continue

                m_sorted_raw.append(item)

        return m_sorted_raw


class CssSorted:
    """
    A sorted CssTarget, has all the necessary methods to make a CssTarget human readable and printable.
    """

    def __init__(self, unsorted: CssTarget, template: CssTemplate):
        self.sorted = unsorted.sort(template)
        self.raw = self.__expand()  # 'Roblox' haHAA

    def __expand_block(self, block: List):
        """
        Reverses CssTarget.read_block() by expanding the block, iterates recursively through its children.

        :param block: list of lines to expand
        :return: list of pure lines only, no nesting
        """

        m_expanded = []

        for item in block:
            if type(item) is str:
                m_expanded.append(item)
            elif type(item) is list:
                m_expanded.extend(self.__expand_block(item))

        return m_expanded

    def __expand(self):
        """
        Expands recursively every block in CssTarget by iterating __expand_block() until there are no more blocks to sort,
        includes children.

        :return: fully expanded sorted CssTarget, no nesting
        """

        m_expanded = []

        for item in self.sorted:
            m_expanded.extend(self.__expand_block(item))

        return m_expanded

    def write(self, file: Path):
        """
        Writes CssSorted to file. Asks for permission to overwrite --force flag is not set

        :param file: file to write in
        :return: filepath of created file
        """

        try:
            validate_filepath(file, platform='auto')
            with file.open('x') as sorted_file:
                sorted_file.writelines(self.raw)
        except FileExistsError:
            confirm = None

            while confirm not in _AFFIRMATIVE_ and confirm not in _NEGATIVE_:
                if not cmd_args.force:
                    confirm = input("Are you sure you want to overwrite \'%s\' with its sorted version? [Y/N]: "
                                    % file.name).upper()
                else:
                    # Force overwrite files if --force flag is set
                    confirm = True

                if confirm in _AFFIRMATIVE_:
                    with file.open('w') as sorted_file:
                        sorted_file.writelines(self.raw)
                elif confirm in _NEGATIVE_:
                    action = input("Specify a [new filename] or [abort]: ")
                    if action == 'abort' or action == '\n':
                        return None
                    else:
                        file = self.write(Path(action))
                else:
                    print("The available choices are %s or %s (not case sensitive)" % (_AFFIRMATIVE_, _NEGATIVE_))

            return file

        except ValidationError as e:
            print("Not a valid file path: \'%s\'" % file, e)


# --------------------------------------- #

startup()
c_template = CssTemplate(cmd_args.template)

for target in cmd_args.target:
    c_target = CssTarget(target)
    c_sorted = CssSorted(c_target, c_template)
    c_sorted.write((cmd_args.output_dir if cmd_args.output_dir else target.parent) / (cmd_args.prefix + target.name))
