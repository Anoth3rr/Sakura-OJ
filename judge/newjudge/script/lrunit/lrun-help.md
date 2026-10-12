`
--reset-env       bool        Clean environment variables
`

```
lrun-mirrorfs --name 123 --setup compile.mirrorfs  --comment tt_compile
```


```
lrun --help
Run program with resources limited.

Usage: lrun [options] [--] command-args [3>stat]

Options:
  --max-cpu-time    seconds     Limit cpu time. `seconds` can be a floating-point number
  --max-real-time   seconds     Limit physical time
  --max-memory      bytes       Limit memory (+swap) usage. `bytes` supports common suffix like `k`, `m`, `g`
  --max-output      bytes       Limit output. Note: lrun will make a "best  effort" to enforce the limit but it is NOT accurate
  --max-rtprio      n           Set max realtime priority
  --max-nfile       n           Set max number of file descriptors
  --max-stack       bytes       Set max stack size per process
  --max-nprocess    n           Set RLIMIT_NPROC. Note: user namespace is not separated, current processes are counted
  --isolate-process bool        Isolate PID, IPC namespace
  --basic-devices   bool        Enable device whitelist: null, zero, full, random, urandom
  --remount-dev     bool        Remount /dev and create only basic device files in it (see --basic-device)
  --reset-env       bool        Clean environment variables
  --network         bool        Whether network access is permitted
  --pass-exitcode   bool        Discard lrun exit code, pass child process's exit code
  --chroot          path        Chroot to specified `path` before exec
  --umount-outside  bool        Umount everything outside the chroot path. This is not necessary but can help to hide mount information. Note: umount is SLOW
  --chdir           path        Chdir to specified `path` after chroot
  --nice            value       Add nice with specified `value`. Only root can use a negative value
  --umask           int         Set umask
  --uid             uid         Set uid (`uid` must > 0). Only root can use this
  --gid             gid         Set gid (`gid` must > 0). Only root can use this
  --no-new-privs    bool        Do not allow getting higher privileges using exec. This disables things like sudo, ping, etc. Only root can set it to false. Require
                                Linux >= 3.5
  --stdin-fd        int         Redirect child process stdin to specified fd
  --stdout-fd       int         Redirect child process stdout to specified fd
  --stderr-fd       int         Redirect child process stderr to specified fd
  --syscalls        syscalls    Apply a syscall filter.  `syscalls` is basically a list of syscall names separated by ',' with an optional prefix '!'. If prefix '!'
                                exists, it's a blacklist otherwise a whitelist. For full syntax of `syscalls`, see `--help-syscalls`. Conflicts with `--no-new-privs
                                false`
  --cgname          string      Specify cgroup name to use. The specified cgroup will be created on demand, and will not be deleted. If this option is not set, lrun
                                will pick an unique cgroup name and destroy it upon exit.
  --hostname        string      Specify a new hostname
  --interval        seconds     Set interval status update interval
  --debug                       Print debug messages
  --status                      Show realtime resource usage status
  --help                        Show this help
  --help-syscalls               Show full syntax of `syscalls`
  --help-fopen-filter           Show detailed help about fopen filter
  --version                     Show version information

Options that could be used multiple times:
  --bindfs          dest src    Bind `src` to `dest`. This is performed before chroot. You should have read permission on `src`
  --bindfs-ro       dest src    Like `--bindfs` but also make `dest` read-only
  --tmpfs           path bytes  Mount writable tmpfs to specified `path` to hide filesystem subtree. `size` is in bytes. If it is 0, mount read-only.  --fopen-filter
                                   cond action Do something when a file is opened. For details, see `--help-fopen-filter`
 This is performed after chroot. You should have write permission on `path`
  --env             key value   Set environment variable before exec
  --cgroup-option   subsys k v  Apply cgroup setting before exec. Only root can use this
  --fd              n           Do not close fd `n`
  --cmd             cmd         Execute system command after tmpfs mounted. Only root can use this
  --group           gid         Set additional groups. Applied to lrun itself. Only root can use this

Return value:
  - If lrun is unable to execute specified command, non-zero is returned and nothing will be written to fd 3
  - Otherwise, lrun will return 0 and output time, memory usage, exit status of executed command to fd 3
  - If `--pass-exitcode` is set to true, lrun will just pass exit code of the child process

Option processing order:
  --hostname, --fd, --umount-outside, (mount /proc), --bindfs, --bindfs-ro, --chroot, --tmpfs, --remount-dev, --fopen-filter, --chdir, --cmd, --umask, --gid, --uid,
  (rlimit options), --env, --nice, (cgroup limits), --syscalls

Default options:
  lrun --network true --basic-devices false --isolate-process true --remount-dev false --reset-env false --interval 0.02 --pass-exitcode false --no-new-privs true \
       --umount-outside false --max-nprocess 2048 --max-nfile 256 --max-rtprio 0 --nice 0
```