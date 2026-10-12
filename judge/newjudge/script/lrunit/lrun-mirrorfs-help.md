lrun-mirrorfs




```bash

Mirror some parts of current filesystem for chroot purpose.

Usage:
  mirrorfs [--verbose] [--dry-run] --name $name --setup $config-path
  mirrorfs [--verbose] [--dry-run] --name $name --teardown $config-path
  mirrorfs --list
  mirrorfs --help
  mirrorfs --version

Config file is consist of multiple lines, each line can be:
  - mkdir $path
    mkdir -p $dest/$path
    the directory will be owned by root:root and have mode 0555.
  - touch $path
    create an empty file at $dest/$path
  - mirror $path
    mount --bind $path $dest/$path -o ro
    if $path is a directory, it must end with '/'
    $path can also be a glob pattern (ex. "foo-*.{c,cc}")

Notes:
  - $dest will be /run/lrun/mirrorfs/$name
  - if $path does not exist (or glob pattern matches nothing),
    it will be ignored but a warning will be printed.
  - if $path is (or matches) a symbol link, an equivalent symbol
    link will be created.
  - $dest will be printed if --setup completes without errors
```
