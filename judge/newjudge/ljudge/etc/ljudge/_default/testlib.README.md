The adjacent `testlib.h` is the unmodified official testlib 0.9.45 header.

- Upstream: https://github.com/MikeMirzayanov/testlib
- Pinned commit: `1e4e8a24c79c6bad3becbdb5a332ffc352b7d5dd`
- Its license is included in the header.

`linteractive` copies this configured header beside the interactor source before
compilation. An interactor can use `#include "testlib.h"` and the normal
`registerInteraction(argc, argv)` entry point. Language-specific `testlib.h`
configuration overrides this default, using the existing config lookup rules.

This only changes interactor compilation. The legacy `include/testlib.h` and
ordinary `ljudge` checkers retain their existing behavior.
