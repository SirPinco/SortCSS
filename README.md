# SortCSS <sub><sup>v2.1</sup></sub>
A small script useful if you have a lot of css-like files to sort. 
*It works, but don't rely on it.*

The sorting is done by following a template with a specific format (see [Template Guidelines](#template-guidelines)) and
applying it to original file.

## Features
- **Bulk targets:** Target specific files or whole directories, the script will search for valid files on its own. Recursion is supported.
- **Exclusions:** Exclude specific files or whole directories from the search.
- **Prefix:** Define a filename prefix for the newly sorted files.
- **Force overwrite:** If you blindly trust this script you can choose to sort the files in place by overwriting the original with the sorted copy.

## Arguments
| flag                      | description                                                  | default (no flag)                                            | default (flag only)                                          |
| ------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- | ------------------------------------------------------------ |
| `template` *              | The filepath of the template.                                | -                                                            | -                                                            |
| `-s`, <br />`--source`    | Source directory where to look for targets.                  | `/script_directory/`                                         | Error                                                        |
| `-d`, <br />`--ouput-dir` | Output directory where to write sorted files.                | Same as original file.                                       | `/script_directory/sorted/`                                  |
| `-t`, <br />`--target`    | Target specific files or directories. Affected by `--recursive`. | All files in `--source`. <br />Recursion depends on --recursive. | All files in --source. <br />Recursion depends on `--recursive`. |
| `-x`, <br />`--exclude`   | Exclude specified files or directories.                      | None                                                         | None                                                         |
| `-p`, <br />`--prefix`    | Add a prefix to the sorted file name.                        | `sorted_`                                                    | Original file name                                           |
| `-f`, <br />`--force`     | Overwrite files without asking.                              | False                                                        | True                                                         |
| `-r`, <br />`--recursive` | Allows the script to search for targets recursively. See `--target`. | False                                                | True                                                         |
| `-v`, <br />`--version`   | Shows the script version.                                    | -                                                            | -                                                            |

<sup>* positional, mandatory</sup>

> **BEWARE:** when using `--output-dir` you are writing all files into the same directory which means that if you have 
> targets with the same name but in different directories they will conflict with each other. [#1][i1]

## Template guidelines
1. The section title enclosed in brackets must not have an empty line under it, the attribute list must follow it immediately.
2. At least one empty line must follow the end of the attribute list, the empty line acts as the End-Of-Section.
3. The attribute name must be the first word in the line, everything else is considered the description.
   - *Attributes are indexed in descending order (`first-attribute=0, ..., nth-attribute=N`).*
4. The file extension for a template is `.scs`.

Pseudo template:
```
# Comment, lorem ipsum dolor sit amet

[ Section1 Title]
attribute1                  description
# Comment, lorem ipsum 
attribute2                  description
...
attributeN                  description

[ Section2 Title]
attributeN                  description
attributeN+1                description
...
attributeN+M                description

...
```

A template is included in the project files: [base_template.scs](https://github.com/SirPinco/SortCSS/blob/master/base_template.scs)

## Roadmap ✖ `v2.1`
- [X] [#2][i2] - `--source` doesn't influence target search if used with `--target`.
- [X] [#3][i3] - `list.append()` and `list.extend()` are being used interchangeably.
- [X] [#4][i4] - Private/member variables should have an identifying prefix to avoid conflicts.

## Roadmap ✖ `v2.5`
- [ ] [#6][i6] - Block should be a class.

[i1]: https://github.com/SirPinco/SortCSS/issues/1
[i2]: https://github.com/SirPinco/SortCSS/issues/2
[i3]: https://github.com/SirPinco/SortCSS/issues/3
[i4]: https://github.com/SirPinco/SortCSS/issues/4
[i6]: https://github.com/SirPinco/SortCSS/issues/6
