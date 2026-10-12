# Interactive judging

`linteractive` compiles a contestant and an interactor separately, connects their
standard streams with two pipes, and runs one pair of processes per testcase.
The two programs use their own language configuration and working directory.

Language support comes from the same `--etc-dir` profiles as `ljudge`, including
interpreters and multi-file compiler output. An optional `run.stream.cmd_list`
overrides `run.cmd_list` for streaming protocols. The supplied `sh` override runs
`bash $src` directly; the old batch wrapper consumes stdin until EOF and creates
fixed files, so it cannot be used on live interactive pipes. Copy the new file
to `sh/run.stream.cmd_list` when updating an existing configuration directory.
The native ordinary judge keeps its existing batch command. Both judges accept
the profile's `--max-stack` option. JVM profiles using `$jvmmemory` also require
an explicit byte value, for example `--max-jvm-memory 268435456`.

## Build and runtime requirements

Build and install with `make && sudo make install` from the `ljudge` directory.
Both `ljudge` and `linteractive` are installed. A release build uses
`make clean && make NDEBUG=1`.

The real backend requires a configured `lrun`, `lrun-mirrorfs`, language toolchains
and a Linux kernel providing **cgroup v1 cpuacct, memory, devices and freezer**.
The bundled `lrun` has no cgroup v2 backend. A cgroup v2-only kernel cannot run
the real sandbox; WSL needs a kernel with the required v1 controllers enabled.
Container images alone cannot supply a controller absent from the host kernel.

Run `linteractive` as an unprivileged judge account after installing the sandbox
and setting its permissions as described in the existing installation guide.
Do not replace the sandbox with the test adapter when judging submissions.

## Invocation

```sh
linteractive \
  --etc-dir /etc/ljudge \
  --cache-dir /var/cache/ljudge \
  --solution-code contestant.cpp \
  --user-code interactor.cpp \
  --threads 1 --keep-stderr \
  --max-cpu-time 1 --max-real-time 3 --max-memory 128m \
  --max-checker-cpu-time 2 --max-checker-real-time 5 \
  --testcase --input case.in --output case.out
```

The flag names are historical: `--solution-code` is the **contestant** and
`--user-code` is the **interactor**. Place the limits before the corresponding
`--input`. Repeat `--testcase --input ... --output ...` for more test files.

The interactor is invoked with standard testlib arguments:

```text
interactor input transcript output
```

| Argument | testlib stream | Purpose |
| --- | --- | --- |
| `argv[1] = input` | `inf` | Read-only hidden input from `--input` |
| `argv[2] = transcript` | `tout` | Writable transcript, separately allocated for each testcase |
| `argv[3] = output` | `ans` | Read-only reference answer from `--output` |

The names are relative to the sandbox working directory, `/tmp`. The interactor
can use the normal entry point without constructing replacement arguments:

```cpp
#include "testlib.h"
#include <iostream>

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    int secret = inf.readInt();
    std::cout << 100 << std::endl;
    int guess = ouf.readInt();
    if (guess != secret) quitf(_wa, "incorrect guess");
    tout << guess << std::endl; // Optional: a record, not a reply to the contestant.
    quitf(_ok, "accepted");
}
```

The interactor's stdin (`ouf`) receives contestant output; its stdout (`cout`)
goes to contestant input. Both sides must flush before waiting for a reply.
The contestant does not receive the interactor's source, executable or data files
in its working directory. Both sandboxes disable networking by default.

`--output` is still required; supply an empty file if the interactor does not use
`ans`. An empty `tout` is valid. Each transcript is mounted writable over a
placeholder in the otherwise read-only interactor directory, so parallel cases
cannot share or truncate one another's records. Transcripts are temporary and
removed at the end of the invocation; they are not automatically passed to a
post-checker or returned as contestant stdout. `--max-checker-output` also limits
transcript file size.

The supplied configuration contains the unmodified official testlib 0.9.45 at
`etc/ljudge/_default/testlib.h`. `linteractive` stages the configured header beside
the interactor source before compiling it, so `#include "testlib.h"` works without
uploading a header. When updating an existing/custom `--etc-dir`, copy this file
to its `_default/testlib.h`; a language-specific `testlib.h` may override it.
Ordinary `ljudge` compilation and the legacy `include/testlib.h` are unchanged.
Legacy interactors that ignore command-line arguments and open `input`/`output`
continue to work.

## Verdicts and results

The interactor returns 0 for AC, 1 for WA, and 2 for PE. The contestant must also
exit successfully and stay within its limits for AC. Contestant crashes and
nonzero exits cannot produce AC. Contestant CPU/wall-time exhaustion produces TLE;
a missing flush can therefore produce TLE, without requiring a separate idle timer.
Memory and output limit reports produce MLE and OLE.

Interactor crashes, malformed/missing sandbox reports and unrecognized interactor
exit codes produce `INTERNAL_ERROR`. An interactor hitting its CPU, memory or
output limit is an internal failure. If the contestant has failed or exceeded a
limit while the interactor waits, that contestant failure takes precedence over
an interactor wall timeout. An interactor wall timeout after a successful contestant
exit is an internal failure. A contestant SIGPIPE following an explicit interactor
WA/PE preserves that rejection verdict.

Contestant limits use `--max-*`; interactor limits use `--max-checker-*`.
After both programs start, the parent closes all communication endpoints and waits
for both sandbox supervisors to exit, including their cleanup. A rejected session
may still take the other program's configured time limit to finish. Set finite
wall-time limits for both sides.

JSON has `userCompilation`, optional `judgeCompilation`, and `testcases` after
successful compilation. `--keep-stderr` returns separate `stderr` and `judgeStderr`
fields for each testcase. Stdout is the interaction channel, not an output-file
transcript. The response schema is `schema/interactive-response.json`, also printed
by `linteractive --json-schema`.

## Regression tests

Build `src/linteractive`, then run from `ljudge` on Linux:

```sh
sudo unshare --mount --propagation private -- \
  python3 test/interactive_test.py \
    --binary "$PWD/src/linteractive" \
    --output-dir /tmp/linteractive-results
```

The test uses only Python's standard library and g++. It runs trusted C++/Python
fixtures as UID/GID 65534, with real pipes, subprocess exits, signals and timeouts.
It injects `test/fake_lrun.py` into that test's PATH only. Mounts are private, and
test processes and temporary working directories are cleaned up.

These are **orchestration and verdict regression tests**, not acceptance tests of
the real sandbox. They cover AC/WA/PE, missing flush, crashes, nonzero exits,
interactor failures and independent limits, EOF, malformed status, startup failure,
cleanup completion, separate logs, C++/Python combinations, 30 sequential testcases
under a 64-FD limit, and 12 testcases with four workers. Results and backend evidence
are saved under `--output-dir`; the script exits nonzero on a failed expectation.

The official-testlib integration suite uses the real installed `lrun` and runs as
the dedicated non-root judge account:

```sh
python3 test/testlib_interaction_test.py \
    --binary "$PWD/src/linteractive" \
    --runtime "$PWD/../runtime" \
    --output-dir /tmp/linteractive-testlib-results
```

It checks the standard `registerInteraction(argc, argv)` entry point, `inf`/`ans`
read-only access, `tout` writes and output limits, empty answers, AC/WA/PE/TLE/IE,
Python contestants, transcript separation across sequential/parallel cases, and
the unmodified number-bomb example. Standalone compilation, normal/SPJ and
language-profile regressions are in `../tests/`; see `../TESTING.md`.

Verified on 2026-10-04 with kernel
`6.18.33.2-microsoft-standard-WSL2-memcg1`: all 11 real-lrun testlib integration
checks and all 24 orchestration regression checks passed. After installation,
the number-bomb sources using the unmodified registration call also passed a
six-round boundary testcase through `/usr/local/bin/linteractive`.
