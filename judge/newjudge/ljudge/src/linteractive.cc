#ifndef _GNU_SOURCE
# define _GNU_SOURCE
#endif

#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <csignal>
#include <cmath>
#include <dlfcn.h>
#include <fcntl.h>
#include <list>
#include <map>
#include <mutex>
#include <string>
#include <sstream>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#else
#warning OpenMP support is not detected. Threading will not work
#endif
#include <iostream>
#include <fstream>

#include "sha1.hpp"
#include "fs.hpp"
#include "term.hpp"
#include "deps/picojson/picojson.h"
#include "deps/tinyformat/tinyformat.h"

extern "C" {
#include "deps/log.h/log.h"
  int debug_level;
}

using std::list;
using std::map;
using std::string;
using std::vector;
using tfm::format;
namespace j = picojson;

#define fatal(...) { fprintf(stderr, __VA_ARGS__); fprintf(stderr, "\n"); cleanup_exit(1); }

#define LJUDGE_VERSION "v0.6.1"

// lrun-mirrorfs chroot path (lrun-mirrorfs --show-root)
#define CHROOT_BASE_DIR "/run/lrun/mirrorfs"

// truncate log size, ex. compiler log, stdout, stderr, etc.
#define TRUNC_LOG 265535

// sub-directory names in cache_dir
#define SUBDIR_USER_CODE "code"
#define SUBDIR_CHECKER "checker"
#define SUBDIR_TEMP "tmp"
#define SUBDIR_KERNEL_CONFIG_CACHE "kconfig"

// envs (config file name prefixes)
#define ENV_CHECK "check"
#define ENV_COMPILE "compile"
#define ENV_EXTRA "extra"
#define ENV_RUN "run"
#define ENV_VERSION "version"

// config file extensions
#define EXT_CMD_LIST ".cmd_list"
#define EXT_EXE_NAME ".exe_name"
#define EXT_MIRRRORFS ".mirrorfs"
#define EXT_LRUN_ARGS ".lrun_args"
#define EXT_NAME ".name"
#define EXT_OPT_FAKE_PASSWD "fake_passwd"
#define EXT_FS_OVERRIDE ".fs_override"
#define EXT_SRC_NAME ".src_name"
#define EXT_SOLUTION_NAME ".solution_name"

// config file names which are options
#define OPTION_VALUE_TRUE "true"
#define OPTION_VALUE_FALSE "false"

// default values
#define DEFAULT_EXE_NAME "a.out"
#define DEFAULT_CONF_DIR "_default"

#define DEV_NULL "/dev/null"
#define ETC_PASSWD "/etc/passwd"
#define PROC_CGROUP "/proc/cgroups"

namespace TestcaseResult {
/* [[[cog
  import cog
  for name in ['INTERNAL_ERROR', 'NON_ZERO_EXIT_CODE', 'MEMORY_LIMIT_EXCEEDED', 'TIME_LIMIT_EXCEEDED', 'OUTPUT_LIMIT_EXCEEDED', 'PRESENTATION_ERROR', 'ACCEPTED', 'RUNTIME_ERROR', 'FLOAT_POINT_EXCEPTION', 'SEGMENTATION_FAULT', 'WRONG_ANSWER']:
    cog.outl('const string %(name)s = "%(name)s";' % {'name': name})
]]] */
const string INTERNAL_ERROR = "INTERNAL_ERROR";
const string NON_ZERO_EXIT_CODE = "NON_ZERO_EXIT_CODE";
const string MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED";
const string TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED";
const string OUTPUT_LIMIT_EXCEEDED = "OUTPUT_LIMIT_EXCEEDED";
const string PRESENTATION_ERROR = "PRESENTATION_ERROR";
const string ACCEPTED = "ACCEPTED";
const string RUNTIME_ERROR = "RUNTIME_ERROR";
const string FLOAT_POINT_EXCEPTION = "FLOAT_POINT_EXCEPTION";
const string SEGMENTATION_FAULT = "SEGMENTATION_FAULT";
const string WRONG_ANSWER = "WRONG_ANSWER";
const string IDLENESS_LIMIT_EXCEED = "IDLENESS_LIMIT_EXCEED";
/* [[[end]]] */
};

struct Limit {
  double cpu_time;   // seconds
  double real_time;  // seconds
  long long memory;  // bytes
  long long output;  // bytes
  long long jvm_memory; //bytes
};

struct Testcase {
  string input_path;
  string output_path;
  string output_sha1;
  string output_pe_sha1;
  string user_stdout_path;
  string user_stderr_path;
  string slice_path;
  Limit runtime_limit;
  Limit checker_limit;
};

struct Options {
  string etc_dir;
  string cache_dir;
  string user_code_path;
  string checker_code_path;
  string solution_code_path;
  Limit compiler_limit;
  vector<Testcase> cases;
  map<string, string> envs;
  bool pretty_print;
  bool skip_checker;  // if true, do not run can checker, but capture user program's output
  bool keep_stdout;
  bool keep_stderr;
  bool direct_mode;  // if true, just run the program and prints the result
  int nthread;  // how many testcases can run in parallel. default is decided by omp (cpu cores
};

struct LrunArgs : public vector<string> {
  void append(const Limit& limit) {
    /* [[[cog
      import cog
      opts = {'cpu_time': 'g', 'real_time': 'g', 'output': 'Ld', 'memory': 'Ld'}
      for opt, flag in opts.items():
        cog.out(
          '''
          if (%(opt)s > 0) {
            push_back("--max-%(opt_m)s");
            push_back(format("%%%(flag)s", %(opt)s));
          }
          ''' % {'opt': 'limit.' + opt,
                 'opt_m': opt.replace('_', '-'),
                 'flag': flag}, trimblanklines=True)
    ]]] */
    if (limit.real_time > 0) {
      push_back("--max-real-time");
      push_back(format("%g", limit.real_time));
    }
    if (limit.cpu_time > 0) {
      push_back("--max-cpu-time");
      push_back(format("%g", limit.cpu_time));
    }
    if (limit.memory > 0) {
      push_back("--max-memory");
      push_back(format("%Ld", limit.memory));
    }
    if (limit.output > 0) {
      push_back("--max-output");
      push_back(format("%Ld", limit.output));
    }
    /* [[[end]]] */
  }

  void append(const string& arg1) {
    push_back(arg1);
  }

  void append(const string& arg1, const string& arg2) {
    push_back(arg1);
    push_back(arg2);
  }

  void append(const string& arg1, const string& arg2, const string& arg3) {
    push_back(arg1);
    push_back(arg2);
    push_back(arg3);
  }

  void append(const vector<string>& args) {
    insert(end(), args.begin(), args.end());
  }

  void append(const list<string>& args) {
    insert(end(), args.begin(), args.end());
  }

  void append_default() {
#ifndef NDEBUG
    if (getenv("LJUDGE_DEBUG_LRUN")) push_back("--debug");
#endif
    append("--reset-env", "true");
    append("--basic-devices", "true");
    append("--remount-dev", "true");
    append("--network", "false");
    append("--chdir", "/tmp");
    append("--env", "ONLINE_JUDGE", "1");
    append("--env", "HOME", "/tmp");
    append("--env", "PATH", "/usr/bin:/bin:/etc/alternatives:/usr/local/bin");
    // Pass as-is
    static const char pass_envs[][16] = {"JAVA_HOME"};
    for (size_t i = 0; i < sizeof(pass_envs) / sizeof(pass_envs[0]); ++i) {
      const char* env_val = getenv(pass_envs[i]);
      if (env_val) append("--env", pass_envs[i], env_val);
    }
  }
};

struct LrunResult {
  string error;
  long long memory;
  double cpu_time;
  double real_time;
  bool signaled;
  int exit_code;
  int term_sig;
  string exceed;
  pid_t pid;
  int pipe_fd;

  LrunResult() : memory(0), cpu_time(0), real_time(0), signaled(false),
                 exit_code(-1), term_sig(0), pid(-1), pipe_fd(-1) { }
};

struct CompileResult {
  string log;
  string error;
  bool success;
};

#ifdef _OPENMP
static std::map<string, omp_lock_t> omp_locks;
static omp_lock_t omp_locks_lock = omp_lock_t();

struct InitOmpLocksLock {
  InitOmpLocksLock() {
    omp_init_lock(&omp_locks_lock);
  }
} init_omp_locks_lock;

struct ScopedOMPLock {
  ScopedOMPLock(const string& name) {
    omp_set_lock(&omp_locks_lock);
    if (!omp_locks.count(name)) {
      omp_locks[name] = omp_lock_t();
      omp_init_lock(&omp_locks[name]);
    }
    plock_ = &omp_locks[name];
    omp_unset_lock(&omp_locks_lock);
    omp_set_lock(plock_);
  }
  ~ScopedOMPLock() {
    omp_unset_lock(plock_);
  }
  omp_lock_t* plock_;
};
#endif

string string_chomp(const string& str) {
  if (str.empty() || str[str.length() - 1] != '\n') return str;
  return str.substr(0, str.length() - 1);
}

vector<string> string_split(const string& str, const string& delim) {
  vector<string> result;
  if (delim.empty()) {
    result.push_back(str);
  } else {
    size_t pos = 0, start = 0;
    for (int running = 1; running;) {
      pos = str.find(delim, start);
      size_t len;
      if (pos == string::npos) {
        len = string::npos;
        running = 0;
      } else {
        len = pos - start;
      }
      result.push_back(str.substr(start, len));
      start = pos + delim.length();
    }
  }
  return result;
}

void string_replacei(string& str, const string& from, const string& to) {
  size_t pos = 0;
  while ((pos = str.find(from, pos)) != string::npos) {
    str.replace(pos, from.length(), to);
    pos += to.length();
  }
}

string which(const string& name, int access = R_OK | X_OK) {
  string result;
  char* path_env = getenv("PATH");
  if (path_env) {
    vector<string> dirs = string_split(path_env, ":");
    for (int i = 0; i < (int)dirs.size(); ++i) {
      string path = fs::join(dirs[i], name);
      if (fs::is_accessible(path, access)) {
        result = path;
        break;
      }
    }
  }
  return result;
}


static list<string> cleanup_paths;

void register_cleanup_path(const string& path) {
  if (path.empty()) return;
  cleanup_paths.push_back(path);
}

int cleanup_exit(int code) {
#ifndef NDEBUG
  if (!getenv("DEBUG") && !getenv("NOCLEANUP")) {
#endif
    for (__typeof(cleanup_paths.begin()) it = cleanup_paths.begin();
         it != cleanup_paths.end(); ++it) {
      string path = *it;
      if (!fs::exists(path)) continue;
      log_debug("cleaning: rm -rf %s", path.c_str());
      fs::rm_rf(path);
    }
#ifndef NDEBUG
  } else {
    log_debug("skip cleaning up");
  }
#endif
  exit(code);
}

void enforce_mkdir_p(const string& dir) {
  if (fs::mkdir_p(dir) < 0) fatal("cannot mkdir: %s", dir.c_str());
}

void load_libsegfault() {
  void* libSegFault = dlopen("libSegFault.so", RTLD_NOW);
  (void)libSegFault;
}


/**
 * Example:
 *   get_config_path("/etc/ljudge", "/path.to/bla.clang.cc", "foo")
 *
 *   returns "/etc/ljudge/clang.cc/foo"  # if it exists
 *   returns "/etc/ljudge/cc/foo"        # if it exists and the above one doesn't exist
 *   returns "/etc/ljudge/_default/foo"  # if it exists and the above two don't exist, and strit is false
 *   returns ""                          # if the above three don't exist
 */
static string get_config_path(const string& etc_dir, const string& code_path,
                              const string& config_name, bool strict = false) {
  string basename = fs::basename(code_path);
  log_debug("get_config_path: %s %s", config_name.c_str(), basename.c_str());
  //兼容v8js
  if (strncmp("mainv8.js", basename.c_str(), 9) == 0) {
    string path = fs::join(etc_dir, "v8js", config_name);
    if (fs::exists(path)) return path;
  }

  for (size_t pos = 0; (pos = basename.find('.', pos)) != string::npos; ) {
    string ext = basename.substr(++pos);
    string path = fs::join(etc_dir, ext, config_name);
    if (fs::exists(path)) return path;
  }
  if (!strict) {
    string path = fs::join(etc_dir, DEFAULT_CONF_DIR, config_name);
    if (fs::exists(path)) return path;
  }

  return "";
}

/**
 * Example:
 *   cat /etc/ljudge/cc/cmd.compile
 *   # comment line
 *   g++
 *   -Wall
 *   $src
 *   -o
 *   $dest
 *
 *   get_config_list("/etc/ljudge", "/path.to/foo.cc", "cmd.compile")
 *   returns {"g++", "-Wall", "$src", "-o", "$dest"}
 *
 *   get_config_list("/etc/ljudge", "/path.to/foo.cc", "notfound")
 *   returns {}
 */
static list<string> get_config_list(const string& etc_dir,
                                    const string& code_path, const string& name, bool strict = false) {
  string path = get_config_path(etc_dir, code_path, name, strict);
  log_debug("get_config_list: %s", path.c_str());
  list<string> result;

  char* line = NULL;
  size_t line_size = 0;

  if (!path.empty()) {
    FILE* fp = fopen(path.c_str(), "r");
    if (!fp) fatal("can not open %s for reading", path.c_str());
    for (ssize_t line_len = 0; line_len != -1;
         line_len = getline(&line, &line_size, fp)) {
      if (!line || line_len <= 1 || line[0] == '#') continue;
      if (line[line_len - 1] == '\n') line[line_len - 1] = 0;  // chomp
      // ltrim
      const char* p = line;
      while (*p == ' ') ++p;
      result.push_back(p);
    }
    fclose(fp);
  }
  if (line) free(line);
  return result;
}

static string get_config_content(const string& etc_dir, const string& code_path,
                                 const string& name, const string& fallback = "", bool strict = false) {
  string result;
  string config_path = get_config_path(etc_dir, code_path, name, strict);
  log_debug("get_config_content: %s %s", name.c_str(), config_path.c_str());
  if (!config_path.empty()) {
    result = string_chomp(fs::read(config_path));
  }
  if (result.empty()) result = fallback;
  return result;
}

static string get_src_name(const string& etc_dir, const string& code_path) {
  string fallback = "a" + fs::extname(code_path);
  return get_config_content(etc_dir, code_path, ENV_COMPILE EXT_SRC_NAME,
                            fallback);
}

static string get_solution_name(const string& etc_dir,
                                const string& code_path) {
  string fallback = "solution" + fs::extname(code_path);
  return get_config_content(etc_dir, code_path, ENV_COMPILE EXT_SOLUTION_NAME,
                            fallback);
}

static string prepare_dummy_passwd(const string& cache_dir) {
#ifdef _OPENMP
  ScopedOMPLock lock("dummy_passwd_lock");
#endif
  string path = fs::join(cache_dir, format("tmp/etc/passwd-%d", (int)getuid()));
  string content = format("nobody:%d:%d::/tmp:/bin/false\n", (int)getuid(),
                          (int)getgid());
  if (!fs::exists(path) || fs::read(path) != content) {
    enforce_mkdir_p(fs::dirname(path));
    fs::touch(path);
    fs::ScopedFileLock lock(path);
    fs::write(path, content.c_str());
  }
  return path;
}

static list<string> get_override_lrun_args(const string& etc_dir,
    const string& cache_dir, const string& code_path, const string& env,
    const string& chroot_path, const string& interpreter_name = "") {
  list<string> result;
  // Hide real /etc/passwd (required by Python) on demand
  if (fs::exists(fs::join(chroot_path, ETC_PASSWD)) &&
      get_config_content(etc_dir, code_path, format("%s%s", env, EXT_OPT_FAKE_PASSWD),
                         OPTION_VALUE_TRUE) == OPTION_VALUE_TRUE) {
    string passwd_path = prepare_dummy_passwd(cache_dir);
    result.push_back("--bindfs-ro");
    result.push_back(fs::join(chroot_path, ETC_PASSWD));
    result.push_back(passwd_path);
  }

  // override_dir in config
  string override_dir = get_config_path(etc_dir, code_path, format("%s%s", env,
                                        EXT_FS_OVERRIDE));
  if (override_dir.empty()) return result;

  list<string> files = fs::scandir(override_dir);
  for (__typeof(files.begin()) it = files.begin(); it != files.end(); ++it) {
    // treat "__" as "/"
    string name = *it;
    string path = name;
    string_replacei(path, "__", "/");
    if (fs::is_accessible(fs::join(chroot_path, path), R_OK)) {
      result.push_back("--bindfs-ro");
      result.push_back(fs::join(chroot_path, path));
      result.push_back(fs::join(override_dir, name));
    }
  }
  return result;
}

static string uname_r() {
  struct utsname buf;
  uname(&buf);
  return buf.release;
}

static bool is_fopen_filter_supported(const string& cache_dir) {
  // annoying, but we have to do this check...
  // otherwise we won't work on a Debian stock kernel if --fopen-filter is used in lrun args.
  bool result =
    true;  // most distros enable it, Arch, Ubuntu, Fedora ... except for Debian
  string release = uname_r();
  // read result from cache first. If our detection is incorrect, the user is able to
  // write the cache file to override it.
  string cached_result_path = fs::join(cache_dir, SUBDIR_KERNEL_CONFIG_CACHE,
                                       "CONFIG_FANOTIFY_ACCESS_PERMISSIONS");
  if (fs::is_accessible(cached_result_path)) {
    result = ((fs::read(cached_result_path) + " ")[0] == 'y');
  } else {
    string kconfig_path = "/boot/config-" + release;  // only consider debian
    if (fs::is_accessible(kconfig_path)) {
      string kconfig_content = fs::read(kconfig_path);
      if (kconfig_content.find("CONFIG_FANOTIFY_ACCESS_PERMISSIONS=y") ==
          string::npos) {
        result = false;
      }
    }
    enforce_mkdir_p(fs::dirname(cached_result_path));
    fs::write(cached_result_path, result ? "y" : "n");
  }
  return result;
}

// try to keep only lrun "safe" args
template<typename L>
static L filter_user_lrun_args(const L& items, const string& cache_dir) {
  L result;
  int next_safe = 0, next_ignored = 0;
  for (__typeof(items.begin()) it = items.begin(); it != items.end(); ++it) {
    string item = string(*it);
    if (next_safe > 0) {
      if (next_ignored == 0) {
        result.push_back(item);
      } else {
        --next_ignored;
      }
      --next_safe;
      continue;
    }
    if (item == "--syscalls" || item == "--domainname" || item == "--hostname" ||
        item == "--ostype" \
        || item == "--osrelease" || item == "--osversion" || item == "--max-stack") {
      next_safe = 1;
    } else if (item == "--fopen-filter") {
      next_safe = 2;
      if (!is_fopen_filter_supported(cache_dir)) {
        next_ignored = next_safe;
        static bool warned = false;
        if (!warned) {
          errno = 0;
          log_warn("You system does not support --fopen-filter. The kernel must be compiled with %s",
                   "CONFIG_FANOTIFY_ACCESS_PERMISSIONS");
          continue;
        }
      }
    } else {
      log_info("lrun arg '%s' is unsafe, dropping it and following args",
               item.c_str());
      break;
    }
    result.push_back(item);
  }
  return result;
}

template<typename L>
static L escape_list(const L& items, const map<string, string>& mappings) {
  L result;
  for (__typeof(items.begin()) it = items.begin(); it != items.end(); ++it) {
    string item = string(*it);
    for (__typeof(mappings.begin()) it = mappings.begin(); it != mappings.end();
         ++it) {
      const string& k = it->first;
      const string& v = it->second;
      string_replacei(item, k, v);
    }
    result.push_back(item);
  }
  return result;
}

static string shell_escape(const string& str) {
  bool should_escape = false;
  static const char safe_chars[] =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+=./$:|;";
  for (size_t i = 0; i < str.length(); ++i) {
    if (strchr(safe_chars, str[i]) == NULL) {
      should_escape = true;
      break;
    }
  }

  if (!should_escape) return str;

  string result = "'";
  for (size_t i = 0; i < str.length(); ++i) {
    char c = str[i];
    if (c == '\'') {
      result += "'\"'\"'";
    } else {
      result += c;
    }
  }
  return result + "'";
}

static string shell_escape(const list<string>& items) {
  string result = "";
  for (__typeof(items.begin()) it = items.begin(); it != items.end(); ++it) {
    if (!result.empty()) result += " ";
    result += shell_escape(*it);
  }
  return result;
}

static string get_random_hash(int len = 40) {
  static const char chars[] = "0123456789abcdef";
  static const int MIN_LEN = 4;
  if (len < MIN_LEN) len = MIN_LEN;

  string result;
  result.reserve(len);
  for (int i = 0; i < len; ++i) result += chars[rand() % (sizeof(chars) - 1)];
  return result;
}


static void ensure_system(const string& cmd) {
  log_debug("running: %s", cmd.c_str());
  int ret = system(cmd.c_str());
  if (ret != 0) fatal("failed to run %s", cmd.c_str());
}

static string prepare_chroot(const string& etc_dir, const string& code_path,
                             const string& env) {
  string mirrorfs_config_path = get_config_path(etc_dir, code_path, format("%s%s",
                                env, EXT_MIRRRORFS));
  if (mirrorfs_config_path.empty()) fatal("cannot find mirrorfs config");

  string content = fs::read(mirrorfs_config_path);
  string name = sha1(content);
  string dest = fs::join(CHROOT_BASE_DIR, name);

  log_debug("prepare_chroot: config = %s dest = %s", mirrorfs_config_path.c_str(),
            dest.c_str());

  {
    // lock both processes and threads
#ifdef _OPENMP
    ScopedOMPLock lock("chroot_lock");
#endif
    // enforce_mkdir_p(base_dir);
    fs::ScopedFileLock chroot_dir_lock(mirrorfs_config_path);

    if (fs::is_accessible(dest, F_OK)) {
      log_debug("already mounted: %s", dest.c_str());
      return dest;
    }

    string comment = fs::join(fs::basename(fs::dirname(mirrorfs_config_path)), env);
    string cmd = format("lrun-mirrorfs --name %s --setup %s --comment %s 1>&2",
                        name, shell_escape(mirrorfs_config_path), comment);
    ensure_system(cmd);

    // wait 5s until mount finishes
    int mounted = 0;
    for (int i = 0; i < 50; ++i) {
      if (fs::is_accessible(dest, F_OK)) {
        mounted = 1;
        break;
      }
      usleep(100000); // 0.1s
    }
    if (!mounted) fatal("%s is not mounted correctly", dest.c_str());
  }

  return dest;
}

static void print_usage() {
  fprintf(stderr, "%s",
          "Run a contestant and interactor and print response JSON:\n"
          "  linteractive --solution-code contestant.cpp --user-code interactor.cpp\n"
          "               --testcase --input case.in --output case.out\n"
          "               [--testcase --input case2.in --output case2.out] ...\n"
          "\n"
          "Legacy flag names: --solution-code is the contestant; --user-code is the interactor.\n"
          "The interactor is invoked with testlib arguments: input transcript output.\n"
          "Input and answer are read-only; transcript is a separate writable file per testcase.\n"
          "It exchanges messages with the contestant on stdin/stdout.\n"
          "Its exit code is 0 for AC, 1 for WA, 2 for PE; other exits or crashes are internal errors.\n"
          "\n"
          "Options (put limits before the corresponding --input):\n"
          "  --etc-dir path  --cache-dir path  --threads n  --keep-stderr\n"
          "  --max-cpu-time seconds  --max-real-time seconds\n"
          "  --max-memory bytes  --max-output bytes\n"
          "  --max-checker-cpu-time seconds  --max-checker-real-time seconds\n"
          "  --max-checker-memory bytes  --max-checker-output bytes\n"
          "  --max-compiler-cpu-time seconds  --max-compiler-real-time seconds\n"
          "  --max-compiler-memory bytes  --max-compiler-output bytes\n"
          "  --env name value  --user-stderr path  --pretty-print\n"
          "  --check  --compiler-versions  --all-compiler-versions\n"
          "  --help  --json-schema  --version\n"
          "\n"
          "--keep-stderr returns separate stderr and judgeStderr fields.\n"
          "The lrun backend requires a Linux kernel with cgroup v1 controllers.\n"
         );
  cleanup_exit(0);
}

static void print_json_schema() {
  // Generated from schema/interactive-response.json.
  fprintf(stderr, "%s",
          "{\n"
          "  \"$schema\": \"http://json-schema.org/draft-04/schema#\",\n"
          "  \"type\": \"object\",\n"
          "  \"definitions\": {\n"
          "    \"compilationResult\": {\n"
          "      \"type\": \"object\",\n"
          "      \"description\": \"The compilation result of the source code\",\n"
          "      \"properties\": {\n"
          "        \"log\": {\n"
          "          \"type\": \"string\",\n"
          "          \"description\": \"Compiler log, including warnings and errors. Show this to end-users\"\n"
          "        },\n"
          "        \"success\": {\n"
          "          \"type\": \"boolean\",\n"
          "          \"description\": \"Whether compilation has succeeded\"\n"
          "        },\n"
          "        \"error\": {\n"
          "          \"type\": \"string\",\n"
          "          \"description\": \"Internal error message. Should not be visible to end-users. Present only when an internal error (ex. required compiler is not installed) happens\"\n"
          "        }\n"
          "      },\n"
          "      \"additionalProperties\": false,\n"
          "      \"required\": [\n"
          "        \"log\",\n"
          "        \"success\"\n"
          "      ]\n"
          "    },\n"
          "    \"testcaseResult\": {\n"
          "      \"type\": \"object\",\n"
          "      \"properties\": {\n"
          "        \"result\": {\n"
          "          \"type\": \"string\",\n"
          "          \"enum\": [\n"
          "            \"ACCEPTED\",\n"
          "            \"PRESENTATION_ERROR\",\n"
          "            \"WRONG_ANSWER\",\n"
          "            \"NON_ZERO_EXIT_CODE\",\n"
          "            \"MEMORY_LIMIT_EXCEEDED\",\n"
          "            \"TIME_LIMIT_EXCEEDED\",\n"
          "            \"OUTPUT_LIMIT_EXCEEDED\",\n"
          "            \"FLOAT_POINT_EXCEPTION\",\n"
          "            \"SEGMENTATION_FAULT\",\n"
          "            \"RUNTIME_ERROR\",\n"
          "            \"INTERNAL_ERROR\"\n"
          "          ],\n"
          "          \"description\": \"Judge response for the test case\"\n"
          "        },\n"
          "        \"exceed\": {\n"
          "          \"type\": \"string\",\n"
          "          \"enum\": [\n"
          "            \"CPU_TIME\",\n"
          "            \"REAL_TIME\",\n"
          "            \"MEMORY\",\n"
          "            \"OUTPUT\"\n"
          "          ],\n"
          "          \"description\": \"The limit that the program exceeded. Present only when the program has exceeded one limit\"\n"
          "        },\n"
          "        \"time\": {\n"
          "          \"type\": \"number\",\n"
          "          \"description\": \"Contestant CPU time in seconds, including failed runs when available.\"\n"
          "        },\n"
          "        \"memory\": {\n"
          "          \"type\": \"number\",\n"
          "          \"description\": \"Contestant peak memory in bytes, including failed runs when available.\"\n"
          "        },\n"
          "        \"error\": {\n"
          "          \"type\": \"string\",\n"
          "          \"description\": \"Judge diagnostic; may include details of contestant or interactor failures.\"\n"
          "        },\n"
          "        \"stderr\": {\n"
          "          \"type\": \"string\",\n"
          "          \"description\": \"stderr output of the program. Present only when the command line option \\\"--keep-stderr\\\" is set\"\n"
          "        },\n"
          "        \"judgeStderr\": {\n"
          "          \"type\": \"string\",\n"
          "          \"description\": \"Interactor stderr, captured separately when --keep-stderr is set.\"\n"
          "        }\n"
          "      },\n"
          "      \"additionalProperties\": false,\n"
          "      \"required\": [\n"
          "        \"result\"\n"
          "      ]\n"
          "    }\n"
          "  },\n"
          "  \"properties\": {\n"
          "    \"testcases\": {\n"
          "      \"type\": \"array\",\n"
          "      \"description\": \"Test case results. Present only when compilation has successed\",\n"
          "      \"items\": {\n"
          "        \"$ref\": \"#/definitions/testcaseResult\"\n"
          "      }\n"
          "    },\n"
          "    \"userCompilation\": {\n"
          "      \"$ref\": \"#/definitions/compilationResult\",\n"
          "      \"description\": \"Compilation result of the user code\"\n"
          "    },\n"
          "    \"judgeCompilation\": {\n"
          "      \"$ref\": \"#/definitions/compilationResult\",\n"
          "      \"description\": \"Interactor compilation result. Present after contestant compilation succeeds.\"\n"
          "    }\n"
          "  },\n"
          "  \"additionalProperties\": false,\n"
          "  \"required\": [\n"
          "    \"userCompilation\"\n"
          "  ]\n"
          "}\n"
         );
  cleanup_exit(0);
}

static void print_version() {
  printf("linteractive %s\n", LJUDGE_VERSION);
  printf("\nthread support: %s\n",
#ifdef _OPENMP
         "yes"
#else
         "no"
#endif
        );
  cleanup_exit(0);
}

// like Python's subprocess.check_output but without the check part
static string check_output(const string& command, bool capture_stderr = false) {
  string result;
  do {
    // check lrun
    string real_command = command + " <" DEV_NULL;
    if (real_command.find(" 2>") == string::npos) {
      if (capture_stderr) real_command += " 2>&1";
      else real_command += " 2>" DEV_NULL;
    }

    FILE* fp = popen(real_command.c_str(), "r");
    if (!fp) break;

    char buf[16384];
    for (;;) {
      size_t bytes = fread(buf, 1, sizeof(buf) - 1, fp);
      buf[bytes] = 0;
      if (bytes == 0) break;
      result += buf;
    }
    pclose(fp);
  } while (false);
  return result;
}

static void print_checkpoint(const string& name, bool passed,
                             const string& solution) {
  term::set(term::attr::BOLD, term::fg::WHITE,
            passed ? term::bg::GREEN : term::bg::RED);
  printf(passed ? " Y " : " N ");
  term::set();
  term::set(term::attr::BOLD);
  printf(" %s\n", name.c_str());
  term::set();
  if (!passed) {
    string indented = solution;
    string_replacei(indented, "\n", "\n    ");
    printf("    %s\n\n", indented.c_str());
  }
}

static void print_checkfail(const string& name, const string& message,
                            char symbol = '!') {
  term::set(term::attr::BOLD, term::fg::WHITE, symbol == 'S' ||
            symbol == 'W' ? term::bg::YELLOW : term::bg::RED);
  printf(" %c ", symbol);
  term::set();
  term::set(term::attr::BOLD);
  printf(" %s\n", name.c_str());
  term::set();
  string indented = message;
  string_replacei(indented, "\n", "\n    ");
  printf("    %s\n\n", indented.c_str());
}

static bool is_cgroup_enabled(const string& subsystem) {
  if (!fs::exists(PROC_CGROUP)) return false;
  FILE* fp = fopen(PROC_CGROUP, "r");
  if (!fp) return false;
  int enabled_bit = 0;
  char name[32], enabled[16];
  while (fscanf(fp, "%31s %*s %*s %15s", name, enabled) == 2) {
    if (subsystem == string(name)) {
      enabled_bit = (strcmp(enabled, "0") != 0);
      break;
    }
  }
  if (fp) fclose(fp);
  return enabled_bit;
}

static void do_check() {
  if (getuid() == 0) {
    fprintf(stderr,
            "Running ljudge --check using root is not supported.\n"
            "Please switch to a non-root user and try again.\n");
    exit(1);
  }

  string username = getenv("USER") ? getenv("USER") : "username";

  {
    // cgroup
    print_checkpoint(
      "cgroup memory controller is enabled",
      is_cgroup_enabled("memory"),
      "This is common on Debian-based systems. Add `cgroup_enable=memory`\n"
      "to kernel parameter and reboot. If you are using GRUB2, try:\n\n"
      "  grep -q cgroup_enable /etc/default/grub || {\n"
      "    S='s/CMDLINE_LINUX=\"/CMDLINE_LINUX=\"cgroup_enable=memory /'\n"
      "    sudo sed -i \"$S\" /etc/default/grub\n"
      "    sudo update-grub2\n"
      "    sudo reboot\n"
      "  }");
    print_checkpoint(
      "cgroup cpuacct, devices, freezer controllers are enabled",
      is_cgroup_enabled("cpuacct") && is_cgroup_enabled("devices") &&
      is_cgroup_enabled("freezer"),
      "Most modern Linux distributions have cgroup enabled by default.\n"
      "Upgrade the kernel or switch to another distribution.");
  }

  do { // lrun
    string lrun_path = which("lrun");
    if (lrun_path.empty()) {
      string lrun_path_non_exec = which("lrun", F_OK);
      if (lrun_path_non_exec.empty()) {
        print_checkfail(
          "lrun not found",
          "lrun is required. Please install it.");
      } else {
        print_checkfail(
          "lrun is not executable",
          "lrun is installed but the current user cannot execute it.\n"
          "This is probably because the current user is not in `lrun`\n"
          "group. To fix it by adding the user to `lrun` group:\n\n" +
          format("  sudo gpasswd -a %s lrun", username));
      }
      break;
    }
    string lrun_help = check_output("lrun --help 2>&1");
    print_checkpoint(
      "lrun supports --syscalls",
      lrun_help.find("--syscalls") != string::npos,
      "lrun is compiled without libseccomp support.\n"
      "This means all syscall filters will cause ljudge to\n"
      "not work correctly. Install related libseccomp packages\n"
      "and recompile lrun.");
    print_checkpoint(
      "lrun supports --bindfs-ro",
      lrun_help.find("--bindfs-ro") != string::npos,
      "Please upgrade lrun to at least v1.1.3");
    print_checkpoint(
      "lrun supports --fopen-filter",
      lrun_help.find("--fopen-filter") != string::npos,
      "Please upgrade lrun to at least v1.1.3");
    print_checkpoint(
      "lrun actually works",
      check_output("lrun echo foofoo 2>" DEV_NULL).find("foofoo") != string::npos,
      "lrun doesn't work. Please make sure other issues are resolved\n"
      "and try `lrun --debug echo foo` to get some help.");
  } while (false);

  do { // lrun-mirrorfs
    string mirrorfs_path = which("lrun-mirrorfs");
    if (mirrorfs_path.empty()) {
      print_checkfail(
        "lrun-mirrorfs not found",
        "lrun-mirrorfs is required. Please upgrade lrun to v1.1.3");
      break;
    }
  } while (false);

  {
    // kernel
    if (fs::nread("/proc/sys/debug/exception-trace", 1) == "1") {
      print_checkfail(
        "debug.exception-trace is 1",
        "Programs being judged may die in many ways, some of which\n"
        "will write the kernel log. Consider set the flag to 0 to\n"
        "keep the kernel log clean:\n\n"
        "  sudo sysctl -w debug.exception-trace=0\n"
        "  echo 'debug.exception-trace=0' | \\\n"
        "    sudo tee /etc/sysctl.d/99-disable-trace.conf", 'W');
    }

#ifndef PR_GET_NO_NEW_PRIVS
# define PR_GET_NO_NEW_PRIVS 39
#endif

    if (prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) == -1) {
      print_checkfail(
        "prctl has no NO_NEW_PRIVS support",
        "You are running an old kernel which has no prctl NO_NEW_PRIVS\n"
        "support. This may cause potencial security issues. However,\n"
        "ljudge uses FUSE's `-o nosuid` to counter these issues. Not a\n"
        "big deal. Upgrading kernel is recommended.", 'W');
    }

    if (!fs::exists("/proc/self/ns/pid")) {
      print_checkfail(
        "kernel does not have full pid namespace support",
        "lrun will use a legacy method to run programes.\n"
        "Not a big deal. But upgrading kernel is recommended.", 'W');
    }

    if (sysconf(_SC_ARG_MAX) < 4096) {
      print_checkfail(
        "Maximum length of arguments for a new process is too small.",
        "Not a serious one. But upgrading kernel is recommended.", 'W');
    }
  }

  {
    // kernel config
    string kernel_config;
    // Arch Linux puts kernel config at /proc/config.gz
    // Debian puts kernel config at /boot/config-`uname -r`
    if (fs::is_accessible("/proc/config.gz")) {
      kernel_config = check_output("zcat /proc/config.gz");
    } else {
      string config_path = "/boot/config-" + uname_r();
      if (fs::is_accessible(config_path)) {
        kernel_config = fs::read(config_path);
      }
    }
    if (kernel_config.empty()) {
      print_checkfail(
        "kernel config not found",
        "Related checks are skipped. Please make sure\n"
        "the kernel is compiled with\n"
        "CONFIG_FANOTIFY_ACCESS_PERMISSIONS", 'W');
    } else {
      print_checkpoint(
        "kernel supports fanotify permission check",
        kernel_config.find("CONFIG_FANOTIFY_ACCESS_PERMISSIONS=y") != string::npos,
        "CONFIG_FANOTIFY_ACCESS_PERMISSIONS not found.\n"
        "lrun --fopen-filter will not work properly.");
    }
  }

  cleanup_exit(0);
}

// find something like a.b.c from a long string
static string scan_version_string(const string& content) {
  string result;
  bool current_word_is_version = false;
  for (size_t i = 0; i < content.length(); ++i) {
    char c = content[i];
    if (c >= '0' && c <= '9') {
      result += c;
      current_word_is_version = true;
    } else if (c == '.') {
      if (current_word_is_version) result += c;
    } else {
      if (current_word_is_version) {
        // exiting version, do check
        // remove tailing dot
        if (result.length() > 0 &&
            result[result.length() - 1] == '.') result = result.substr(0,
                  result.length() - 1);
        if (strchr(result.c_str(), '.') != NULL && result.length() >= 2) return result;
        // no '.', not a version string
        result = "";
      }
      current_word_is_version = false;
    }
  }
  return result;
}

static void fetch_compiler_versions(std::vector<j::value>& result,
                                    const string& etc_dir, bool only_present = true) {
  // scan etc_dir
  list<string> exts = fs::scandir(etc_dir);
  for (__typeof(exts.begin()) it = exts.begin(); it != exts.end(); ++it) {
    const string& ext = *it;
    if (ext == DEFAULT_CONF_DIR) continue;

    // pick version.cmd_list and run
    string dummy_code_path = format("a.%s", ext);
    string version_cmd = shell_escape(get_config_list(etc_dir, dummy_code_path,
                                      ENV_VERSION EXT_CMD_LIST, true /* strict */));

    // version cmd is required for every
    if (version_cmd.empty()) continue;
    string content = check_output(version_cmd, true /* stderr */);

    // scan version string from the output
    // if no version found, hide the compiler from output list
    string version = scan_version_string(content);

    j::object jo;
    if (!version.empty()) {
      jo["version"] = j::value(version);
    } else {
      if (only_present) continue;
    }

    // get compiler / interpreter name
    // if not set, use the first name of compile cmd or run cmd
    // besides, get compile and run commands
    string name = string_chomp(get_config_content(etc_dir, dummy_code_path,
                               ENV_VERSION EXT_NAME, "" /* default */, true /* strict */));
    list<string> compile_cmds = get_config_list(etc_dir, dummy_code_path,
                                ENV_COMPILE EXT_CMD_LIST, true /* strict */);
    list<string> run_cmds = get_config_list(etc_dir, dummy_code_path,
                                            ENV_RUN EXT_CMD_LIST, true /* strict */);

    if (name.empty() && !compile_cmds.empty()) name = *compile_cmds.begin();
    else if (name.empty() && !run_cmds.empty()) name = *run_cmds.begin();
    else if (name.empty()) name = ext;

    if (!compile_cmds.empty()) jo["compileCmd"] = j::value(shell_escape(
            compile_cmds));
    if (!run_cmds.empty()) jo["runCmd"] = j::value(shell_escape(run_cmds));
    jo["name"] = j::value(name);
    jo["ext"] = j::value(ext);
    result.push_back(j::value(jo));
  }
}

static void print_compiler_versions(const Options& opts,
                                    bool only_present = true) {
  std::vector<j::value> arr;
  fetch_compiler_versions(arr, opts.etc_dir, only_present);
  printf("%s", j::value(arr).serialize(opts.pretty_print).c_str());
  exit(0);
}

static bool is_language_supported(const string& etc_dir,
                                  const string& code_path) {
  // a supported language must have version command configured
  if (get_config_path(etc_dir, code_path, ENV_VERSION EXT_CMD_LIST,
                      true).empty()) {
    return false;
  } else {
    return true;
  }
}

static double to_number(const string& str) {
  double v = 0;
  sscanf(str.c_str(), "%lg", &v);
  return v;
}

long long parse_bytes(const string& str) {
  long long result = 1;
  // accept str which ends with 'k', 'kb', 'm', 'M', etc.
  int pos = str.length() - 1;
  if (pos > 0 && (str[pos] == 'b' || str[pos] == 'B')) --pos;
  if (pos > 0) {
    switch (str[pos]) {
      case 'g':
      case 'G':
        result *= 1024;
      case 'm':
      case 'M':
        result *= 1024;
      case 'k':
      case 'K':
        result *= 1024;
    }
  }
  if (result == 1) {
    // read as long long
    sscanf(str.c_str(), "%lld", &result);
  } else {
    // read as double so that the user can use things like 0.5mb
    double v = 0;
    sscanf(str.c_str(), "%lf", &v);
    result *= v;
  }
  return result;
}


/**
 * --user-code path-to-user-code
 * --testcase
 * --max-cpu-time 1.0
 * --max-real-time 1.5
 * --max-memory 64000000
 * --input /var/cache/bar/1.in
 * --output /var/cache/bar/1.out
 * --input /var/cache/bar/2.in
 * --output /var/cache/bar/2.out
 * --input /var/cache/bar/3.in
 * --output /var/cache/bar/3.out
 */
static Options parse_cli_options(int argc, const char* argv[]) {
  Options options;
  Testcase current_case;

  // default options
  {
    string home = getenv("HOME") ? getenv("HOME") : "/tmp";
    string etc_dir_candidates[] = { "/etc/ljudge", fs::join(home, ".config/ljudge"), fs::join(home, "ljudge/etc/ljudge"), "./etc/ljudge", "../etc/ljudge" };
    for (size_t i = 0;
         i < sizeof(etc_dir_candidates) / sizeof(etc_dir_candidates[0]); ++i) {
      if (fs::is_dir(etc_dir_candidates[i])) {
        options.etc_dir = etc_dir_candidates[i];
        break;
      }
    }
    options.cache_dir = fs::join(home, ".cache/ljudge");
    options.compiler_limit = { 15, 15, 1 << 29 /* 512M mem */, 1 << 27 /* 128M out */, 0 };
    options.pretty_print = isatty(STDOUT_FILENO);
    options.skip_checker = false;
    options.keep_stdout = false;
    options.keep_stderr = false;
    options.direct_mode = false;
    options.nthread = 0;
    current_case.checker_limit = { 120, 120, 1 << 30, 1 << 30, 1 << 30};
    current_case.runtime_limit = { 1, 3, 1 << 26 /* 64M mem */, 1 << 25 /* 32M output */, 0 };
    debug_level = getenv("DEBUG") ? 10 : 0;
  }

#define REQUIRE_NARGV(n) if (i + n >= argc) { \
  fatal("Option '%s' requires %d argument%s.", option.c_str(), n, n > 1 ? "s" : ""); }
#define NEXT_STRING_ARG string(argv[++i])
#define NEXT_NUMBER_ARG (to_number(NEXT_STRING_ARG))
#define APPEND_TEST_CASE if (!current_case.input_path.empty()) { \
  options.cases.push_back(current_case); \
  current_case.input_path = current_case.output_path = current_case.output_sha1 =\
  current_case.user_stdout_path = current_case.user_stderr_path = ""; }

  for (int i = 1; i < argc; ++i) {
    string option;
    if (strncmp("--", argv[i], 2) == 0) {
      option = argv[i] + 2;
    } else if (strncmp("-", argv[i], 1) == 0) {
      option = argv[i] + 1;
    } else {
      // check "direct mode"
      option = argv[i];
      if (options.user_code_path.empty() && i == argc - 1 &&
          is_language_supported(options.etc_dir, option) && options.cases.size() <= 1 &&
          !options.skip_checker && options.checker_code_path.empty()) {
        options.user_code_path = option;
        options.skip_checker = true;
        options.direct_mode = true;
        options.keep_stdout = true;
        options.keep_stderr = true;
        continue;
      } else {
        fatal("`%s` is not a valid option. Use `--help` for more information", argv[i]);
      }
    }

    if (option == "user-code" || option == "u") {
      REQUIRE_NARGV(1);
      options.user_code_path = NEXT_STRING_ARG;
    } else if (option == "checker-code" || option == "c") {
      REQUIRE_NARGV(1);
      options.checker_code_path = NEXT_STRING_ARG;
    } else if (option == "solution-code") {
      REQUIRE_NARGV(1);
      options.solution_code_path = NEXT_STRING_ARG;
    } else if (option == "testcase") {
      APPEND_TEST_CASE;
    } else if (option == "env") {
      REQUIRE_NARGV(2);
      string name = NEXT_STRING_ARG;
      string value = NEXT_STRING_ARG;
      options.envs[name] = value;
    } else if (option == "input" || option == "i") {
      APPEND_TEST_CASE;
      REQUIRE_NARGV(1);
      current_case.input_path = NEXT_STRING_ARG;
    } else if (option == "output" || option == "o") {
      REQUIRE_NARGV(1);
      current_case.output_path = NEXT_STRING_ARG;
    } else if (option == "slice" || option == "s") {
      REQUIRE_NARGV(1);
      current_case.slice_path = NEXT_STRING_ARG;
    } else if (option == "user-stdout") {
      REQUIRE_NARGV(1);
      current_case.user_stdout_path = NEXT_STRING_ARG;
    } else if (option == "user-stderr") {
      REQUIRE_NARGV(1);
      current_case.user_stderr_path = NEXT_STRING_ARG;
    } else if (option == "output-sha1" || option == "osha1") {
      // --output-sha1 ac-sha1(chomp),pe-sha1
      REQUIRE_NARGV(1);
      string sha1s = NEXT_STRING_ARG;
      current_case.output_sha1 = sha1s.substr(0, 40);
      current_case.output_pe_sha1 = sha1s.substr(41, 40);
      /* [[[cog
        import cog
        opts = ['cpu_time', 'real_time', 'output', 'memory']
        prefixes = {'': 'current_case.runtime_limit',
                    'checker-': 'current_case.checker_limit',
                    'compiler-': 'options.compiler_limit'}
        for prefix, var_name in prefixes.items():
          for opt in opts:
            cog.out(
              '''
              } else if (option == "max-%s%s") {
                REQUIRE_NARGV(1);
                %s.%s = %s;
              ''' % (prefix,
                     opt.replace('_', '-'),
                     var_name,
                     opt,
                     (opt in ['memory', 'output']) and 'parse_bytes(NEXT_STRING_ARG)' or 'NEXT_NUMBER_ARG'),
              trimblanklines=True)
      ]]] */
    } else if (option == "max-cpu-time") {
      REQUIRE_NARGV(1);
      current_case.runtime_limit.cpu_time = NEXT_NUMBER_ARG;
    } else if (option == "max-real-time") {
      REQUIRE_NARGV(1);
      current_case.runtime_limit.real_time = NEXT_NUMBER_ARG;
    } else if (option == "max-jvm-memory") {
      REQUIRE_NARGV(1);
      current_case.runtime_limit.jvm_memory = NEXT_NUMBER_ARG;
    } else if (option == "max-output") {
      REQUIRE_NARGV(1);
      current_case.runtime_limit.output = parse_bytes(NEXT_STRING_ARG);
    } else if (option == "max-memory") {
      REQUIRE_NARGV(1);
      current_case.runtime_limit.memory = parse_bytes(NEXT_STRING_ARG);
    } else if (option == "max-compiler-cpu-time") {
      REQUIRE_NARGV(1);
      options.compiler_limit.cpu_time = NEXT_NUMBER_ARG;
    } else if (option == "max-compiler-real-time") {
      REQUIRE_NARGV(1);
      options.compiler_limit.real_time = NEXT_NUMBER_ARG;
    } else if (option == "max-compiler-output") {
      REQUIRE_NARGV(1);
      options.compiler_limit.output = parse_bytes(NEXT_STRING_ARG);
    } else if (option == "max-compiler-memory") {
      REQUIRE_NARGV(1);
      options.compiler_limit.memory = parse_bytes(NEXT_STRING_ARG);
    } else if (option == "max-checker-cpu-time") {
      REQUIRE_NARGV(1);
      current_case.checker_limit.cpu_time = NEXT_NUMBER_ARG;
    } else if (option == "max-checker-real-time") {
      REQUIRE_NARGV(1);
      current_case.checker_limit.real_time = NEXT_NUMBER_ARG;
    } else if (option == "max-checker-output") {
      REQUIRE_NARGV(1);
      current_case.checker_limit.output = parse_bytes(NEXT_STRING_ARG);
    } else if (option == "max-checker-memory") {
      REQUIRE_NARGV(1);
      current_case.checker_limit.memory = parse_bytes(NEXT_STRING_ARG);
      /* [[[end]]] */
    } else if (option == "etc-dir") {
      REQUIRE_NARGV(1);
      options.etc_dir = NEXT_STRING_ARG;
    } else if (option == "cache-dir") {
      REQUIRE_NARGV(1);
      options.cache_dir = NEXT_STRING_ARG;
    } else if (option == "help" || option == "h") {
      print_usage();
    } else if (option == "json-schema") {
      print_json_schema();
    } else if (option == "version" || option == "v") {
      print_version();
    } else if (option == "compiler-versions" || option == "cvs") {
      print_compiler_versions(options, true /* only_present */);
    } else if (option == "all-compiler-versions" || option == "acvs") {
      print_compiler_versions(options, false /* only_present */);
    } else if (option == "debug") {
      debug_level = 10;  // show info, warn, error
      load_libsegfault();
      options.keep_stdout = true;
      options.keep_stderr = true;
    } else if (option == "check") {
      do_check();
    } else if (option == "pretty-print" || option == "pp") {
      options.pretty_print = 1;
    } else if (option == "skip-checker") {
      options.skip_checker = true;
      options.keep_stdout = true;
    } else if (option == "keep-stdout") {
      options.keep_stdout = true;
    } else if (option == "keep-stderr") {
      options.keep_stderr = true;
#ifdef _OPENMP
    } else if (option == "threads" || option == "jobs" || option == "j") {
      REQUIRE_NARGV(1);
      options.nthread = NEXT_NUMBER_ARG;
#endif
    } else {
      fatal("'%s' is not a valid option", argv[i]);
    }
  }
  APPEND_TEST_CASE;

  // if the user has decided to skip checker and did not provide a testcase, add a dummy one
  if (options.cases.empty() && options.skip_checker) {
    string input_path = isatty(STDIN_FILENO) ?
                        (options.direct_mode ? "" /* pass through */ : DEV_NULL)
                        : fs::resolve(format("/proc/self/fd/%d",
                                      STDIN_FILENO) /* the file is passed using '<' */);
    if (!fs::is_accessible(input_path, R_OK)) input_path = DEV_NULL;
    current_case.input_path = input_path;
    if (options.direct_mode && input_path != DEV_NULL &&
        !input_path.empty() /* not using a real file */) {
      current_case.runtime_limit.real_time = 0;  // unlimited
    }
    options.cases.push_back(current_case);
  }

#undef APPEND_TEST_CASE
#undef NEXT_NUMBER_ARG
#undef NEXT_STRING_ARG
#undef REQUIRE_NARGV

  log_debug("etc-dir = %s", options.etc_dir.c_str());
  log_debug("cache-dir = %s", options.cache_dir.c_str());
  log_debug("debug-level = %d", debug_level);

  return options;
}

static void check_path(std::vector<string>& errors, const string& path,
                       bool is_dir, const string& name) {
  if (path.empty()) {
    errors.push_back(name + " is required");
    return;
  }

  if (!(is_dir ? \
        (fs::is_dir(path) && fs::is_accessible(path, R_OK | X_OK))
        : (!fs::is_dir(path) && fs::is_accessible(path, R_OK)))) {
    errors.push_back(name + " (" + path + ") is not accessible");
  }
}

static bool is_sha1(const string& str) {
  if (str.length() != 40) return false;
  for (int i = 0; i < 40; ++i) {
    if (str[i] < '0' || str[i] > 'f') return false;
  }
  return true;
}

static void check_options(const Options& options) {
  std::vector<string> errors;

  enforce_mkdir_p(options.cache_dir);

  check_path(errors, options.etc_dir, true, "--etc-dir");
  check_path(errors, options.cache_dir, true, "--cache-dir");
  check_path(errors, options.user_code_path, false, "--user-code");
  check_path(errors, options.solution_code_path, false, "--solution-code");

  for (int i = 0; i < (int)options.cases.size(); ++i) {
    const Testcase& kase = options.cases[i];
    if (!options.direct_mode || !kase.input_path.empty()) {
      check_path(errors, kase.input_path, false /* is_dir */,
                 format("--input of testcases[%d]", i));
    }
    if (options.skip_checker) {
      if (!kase.output_path.empty())
        errors.push_back("--output conflicts with --skip-checker");
      if (!kase.output_sha1.empty())
        errors.push_back("--output-sha1 conflicts with --skip-checker");
    } else {
      if (!kase.output_sha1.empty()) {
        if (!is_sha1(kase.output_sha1)) errors.push_back("'" + kase.output_sha1 +
              "' is not a valid hex SHA1");
        // allow output_pe_sha1 to be empty
        if (!kase.output_pe_sha1.empty() &&
            !is_sha1(kase.output_pe_sha1)) errors.push_back("'" + kase.output_pe_sha1 +
                  "' is not a invalid hex SHA1");
      } else {
        check_path(errors, kase.output_path, false, format("--output of testcases[%d]",
                   i));
      }
    }
  }

  if (options.cases.empty()) {
    errors.push_back("At lease one testcase is required");
  }

  if (options.skip_checker && !options.checker_code_path.empty()) {
    errors.push_back("--skip-checker conflicts with --checker-code");
  }

  if (getuid() == 0) {
    errors.push_back("Running ljudge using root is forbidden");
  }

#ifdef _OPENMP
  if (options.nthread < 0) {
    errors.push_back("--threads cannot < 0");
  }
#endif

  if (errors.size() > 0) {
    for (int i = 0; i < (int)errors.size(); ++i) {
      fprintf(stderr, "%s\n", errors[i].c_str());
    }
    fprintf(stderr, "--help will show valid options\n");
    cleanup_exit(1);
  }
}

static void setfd(int dst, int src) {
  if (src == dst || src < 0) return;
  if (dup2(src, dst) < 0) {
    perror("dup2");
    _exit(127);
  }
  close(src);
}

// Reserve descriptors 0..3 for stdio and lrun's status channel. CLOEXEC also
// prevents concurrently launched testcases from retaining each other's pipes.
struct ScopedPipe {
  int fd[2];
  ScopedPipe() { fd[0] = fd[1] = -1; }
  ScopedPipe(const ScopedPipe&) = delete;
  ScopedPipe& operator=(const ScopedPipe&) = delete;
  ~ScopedPipe() { close_all(); }
  void close_all() {
    for (int i = 0; i < 2; ++i) {
      if (fd[i] >= 0) close(fd[i]);
      fd[i] = -1;
    }
  }
  bool open_pipe() {
    if (pipe2(fd, O_CLOEXEC) < 0) return false;
    for (int i = 0; i < 2; ++i) {
      if (fd[i] >= 4) continue;
      int replacement = fcntl(fd[i], F_DUPFD_CLOEXEC, 4);
      if (replacement < 0) { close_all(); return false; }
      close(fd[i]);
      fd[i] = replacement;
    }
    return true;
  }
};

static LrunResult parse_lrun_output(const string& lrun_output) {
  LrunResult result;
  unsigned seen = 0;
  std::istringstream lines(lrun_output);
  string line;
  while (std::getline(lines, line)) {
    std::istringstream fields(line);
    string key, extra;
    if (!(fields >> key)) continue;
    unsigned bit = 0;
    bool valid = true;
    if (key == "MEMORY") {
      bit = 1;
      valid = bool(fields >> result.memory) && result.memory >= 0;
    } else if (key == "CPUTIME") {
      bit = 2;
      valid = bool(fields >> result.cpu_time) && std::isfinite(result.cpu_time) && result.cpu_time >= 0;
    } else if (key == "REALTIME") {
      bit = 4;
      valid = bool(fields >> result.real_time) && std::isfinite(result.real_time) && result.real_time >= 0;
    } else if (key == "SIGNALED") {
      bit = 8;
      int value = -1;
      valid = bool(fields >> value) && (value == 0 || value == 1);
      result.signaled = value == 1;
    } else if (key == "EXITCODE") {
      bit = 16;
      valid = bool(fields >> result.exit_code) && result.exit_code >= 0 && result.exit_code <= 255;
    } else if (key == "TERMSIG") {
      bit = 32;
      valid = bool(fields >> result.term_sig) && result.term_sig >= 0 && result.term_sig < NSIG;
    } else if (key == "EXCEED") {
      bit = 64;
      string value;
      valid = bool(fields >> value) && (value == "none" || value == "CPU_TIME" ||
              value == "REAL_TIME" || value == "MEMORY" || value == "OUTPUT");
      if (value != "none") result.exceed = value;
    } else {
      continue;
    }
    if (!valid || (fields >> extra) || (seen & bit)) {
      result.error = "invalid lrun field: " + key;
      return result;
    }
    seen |= bit;
  }
  if (seen != 127) result.error = "incomplete lrun status report";
  else if (result.signaled != (result.term_sig != 0))
    result.error = "inconsistent lrun signal status";
  return result;
}

static void waitChildrenResult(LrunResult& result) {
  // Save ownership before replacing resource data parsed from the status pipe.
  const pid_t pid = result.pid;
  const int fd = result.pipe_fd;
  if (pid <= 0 || fd < 0) return;
  string report, read_error;
  char buffer[1024];
  for (;;) {
    ssize_t size = read(fd, buffer, sizeof buffer);
    if (size > 0) {
      if (report.size() + size <= 65536) report.append(buffer, size);
      else read_error = "lrun status report is too large";
    } else if (size == 0) {
      break;
    } else if (errno != EINTR) {
      read_error = "cannot read lrun status: " + string(strerror(errno));
      break;
    }
  }
  close(fd);
  int status = 0;
  pid_t reaped;
  do { reaped = waitpid(pid, &status, 0); } while (reaped < 0 && errno == EINTR);
  int wait_error = errno;
  result = parse_lrun_output(report);
  if (!read_error.empty()) result.error = read_error;
  if (reaped != pid) {
    result.error = "cannot reap lrun: " + string(strerror(wait_error));
  } else if (WIFSIGNALED(status)) {
    result.error = format("lrun was signaled (%d)", WTERMSIG(status));
  } else if (WIFEXITED(status) && WEXITSTATUS(status) != 0 &&
             (!result.error.empty() || WEXITSTATUS(status) != result.exit_code)) {
    result.error = format("lrun exited with non-zero (%d)", WEXITSTATUS(status));
  }
  log_debug("lrun output:\n%s", report.c_str());
}

#ifndef NDEBUG
static void prepare_crash_report_path() {
  setenv("SEGFAULT_OUTPUT_NAME", format("/tmp/segv.%s.log",
                                        get_random_hash(6)).c_str(), 1 /* overwrite */);
  setenv("SEGFAULT_USE_ALTSTACK", "1", 1 /* overwrite */);
}
#endif

static LrunResult lrun(
#ifdef NDEBUG
  const vector<string>& args, const string& stdin_path, const string& stdout_path,
  const string& stderr_path,
#else
  vector<string> args, string stdin_path, string stdout_path, string stderr_path,
#endif
  bool waiting, int input_fd = -1, int output_fd = -1
) {
  LrunResult result;
  ScopedPipe status_pipe;
  if (!status_pipe.open_pipe()) {
    result.error = "cannot create lrun status pipe";
    return result;
  }

#ifndef NDEBUG
  if (getenv("LJUDGE_SET_LRUN_SEGFAULT_PATH")) {
    prepare_crash_report_path();
  }
  string debug_lrun_command = "lrun";
  for (__typeof(args.begin()) it = args.begin(); it != args.end(); ++it) {
    debug_lrun_command += " " + shell_escape(*it);
  }
  if (!stdin_path.empty()) debug_lrun_command += " <" + shell_escape(stdin_path);
  if (!stdout_path.empty()) debug_lrun_command += " >" + shell_escape(
          stdout_path);
  if (!stderr_path.empty()) {
    if (stderr_path == stdout_path)
      debug_lrun_command += " 2>&1";
    else
      debug_lrun_command += " 2>" + shell_escape(stderr_path);
  }
  log_debug("running: %s", debug_lrun_command.c_str());
  fflush(stderr);
  if (getenv("LJUDGE_KEEP_LRUN_STDERR") && stderr_path == DEV_NULL) {
    stderr_path = format("/tmp/ljudge_lrun.%s.log", get_random_hash(6));
    log_debug("lrun stderr redirects to %s", stderr_path.c_str());
  }
#endif

  pid_t pid = fork();
  if (pid == -1) {
    log_debug("failed to fork\n");
    result.error = "cannot fork to run lrun";
    return result;
  }
  if (pid) {
    close(status_pipe.fd[1]);
    status_pipe.fd[1] = -1;
    result.pipe_fd = status_pipe.fd[0];
    status_pipe.fd[0] = -1;
    result.pid = pid;
    if (waiting) waitChildrenResult(result);
  } else {
    prctl(PR_SET_PDEATHSIG, SIGTERM);
    close(status_pipe.fd[0]);
    // pass lrun's fd (3) output
    static const int LRUN_FILENO = 3;
    setfd(LRUN_FILENO, status_pipe.fd[1]);
    // prepare fds
    if (input_fd >= 0) setfd(STDIN_FILENO, input_fd);
    if (output_fd >= 0) setfd(STDOUT_FILENO, output_fd);
    if (!stdin_path.empty()) {
      fclose(stdin);
      int ret = open(stdin_path.c_str(), O_RDONLY);
      if (ret < 0) { perror(stdin_path.c_str()); _exit(127); }
      setfd(STDIN_FILENO, ret);
    }
    if (!stderr_path.empty()) {
      fclose(stderr);
      int ret = open(stderr_path.c_str(), O_WRONLY | O_TRUNC | O_CREAT, 0600);
      if (ret < 0) { perror(stderr_path.c_str()); _exit(127); }
      setfd(STDERR_FILENO, ret);
    }
    if (!stdout_path.empty()) {
      fclose(stdout);
      if (stderr_path == stdout_path) {
        if (dup2(STDERR_FILENO, STDOUT_FILENO) < 0) { perror("dup2"); _exit(127); }
      } else {
        int ret = open(stdout_path.c_str(), O_WRONLY | O_TRUNC | O_CREAT, 0600);
        if (ret < 0) { perror(stdout_path.c_str()); _exit(127); }
        setfd(STDOUT_FILENO, ret);
      }
    }
    // prepare args
    const char** argv = (const char**)malloc(sizeof(char*) * (args.size() + 2));
    argv[0] = "lrun";
    for (int i = 0; i < (int)args.size(); ++i) {
      argv[i + 1] = args[i].c_str();
    }
    argv[args.size() + 1] = 0;
    execvp("lrun", (char* const*) argv);
    log_error("can not start lrun");
    // not using cleanup_exit here because it is the child
    _exit(1);
  }

  return result;
}

static string get_process_tmp_dir(const string& cache_dir) {
  static string result;
  if (result.empty()) {
    result = fs::join(cache_dir, SUBDIR_TEMP, format("%lu",
                      (unsigned long)(getpid())));
    enforce_mkdir_p(result);
    register_cleanup_path(result);
  }
  return result;
}

static string get_code_work_dir(const string& base_dir,
                                const string& code_path) {
#ifdef _OPENMP
  ScopedOMPLock lock("code_work_dir_lock");
#endif
  // assume code file doesn't change
  static map<string, string> cache;
  string key = code_path + "///" + base_dir;
  if (cache.count(key)) return cache[key];
  string code_sha1 = sha1(fs::read(code_path));
  string dest = fs::join(base_dir, format("%s/%s", code_sha1.substr(0, 2),
                                          code_sha1.substr(2)));
  cache[key] = dest;
  return dest;
}

static string get_program_work_dir(const string& cache_dir,
                                   const string& code_path, bool contestant) {
  return get_code_work_dir(fs::join(get_process_tmp_dir(cache_dir),
                                   contestant ? "user" : "judge"), code_path);
}

static string get_temp_file_path(const string& cache_dir,
                                 const string& prefix = "", int len = 10) {
  string dest;
#ifdef _OPENMP
  ScopedOMPLock lock("temp_file_path_lock");
#endif
  do {
    string hash = get_random_hash(len);
    dest = fs::join(get_process_tmp_dir(cache_dir),
                    prefix.empty() ? hash : format("%s-%s", prefix, hash));
  } while (fs::exists(dest));
  enforce_mkdir_p(fs::dirname(dest));
  if (!fs::touch(dest)) fatal("can not prepare temp file %s", dest.c_str());
  // no more needed since it is inside the process tmp dir, which will be removed
  // register_cleanup_path(dest);
  return dest;
}

static map<string, string> get_mappings(const string& src_name,
                                        const string& exe_name, const string& dest) {
  map<string, string> mappings;
  mappings["$src"] = src_name;  // basename
  mappings["$exe"] = exe_name;  // basename
  mappings["$dir"] = dest;      // unsandboxed, workdir full path

  return mappings;
}

static CompileResult compile_code(const string& etc_dir,
                                  const string& cache_dir, const string& dest /* work dir */,
                                  const string& code_path, const Limit& limit,
                                  bool is_interactor = false) {
  log_debug("compile_code: %s %s", code_path.c_str(), dest.c_str());

  CompileResult result;
  result.success = false;

  if (!is_language_supported(etc_dir, code_path)) {
    result.error =
      format("Compiling `%s` is not supported. No appropriate config found.",
             fs::basename(code_path));
    return result;
  }

  enforce_mkdir_p(dest);

  do {
    // compile_code is not running in 2 threads. locking processes is enough.
    fs::ScopedFileLock lock(dest);

    string src_name = get_src_name(etc_dir, code_path);
    string dest_code_path = fs::join(dest, src_name);
    if (!fs::exists(dest_code_path)) {
      log_debug("copying code from %s to %s", code_path.c_str(),
                dest_code_path.c_str());
      std::ifstream src_stream(code_path.c_str(), std::ios::binary);
      std::ofstream dst_stream(dest_code_path.c_str(), std::ios::binary);
      dst_stream << src_stream.rdbuf();
    }

    // A configured official header takes precedence over legacy -I include
    // paths for interactors using #include "testlib.h". Work directories are
    // scoped to this invocation, so a header update cannot reuse an old binary.
    if (is_interactor) {
      string header_path = get_config_path(etc_dir, code_path, "testlib.h");
      if (!header_path.empty()) {
        std::ifstream header(header_path.c_str(), std::ios::binary);
        std::ofstream staged(fs::join(dest, "testlib.h").c_str(), std::ios::binary);
        if (!header || !staged) {
          result.error = "cannot stage interactor testlib.h";
          break;
        }
        staged << header.rdbuf();
        staged.flush();
        if (!staged) {
          result.error = "cannot write interactor testlib.h";
          break;
        }
      }
    }

    // string solution_name = get_solution_name(etc_dir, code_path);
    // string dest_solution_code_path = fs::join(dest, solution_name);
    // if (!fs::exists(dest_solution_code_path) && !solution_code_path.empty()) {
    //   log_debug("copying solution code from %s to %s", solution_code_path.c_str(), dest_solution_code_path.c_str());
    //   std::ifstream src_stream(solution_code_path.c_str(), std::ios::binary);
    //   std::ofstream dst_stream(dest_solution_code_path.c_str(), std::ios::binary);
    //   dst_stream << src_stream.rdbuf();
    // }

    std::list<string> compile_cmd = get_config_list(etc_dir, code_path,
                                    ENV_COMPILE EXT_CMD_LIST);
    if (compile_cmd.empty()) {
      result.success = true;
      log_debug("skip compilation because get_config_list() returns nothing");
      break;
    }

    string dest_compile_log_path = fs::join(dest, "compile.log");
    string exe_name = get_config_content(etc_dir, code_path,
                                        ENV_COMPILE EXT_EXE_NAME, DEFAULT_EXE_NAME);
    string dest_exe_path = fs::join(dest, exe_name);
    if (fs::exists(dest_exe_path)) {
      result.success = true;
      log_debug("skip compilation because binary exists: %s", dest_exe_path.c_str());
      result.log = fs::nread(dest_compile_log_path, TRUNC_LOG);
      break;
    }

    string chroot_path = prepare_chroot(etc_dir, code_path, ENV_COMPILE);

    LrunArgs lrun_args;
    lrun_args.append_default();
    lrun_args.append("--chroot", chroot_path);
    lrun_args.append("--bindfs", fs::join(chroot_path, "/tmp"), dest);
    lrun_args.append(limit);

    map<string, string> mappings = get_mappings(src_name, exe_name, dest);
    lrun_args.append(filter_user_lrun_args(escape_list(get_config_list(etc_dir,
                                           code_path, ENV_COMPILE EXT_LRUN_ARGS), mappings), cache_dir));
    lrun_args.append(filter_user_lrun_args(escape_list(get_config_list(etc_dir,
                                           code_path, ENV_EXTRA EXT_LRUN_ARGS), mappings), cache_dir));
    // Override (hide) files using user provided options
    lrun_args.append(get_override_lrun_args(etc_dir, cache_dir, code_path,
                                            ENV_COMPILE, chroot_path));
    lrun_args.append("--");
    lrun_args.append(escape_list(compile_cmd, mappings));

    LrunResult lrun_result = lrun(lrun_args, DEV_NULL, dest_compile_log_path,
                                  dest_compile_log_path, true);

    string log = string_chomp(fs::nread(dest_compile_log_path, TRUNC_LOG));

    // check internal error (mostly lrun can not exec the compiler)
    if (!lrun_result.error.empty()) {
      result.error = lrun_result.error + "\n" + log;
      break;
    }

    // compiler did run. check its status and outputs
    result.log = log;
    if (!lrun_result.exceed.empty()) {
      result.log += format("%sCompiler exceeded %s limit",
                           (log.empty() ? "" : "\n\n"), lrun_result.exceed);
    } else if (lrun_result.signaled) {
      result.log += format("%sCompiler was killed by signal %d\n\n",
                           (log.empty() ? "" : "\n\n"), lrun_result.term_sig);
    } else if (lrun_result.exit_code != 0) {
      // the message is too common. only write to "log" if log is empty
      if (result.log.empty()) result.log = format("Compiler exited with code %d",
                                             lrun_result.exit_code);
    } else if (!fs::exists(dest_exe_path)) {
      if (result.log.empty()) result.log =
          "Compiler did not create the expected binary";
    } else {
      result.success = true;
    }
  } while (false);

  if (!result.success) {
#ifndef NDEBUG
    if (!getenv("DEBUG") && !getenv("NOCLEANUP")) {
#endif
      log_debug("cleaning: rm -rf %s", dest.c_str());
      fs::rm_rf(dest);
#ifndef NDEBUG
    }
#endif
  }
  return result;
}

static LrunResult run_code(
  const string& etc_dir,
  const string& cache_dir,
  const string& dest,
  const string& code_path,
  const Limit& limit,
  const string& stdin_path,
  const string& stdout_path,
  const string& default_exe_name,
  const string& stderr_path = DEV_NULL,
  const vector<string>& extra_lrun_args = vector<string>(),
  const string& env = ENV_RUN,
  const vector<string>& extra_argv = vector<string>(),
  int input_fd = -1, int output_fd = -1
) {
  log_debug("run_code: %s", code_path.c_str());

  string chroot_path = prepare_chroot(etc_dir, code_path, env);
  string exe_name = get_config_content(etc_dir, code_path,
                                      ENV_COMPILE EXT_EXE_NAME, default_exe_name);

  // assume it is precompiled
  {
    // not locking here because the directory is read-only
    // fs::ScopedFileLock lock(dest);
    // A legacy batch wrapper may consume stdin until EOF before starting the
    // program. Interactive protocols require the program to read the live pipe.
    std::list<string> run_cmd = get_config_list(etc_dir, code_path,
                                               "run.stream.cmd_list");
    if (run_cmd.empty()) {
      run_cmd = get_config_list(etc_dir, code_path, ENV_RUN EXT_CMD_LIST);
    }
    if (run_cmd.empty()) {
      // use exe name as fallback
      run_cmd.push_back("./" + exe_name);
    }

    string src_name = get_src_name(etc_dir, code_path);
    map<string, string> mappings = get_mappings(src_name, exe_name, dest);
    mappings["$chroot"] = chroot_path;
    mappings["$jvmmemory"] = format("%Ld", limit.jvm_memory > 0
                                   ? limit.jvm_memory : limit.memory);

    LrunArgs lrun_args;
    lrun_args.append_default();
    lrun_args.append("--chroot", chroot_path);
    lrun_args.append("--bindfs-ro", fs::join(chroot_path, "/tmp"), dest);
    lrun_args.append(get_override_lrun_args(etc_dir, cache_dir, code_path, ENV_RUN,
                                            chroot_path, run_cmd.size() >= 2 ? (*run_cmd.begin()) : "" ));
    lrun_args.append(limit);
    lrun_args.append(escape_list(extra_lrun_args, mappings));
    lrun_args.append(filter_user_lrun_args(escape_list(get_config_list(etc_dir,
                                           code_path, format("%s%s", env, EXT_LRUN_ARGS)), mappings), cache_dir));
    lrun_args.append(filter_user_lrun_args(escape_list(get_config_list(etc_dir,
                                           code_path, ENV_EXTRA EXT_LRUN_ARGS), mappings), cache_dir));
    lrun_args.append("--");
    lrun_args.append(escape_list(run_cmd, mappings));
    lrun_args.append(escape_list(extra_argv, mappings));

    LrunResult run_result = lrun(lrun_args, stdin_path, stdout_path, stderr_path,
                                 false, input_fd, output_fd);

    return run_result;
  }
}

static void write_compile_result(j::object& jo,
                                 const CompileResult& compile_result, const string& key) {
  j::object jco;
  jco["log"] = j::value(compile_result.log);
  if (!compile_result.error.empty()) jco["error"] = j::value(
          compile_result.error);
  jco["success"] = j::value(compile_result.success);
  jo[key] = j::value(jco);
}

static string remove_space(const string& str) {
  string result;
  result.reserve(str.length());
  for (size_t i = 0, l = str.length(); i < l; ++i) {
    if (isspace(str[i])) continue;
    result += str[i];
  }
  return result;
}

static void run_standard_checker(j::object& result, const Testcase& testcase,
                                 const string& user_output_path) {
  log_debug("run_standard_checker: %s %s", testcase.output_path.c_str(),
            user_output_path.c_str());
  bool use_sha1 = !testcase.output_sha1.empty();
  string usr = string_chomp(fs::read(user_output_path));

  if (use_sha1) {
    if (sha1(usr) == testcase.output_sha1) {
      result["result"] = j::value(TestcaseResult::ACCEPTED);
    } else if (!testcase.output_pe_sha1.empty() &&
               sha1(remove_space(usr)) == testcase.output_pe_sha1) {
      result["result"] = j::value(TestcaseResult::PRESENTATION_ERROR);
    } else {
      result["result"] = j::value(TestcaseResult::WRONG_ANSWER);
    }
  } else {
    string out = string_chomp(fs::read(testcase.output_path));
    //string_replacei(out, "\r", "");
    if (usr == out) {
      result["result"] = j::value(TestcaseResult::ACCEPTED);
    } else if (remove_space(usr) == remove_space(out)) {
      result["result"] = j::value(TestcaseResult::PRESENTATION_ERROR);
    } else {
      result["result"] = j::value(TestcaseResult::WRONG_ANSWER);
    }
  }
}

static string get_full_path(const string& path) {
  if (fs::is_absolute(path)) return path;
  return fs::join(get_current_dir_name(), path);
}

static void prepare_checker_mount_bind_files(const string& dest) {
  // prepare files used for mount bind in checker work dir:
  // - input: standard input
  // - output: standard output
  // - user_output: user output
  // - user_code: user code

  // lrun requires non-root users to use full path
  fs::touch(fs::join(dest, "input"));
  fs::touch(fs::join(dest, "output"));
  fs::touch(fs::join(dest, "transcript"));
  fs::touch(fs::join(dest, "slice"));
  fs::touch(fs::join(dest, "user_output"));
  fs::touch(fs::join(dest, "user_code"));
}

static j::object run_testcase(const string& etc_dir, const string& cache_dir,
                              const string& code_path, const string& judge_code_path,
                              const map<string, string>& envs, const Testcase& testcase,
                              bool& has_run_custom_checker, bool skip_checker = false,
                              bool keep_stdout = false, bool keep_stderr = false) {
  log_debug("run_testcase: %s", testcase.input_path.c_str());

  j::object result;
  string stderr_path = testcase.user_stderr_path.empty() ?
                        (keep_stderr ? get_temp_file_path(cache_dir,
                            "err") : DEV_NULL) : testcase.user_stderr_path;
  string judge_stderr = keep_stderr ? get_temp_file_path(cache_dir, "judge-err") : DEV_NULL;
  ScopedPipe user_to_judge, judge_to_user;
  if (!user_to_judge.open_pipe() || !judge_to_user.open_pipe()) {
    result["result"] = j::value(TestcaseResult::INTERNAL_ERROR);
    result["error"] = j::value("cannot create interaction pipes");
    return result;
  }
  LrunArgs judge_args, user_args;
  // The executable directory is read-only and shared by this invocation's
  // cases. Bind a fresh file over its transcript placeholder for each sandbox,
  // so testlib's tout can write without sharing state across parallel cases.
  string transcript_path = get_temp_file_path(cache_dir, "transcript");
  judge_args.append("--bindfs-ro", "$chroot/tmp/input", get_full_path(testcase.input_path));
  judge_args.append("--bindfs-ro", "$chroot/tmp/output", get_full_path(testcase.output_path));
  judge_args.append("--bindfs", "$chroot/tmp/transcript", transcript_path);
  for (auto it = envs.begin(); it != envs.end(); ++it) {
    judge_args.append("--env", it->first, it->second);
    user_args.append("--env", it->first, it->second);
  }
  LrunResult judge = run_code(etc_dir, cache_dir,
      get_program_work_dir(cache_dir, judge_code_path, false), judge_code_path,
      testcase.checker_limit, "", "", DEFAULT_EXE_NAME, judge_stderr,
      judge_args, ENV_RUN, vector<string>{"input", "transcript", "output"},
      user_to_judge.fd[0], judge_to_user.fd[1]);
  LrunResult user = run_code(etc_dir, cache_dir,
      get_program_work_dir(cache_dir, code_path, true), code_path,
      testcase.runtime_limit, "", "", DEFAULT_EXE_NAME, stderr_path,
      user_args, ENV_RUN, vector<string>(), judge_to_user.fd[0], user_to_judge.fd[1]);

  // Only the two children own the communication endpoints now. In particular,
  // a contestant exiting must deliver EOF to an interactor waiting for it.
  user_to_judge.close_all();
  judge_to_user.close_all();
  waitChildrenResult(user);
  waitChildrenResult(judge);
  result["time"] = j::value(user.cpu_time);
  result["memory"] = j::value((double)user.memory);
  string status = TestcaseResult::INTERNAL_ERROR, error;
  bool judge_rejected = judge.error.empty() && judge.exceed.empty() && !judge.signaled &&
                        (judge.exit_code == 1 || judge.exit_code == 2);
  if (!user.error.empty()) {
    error = "contestant sandbox error: " + user.error;
  } else if (!judge.error.empty()) {
    error = "interactor sandbox error: " + judge.error;
  } else if ((!judge.exceed.empty() && judge.exceed != "REAL_TIME") ||
             (judge.signaled && judge.exceed.empty() && judge.term_sig != SIGPIPE)) {
    error = !judge.exceed.empty() ? "interactor exceeded " + judge.exceed + " limit" :
            format("interactor was killed by signal %d", judge.term_sig);
  } else if (judge.exceed.empty() && !judge.signaled &&
             (judge.exit_code < 0 || judge.exit_code > 2)) {
    error = format("unknown interactor exit code %d", judge.exit_code);
  } else if (!user.exceed.empty()) {
    result["exceed"] = j::value(user.exceed);
    if (user.exceed == "CPU_TIME" || user.exceed == "REAL_TIME")
      status = TestcaseResult::TIME_LIMIT_EXCEEDED;
    else if (user.exceed == "MEMORY") status = TestcaseResult::MEMORY_LIMIT_EXCEEDED;
    else if (user.exceed == "OUTPUT") status = TestcaseResult::OUTPUT_LIMIT_EXCEEDED;
  } else if (user.signaled && !(user.term_sig == SIGPIPE && judge_rejected)) {
    status = user.term_sig == SIGSEGV ? TestcaseResult::SEGMENTATION_FAULT :
             user.term_sig == SIGFPE ? TestcaseResult::FLOAT_POINT_EXCEPTION :
             TestcaseResult::RUNTIME_ERROR;
    error = format("contestant was killed by signal %d", user.term_sig);
  } else if (!user.signaled && user.exit_code != 0) {
    status = TestcaseResult::NON_ZERO_EXIT_CODE;
    error = format("contestant exited with code %d", user.exit_code);
  } else if (!judge.exceed.empty()) {
    error = "interactor exceeded " + judge.exceed + " limit";
  } else if (judge.signaled) {
    // SIGPIPE follows the contestant closing its input during the dialogue.
    status = TestcaseResult::WRONG_ANSWER;
    error = "contestant closed the interaction channel";
  } else if (judge.exit_code == 0) {
    status = TestcaseResult::ACCEPTED;
  } else if (judge.exit_code == 1) {
    status = TestcaseResult::WRONG_ANSWER;
  } else if (judge.exit_code == 2) {
    status = TestcaseResult::PRESENTATION_ERROR;
  } else {
    error = format("unknown interactor exit code %d", judge.exit_code);
  }
  if (!error.empty()) result["error"] = j::value(error);
  result["result"] = j::value(status);
  if (keep_stderr) {
    result["stderr"] = j::value(fs::nread(stderr_path, TRUNC_LOG));
    result["judgeStderr"] = j::value(fs::nread(judge_stderr, TRUNC_LOG));
  }
  return result;
}

static j::value run_testcases(const Options& opts) {
  log_debug("nthread = %u", opts.nthread);
#ifdef _OPENMP
  if (opts.nthread > 0) omp_set_num_threads(opts.nthread);
#endif

  vector<j::value> results;
  results.resize(opts.cases.size());
  bool has_run_custom_checker = false;
#ifdef _OPENMP
  #pragma omp parallel for if (opts.nthread != 1 && opts.cases.size() > 1)
#endif
  for (int i = 0; i < (int)opts.cases.size(); ++i) {
    //以用户代码为准，
    j::object testcase_result = run_testcase(opts.etc_dir, opts.cache_dir,
                                opts.solution_code_path, opts.user_code_path, opts.envs, opts.cases[i],
                                has_run_custom_checker, opts.skip_checker, opts.keep_stdout, opts.keep_stderr);
    results[i] = j::value(testcase_result);
  }
  return j::value(results);
}

static void print_with_color(const string& content, int color,
                             FILE* fp = stderr) {
  if (content.empty()) return;

  term::set(term::attr::RESET, color, fp);
  fprintf(fp, "%s", content.c_str());
  if (content[content.length() - 1] != '\n') fprintf(fp, "\n");
  term::set(term::attr::RESET, fp);
}

static void print_final_result(const Options& opts, const j::value& jv) {
  if (opts.direct_mode) {
    // not checking all "contains()" here because direct-mode is not that serious
    string compiler_log = jv.get("compilation").get("log").to_str();
    print_with_color(compiler_log, term::fg::YELLOW);

    if (jv.contains("testcases")) {
      const auto& test_result = jv.get("testcases").get(0);
      printf("%s", test_result.get("stdout").to_str().c_str());
      print_with_color(test_result.get("stderr").to_str(), term::fg::RED);
    }
  } else {
    printf("%s", jv.serialize(opts.pretty_print).c_str());
  }
}

int main(int argc, char const* argv[]) {
  if (argc == 1) print_usage();

  Options opts = parse_cli_options(argc, argv);
  check_options(opts);

  j::object jo;
  bool compiled = true;

  // time(0) is only accurate to seconds, which is not enough, add some pid randomness
  srand((time(0) << 4) | getpid());

  // 编译用户代码
  string dest = get_program_work_dir(opts.cache_dir, opts.solution_code_path, true);
  CompileResult compile_result = compile_code(opts.etc_dir, opts.cache_dir, dest,
                                 opts.solution_code_path, opts.compiler_limit);
  write_compile_result(jo, compile_result, "userCompilation");
  if (!compile_result.success) compiled = false;

  // precompile user code
  if (compiled) {
    string judge_dest = get_program_work_dir(opts.cache_dir, opts.user_code_path, false);
    CompileResult compile_result = compile_code(opts.etc_dir, opts.cache_dir, judge_dest,
                                   opts.user_code_path, opts.compiler_limit, true);
    write_compile_result(jo, compile_result, "judgeCompilation");
    if (!compile_result.success) compiled = false;
    prepare_checker_mount_bind_files(judge_dest);
  }

  if (compiled) {
    j::value results = run_testcases(opts);
    jo["testcases"] = results;
  }

  print_final_result(opts, j::value(jo));
  cleanup_exit(0);
}
