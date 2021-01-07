# SortCSS

A small script useful if you have a lot of css-like files to sort. 
*It works, but don't rely on it.*

The sorting is done by following a template with a specific format (see Template Guidelines) and applying it to original file.

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
| `-r`, <br />`--recursive` | Allows the script to search for targets recursively. See `--target`. | False                                                        | True                                                         |
| `-v`, <br />`--version`   | Shows the script version.                                    | -                                                            | -                                                            |

[^]: * positional, mandatory

> **BEWARE:** when using `--output-dir` you are writing all files into the same directory which means that if you have targets with the same name but in different directories they will conflict with each other. #Issue

> **BEWARE:** as of version `v2.0`, `--source` and `--target` don't work together, `--target` paths are not relative to `--source`. #Issue



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

#### 

The template that I use -> base_template.scs