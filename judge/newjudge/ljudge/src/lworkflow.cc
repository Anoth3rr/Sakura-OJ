// Independent process controller for interactive and multi-pass judging.
// Protocol reference: DOMjudge's multi-pass validator contract. No DOMjudge
// source is embedded here; lrun remains responsible for sandboxing and limits.
#include <algorithm>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>
#include "deps/picojson/picojson.h"

namespace fs = std::filesystem;
namespace j = picojson;
using Obj = j::object;
using Arr = j::array;
using Clock = std::chrono::steady_clock;
using std::string;
const size_t MIB = 1024 * 1024;

static void require(bool ok, const string& message) {
  if (!ok) throw std::runtime_error(message);
}
static const j::value& field(const Obj& o, const string& k) {
  auto it = o.find(k);
  require(it != o.end(), "missing field: " + k);
  return it->second;
}
static string str(const Obj& o, const string& k) {
  const auto& v = field(o, k);
  require(v.is<string>() && v.get<string>().find('\0') == string::npos, "invalid string: " + k);
  return v.get<string>();
}
static double number(const Obj& o, const string& k, double low, double high) {
  const auto& v = field(o, k);
  require(v.is<double>() && std::isfinite(v.get<double>()), "invalid number: " + k);
  double n = v.get<double>();
  require(n >= low && n <= high, "out of range: " + k);
  return n;
}
static Obj object(const Obj& o, const string& k) {
  const auto& v = field(o, k);
  require(v.is<Obj>(), "invalid object: " + k);
  return v.get<Obj>();
}
static void set(Obj& o, const string& k, const string& v) { o[k] = j::value(v); }
static void set(Obj& o, const string& k, double v) { o[k] = j::value(v); }

struct FD {
  int n = -1;
  explicit FD(int value = -1): n(value) {}
  FD(const FD&) = delete;
  FD& operator=(const FD&) = delete;
  ~FD() { if (n >= 0) close(n); }
};

// Never follow a jury-created symlink or block on a FIFO while reading reports.
static string read_file(const fs::path& path, size_t limit, bool optional = false) {
  FD fd(open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (fd.n < 0 && errno == ENOENT && optional) return "";
  require(fd.n >= 0, "文件必须是可读取的普通文件: " + path.filename().string());
  struct stat st;
  require(fstat(fd.n, &st) == 0 && S_ISREG(st.st_mode), "文件必须是普通文件: " + path.filename().string());
  string result;
  char buffer[8192];
  while (result.size() < limit) {
    ssize_t n = read(fd.n, buffer, std::min(sizeof(buffer), limit - result.size()));
    if (n < 0 && errno == EINTR) continue;
    require(n >= 0, "cannot read " + path.string());
    if (!n) break;
    result.append(buffer, size_t(n));
  }
  return result;
}
static void write_file(const fs::path& path, const string& data) {
  FD fd(open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC | O_NOFOLLOW, 0600));
  require(fd.n >= 0, "cannot write " + path.string());
  size_t pos = 0;
  while (pos < data.size()) {
    ssize_t n = write(fd.n, data.data() + pos, data.size() - pos);
    if (n < 0 && errno == EINTR) continue;
    require(n > 0, "cannot write " + path.string());
    pos += size_t(n);
  }
}
static string utf8(const string& s) {
  string out;
  for (size_t i = 0; i < s.size();) {
    unsigned char c = s[i];
    size_t n = c < 128 ? 1 : c >= 194 && c <= 223 ? 2 : c >= 224 && c <= 239 ? 3 : c >= 240 && c <= 244 ? 4 : 0;
    bool valid = n && i + n <= s.size();
    for (size_t k = 1; valid && k < n; ++k) valid = (static_cast<unsigned char>(s[i+k]) & 192) == 128;
    if (valid && n > 2) {
      unsigned char d = s[i+1];
      valid = !(c == 224 && d < 160) && !(c == 237 && d >= 160) && !(c == 240 && d < 144) && !(c == 244 && d >= 144);
    }
    if (valid) { out.append(s, i, n); i += n; }
    else { out += "\xef\xbf\xbd"; ++i; }
  }
  return out;
}

static void check_tree(const fs::path& path, size_t max_bytes = 64 * MIB) {
  size_t bytes = 0, count = 0;
  require(fs::is_directory(fs::symlink_status(path)), "artifact/feedback root must be a directory");
  for (const auto& entry : fs::recursive_directory_iterator(path)) {
    auto st = entry.symlink_status();
    require(fs::is_regular_file(st) || fs::is_directory(st), "编译产物和反馈只允许普通文件及目录");
    if (fs::is_regular_file(st)) bytes += entry.file_size();
    require(++count <= 4096 && bytes <= max_bytes, "artifact/feedback size limit exceeded");
  }
}
static void copy_tree(const fs::path& source, const fs::path& target) {
  check_tree(source);
  fs::create_directories(target);
  for (const auto& entry : fs::recursive_directory_iterator(source)) {
    auto dest = target / entry.path().lexically_relative(source);
    if (entry.is_directory()) fs::create_directory(dest);
    else fs::copy_file(entry.path(), dest);
  }
}
static string replace(string s, const string& from, const string& to) {
  size_t pos = 0;
  while ((pos = s.find(from, pos)) != string::npos) { s.replace(pos, from.size(), to); pos += to.size(); }
  return s;
}

struct Pipe {
  int fd[2] = {-1, -1};
  Pipe() {
    require(pipe2(fd, O_CLOEXEC) == 0, "pipe2 failed");
    // Descriptors 0..3 are reserved for stdio and lrun's status channel.
    for (int& n : fd) if (n < 4) {
      int next = fcntl(n, F_DUPFD_CLOEXEC, 4);
      require(next >= 4, "cannot reserve pipe descriptor");
      close(n); n = next;
    }
  }
  void close_all() { for (int& n : fd) if (n >= 0) { close(n); n = -1; } }
  ~Pipe() { close_all(); }
};

struct Child {
  pid_t pid = -1;
  bool done = false;
  int status = 0;
  fs::path control;
  Clock::time_point deadline;
  size_t output_limit;
  Child(const Child&) = delete;
  Child& operator=(const Child&) = delete;
  Child(): output_limit(0) {}
  void stop() noexcept {
    if (pid <= 0 || done) return;
    // Give lrun's signal handler time to kill/reap its sandbox and cgroup.
    kill(-pid, SIGTERM);
    for (int i = 0; i < 200; ++i) {
      if (waitpid(pid, &status, WNOHANG) == pid) { done = true; return; }
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    kill(-pid, SIGKILL);
    while (waitpid(pid, &status, 0) < 0 && errno == EINTR) {}
    done = true;
  }
  ~Child() { stop(); }
};

static void wait_all(std::initializer_list<Child*> children) {
  while (true) {
    bool all = true;
    for (Child* child : children) {
      if (child->done) continue;
      pid_t ret = waitpid(child->pid, &child->status, WNOHANG);
      if (ret == child->pid) child->done = true;
      else if (ret < 0 && errno != EINTR) throw std::runtime_error("cannot wait for sandbox");
      else {
        all = false;
        require(Clock::now() < child->deadline, "沙箱监督进程未正常退出");
      }
    }
    if (all) return;
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }
}

struct Result {
  Obj report;
  string output;
};

static Result finish(Child& child, bool captured = true) {
  require(child.done, "sandbox was not reaped");
  string errors = utf8(read_file(child.control / "stderr", 16384));
  require(WIFEXITED(child.status) && WEXITSTATUS(child.status) == 0, "沙箱启动失败: " + errors);
  std::istringstream lines(read_file(child.control / "status", 4096));
  std::map<string, string> fields;
  string line, key, value, extra;
  while (std::getline(lines, line)) {
    std::istringstream row(line);
    require(bool(row >> key >> value) && !(row >> extra) && !fields.count(key), "invalid lrun status");
    fields[key] = value;
  }
  std::set<string> expected = {"MEMORY", "CPUTIME", "REALTIME", "SIGNALED", "EXITCODE", "TERMSIG", "EXCEED"};
  require(fields.size() == expected.size(), "incomplete lrun status");
  for (const auto& k : expected) require(fields.count(k), "incomplete lrun status");
  auto numeric = [&](const string& k, double high, bool integer) {
    size_t pos;
    double n = std::stod(fields[k], &pos);
    require(pos == fields[k].size() && std::isfinite(n) && n >= 0 && n <= high && (!integer || n == std::floor(n)), "invalid lrun status number");
    return n;
  };
  double memory = numeric("MEMORY", 1e18, true), cpu = numeric("CPUTIME", 1e12, false), wall = numeric("REALTIME", 1e12, false);
  int sig = int(numeric("SIGNALED", 1, true)), exit_code = int(numeric("EXITCODE", 255, true));
  int term = int(numeric("TERMSIG", NSIG - 1, true));
  string exceed = fields["EXCEED"], verdict = "OK";
  require(exceed == "none" || exceed == "MEMORY" || exceed == "CPU_TIME" || exceed == "REAL_TIME" || exceed == "OUTPUT", "invalid lrun limit");
  if (exceed == "MEMORY") verdict = "MLE";
  else if (exceed == "CPU_TIME" || exceed == "REAL_TIME") verdict = "TLE";
  else if (exceed == "OUTPUT") verdict = "OLE";
  else if (sig || exit_code) verdict = "RE";
  Result r;
  set(r.report, "verdict", verdict); set(r.report, "time_ms", std::round(cpu * 1e6) / 1000);
  set(r.report, "wall_ms", std::round(wall * 1e6) / 1000); set(r.report, "memory_kb", std::round(memory / 1024));
  set(r.report, "exit_code", exit_code); set(r.report, "signal", sig ? term : 0);
  set(r.report, "exceed", exceed); set(r.report, "stderr", errors);
  if (captured) r.output = read_file(child.control / "stdout", child.output_limit + 1);
  return r;
}

class Session {
  fs::path root;
  int serial = 0;
public:
  fs::path feedback;
  explicit Session(const fs::path& parent) {
    require(fs::is_directory(parent), "work_root is not a directory");
    string pattern = (parent / "workflow-XXXXXX").string();
    std::vector<char> name(pattern.begin(), pattern.end()); name.push_back(0);
    require(mkdtemp(name.data()) != nullptr, "cannot create work directory");
    root = name.data(); feedback = root / "feedback";
    fs::create_directory(feedback);
  }
  ~Session() {
    try {
      // Submissions may chmod their writable work directories. Do not follow
      // links while restoring directory permissions for cleanup.
      std::vector<fs::path> pending = {root};
      while (!pending.empty()) {
        auto p = pending.back(); pending.pop_back();
        fs::permissions(p, fs::perms::owner_all, fs::perm_options::add);
        for (const auto& entry : fs::directory_iterator(p))
          if (fs::is_directory(entry.symlink_status())) pending.push_back(entry.path());
      }
      fs::remove_all(root);
    } catch (const std::exception& e) { std::cerr << "cleanup failed: " << e.what() << '\n'; }
  }
  fs::path save(const string& name, const string& data) {
    auto path = root / name; write_file(path, data); return path;
  }
  fs::path stage(const Obj& spec, const string& label) {
    fs::path work = root / (label + "-" + std::to_string(++serial));
    copy_tree(str(spec, "artifacts"), work);
    for (const string key : {"files", "directories"}) {
      auto it = spec.find(key);
      if (it == spec.end()) continue;
      require(it->second.is<Arr>(), "invalid staged paths");
      for (const auto& name : it->second.get<Arr>()) {
        require(name.is<string>(), "invalid staged name");
        string n = name.get<string>();
        require(n == "input" || n == "answer" || n == "output" || n == "feedback", "invalid staged name");
        require(!fs::exists(work / n), "reserved filename in compiler output: " + n);
        if (key == "files") write_file(work / n, "");
        else fs::create_directory(work / n);
      }
    }
    return work;
  }
  std::unique_ptr<Child> spawn(const Obj& spec, const fs::path& work, const fs::path& input,
                             const fs::path& answer, int in = -1, int out = -1,
                             const string& phase = "", int pass = 1, const fs::path& output = {}) {
    std::unique_ptr<Child> child(new Child);
    child->control = root / ("control-" + std::to_string(++serial));
    fs::create_directory(child->control);
    child->output_limit = size_t(number(spec, "output_limit", 1, 64 * MIB));
    double wall = number(spec, "wall_limit", 0.01, 3600);
    auto command = field(spec, "command");
    require(command.is<Arr>() && !command.get<Arr>().empty() && command.get<Arr>().size() <= 1024, "invalid command");
    std::vector<string> tokens;
    for (const auto& token : command.get<Arr>()) {
      require(token.is<string>() && token.get<string>().find('\0') == string::npos, "invalid command argument");
      string s = token.get<string>();
      for (auto pair : std::map<string, string>{{"@WORK@", work.string()}, {"@INPUT@", input.string()},
           {"@ANSWER@", answer.string()}, {"@OUTPUT@", output.string()}, {"@FEEDBACK@", feedback.string()},
           {"@PHASE@", phase}, {"@PASS@", std::to_string(pass)}}) s = replace(s, pair.first, pair.second);
      tokens.push_back(s);
    }
    std::vector<char*> argv;
    for (auto& token : tokens) argv.push_back(&token[0]);
    argv.push_back(nullptr);
    FD input_fd(in < 0 ? open(input.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW) : -1);
    FD output_fd(out < 0 ? open((child->control / "stdout").c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600) : -1);
    FD error_fd(open((child->control / "stderr").c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600));
    FD status_fd(open((child->control / "status").c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600));
    if (in < 0) in = input_fd.n;
    if (out < 0) out = output_fd.n;
    require(in >= 0 && out >= 0 && error_fd.n >= 0 && status_fd.n >= 0, "cannot open sandbox streams");
    child->pid = fork();
    require(child->pid >= 0, "fork failed");
    if (!child->pid) {
      setpgid(0, 0);
      prctl(PR_SET_PDEATHSIG, SIGTERM);
      if (dup2(in, 0) < 0 || dup2(out, 1) < 0 || dup2(error_fd.n, 2) < 0 || dup2(status_fd.n, 3) < 0) _exit(127);
      // All other owned descriptors are CLOEXEC. No shell command is evaluated.
      execvp(argv[0], argv.data());
      _exit(127);
    }
    setpgid(child->pid, child->pid);
    child->deadline = Clock::now() + std::chrono::milliseconds(int((wall + 12) * 1000));
    return child;
  }
  Result run(const Obj& spec, const fs::path& input, const fs::path& answer,
             const string& phase = "", int pass = 1, const fs::path& stdin_path = {},
             const fs::path& output = {}) {
    auto work = stage(spec, "run");
    FD stdin_fd(stdin_path.empty() ? -1 : open(stdin_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    require(stdin_path.empty() || stdin_fd.n >= 0, "cannot open validator input");
    auto child = spawn(spec, work, input, answer, stdin_fd.n, -1, phase, pass, output);
    wait_all({child.get()});
    return finish(*child);
  }
  Result interactive(const Obj& req, bool require_transcript = false) {
    Obj user_spec = object(req, "program"), judge_spec = object(req, "interactor");
    auto userdir = stage(user_spec, "contestant"), judgedir = stage(judge_spec, "interactor");
    Pipe u2j, j2u;
    auto judge = spawn(judge_spec, judgedir, str(req, "input"), str(req, "answer"), u2j.fd[0], j2u.fd[1]);
    auto user = spawn(user_spec, userdir, str(req, "input"), str(req, "answer"), j2u.fd[0], u2j.fd[1]);
    u2j.close_all(); j2u.close_all();
    wait_all({user.get(), judge.get()});
    Result ur = finish(*user, false), jr = finish(*judge, false);
    string verdict = str(ur.report, "verdict"), exceed = str(jr.report, "exceed");
    int jsig = int(jr.report["signal"].get<double>()), jexit = int(jr.report["exit_code"].get<double>());
    int usig = int(ur.report["signal"].get<double>());
    bool rejected = exceed == "none" && !jsig && (jexit == 1 || jexit == 2);
    if ((exceed != "none" && exceed != "REAL_TIME") || (jsig && jsig != SIGPIPE)) verdict = "IE";
    else if (!jsig && exceed == "none" && jexit != 0 && jexit != 1 && jexit != 2) verdict = "IE";
    else if (usig == SIGPIPE && rejected) verdict = jexit == 1 ? "WA" : "PE";
    else if (verdict == "OK") {
      if (exceed != "none") verdict = "IE";
      else if (jsig == SIGPIPE) verdict = "WA";
      else verdict = jexit == 0 ? "OK" : jexit == 1 ? "WA" : "PE";
    }
    ur.output = read_file(judgedir / "transcript", 8 * MIB + 1, !require_transcript || verdict != "OK");
    require(ur.output.size() <= 8 * MIB, "interactor 的交互记录超过 8 MiB");
    set(ur.report, "verdict", verdict); set(ur.report, "judge_stderr", str(jr.report, "stderr"));
    ur.report["interactor"] = j::value(jr.report);
    return ur;
  }
  // Compatibility with testlib communication packages: the interactor's tout
  // is the next input, not the contestant's raw output. The second invocation
  // receives a fresh artifact tree, just as each DOMjudge-style pass does.
  Result communication(const Obj& req) {
    auto program = object(req, "program"), checker = object(req, "checker");
    Result first = interactive(req, true);
    set(first.report, "pass", 1); set(first.report, "phase", "first");
    Arr phases = {j::value(first.report)};
    size_t transferred = first.output.size();
    set(first.report, "passes", 1); set(first.report, "message_bytes", transferred);
    first.report["phases"] = j::value(phases);
    set(first.report, "message", str(first.report, "judge_stderr"));
    if (str(first.report, "verdict") != "OK") {
      first.output.clear(); // There was no second-run output.
      return first;
    }

    auto second = run(program, save("next-input", first.output), str(req, "answer"), "second", 2);
    set(second.report, "pass", 2); set(second.report, "phase", "second");
    if (str(second.report, "verdict") == "OK") {
      auto actual = save("candidate-output", second.output);
      auto checked = run(checker, str(req, "input"), str(req, "answer"), "check", 2,
                         save("checker-stdin", ""), actual);
      bool normal = str(checked.report, "exceed") == "none" && checked.report["signal"].get<double>() == 0;
      int code = int(checked.report["exit_code"].get<double>());
      string verdict = !normal ? "IE" : code == 0 ? "AC" : code == 1 ? "WA" : code == 2 ? "PE" : "IE";
      set(checked.report, "verdict", verdict);
      second.report["checker"] = j::value(checked.report);
      set(second.report, "verdict", verdict);
      set(second.report, "judge_stderr", str(checked.report, "stderr"));
      set(second.report, "message", str(checked.report, "stderr"));
    }
    phases.push_back(j::value(second.report));
    second.report["phases"] = j::value(phases);
    set(second.report, "passes", 2); set(second.report, "message_bytes", transferred);
    for (const string key : {"time_ms", "wall_ms"})
      set(second.report, key, first.report[key].get<double>() + second.report[key].get<double>());
    set(second.report, "memory_kb", std::max(first.report["memory_kb"].get<double>(), second.report["memory_kb"].get<double>()));
    return second;
  }
  Result twice(const Obj& req) {
    size_t maximum = size_t(number(req, "message_bytes", 1, MIB));
    auto first = run(object(req, "program"), str(req, "input"), str(req, "answer"), "send");
    Arr phases = {j::value(first.report)};
    set(first.report, "message_bytes", first.output.size()); set(first.report, "phase", "send");
    first.report["phases"] = j::value(phases);
    if (first.output.size() > maximum) { set(first.report, "verdict", "CLE"); return first; }
    if (str(first.report, "verdict") != "OK") return first;
    auto second = run(object(req, "receiver"), save("message", first.output), str(req, "answer"), "receive", 2);
    phases.push_back(j::value(second.report));
    second.report["phases"] = j::value(phases);
    set(second.report, "phase", "receive"); set(second.report, "message_bytes", first.output.size());
    set(second.report, "time_ms", first.report["time_ms"].get<double>() + second.report["time_ms"].get<double>());
    set(second.report, "memory_kb", std::max(first.report["memory_kb"].get<double>(), second.report["memory_kb"].get<double>()));
    return second;
  }
  Result multipass(const Obj& req) {
    double bound = number(req, "validation_passes", 1, 32);
    require(bound == std::floor(bound), "validation_passes must be an integer");
    int passes = int(bound);
    auto program = object(req, "program"), validator = object(req, "validator");
    fs::path input = str(req, "input"), answer = str(req, "answer");
    Arr phases;
    Result result;
    double cpu = 0, memory = 0;
    size_t transferred = 0;
    for (int pass = 1; pass <= passes; ++pass) {
      result = run(program, input, answer, "", pass);
      cpu += result.report["time_ms"].get<double>();
      memory = std::max(memory, result.report["memory_kb"].get<double>());
      Obj stage = result.report;
      set(stage, "pass", pass);
      if (str(result.report, "verdict") != "OK") { phases.push_back(j::value(stage)); break; }
      auto checked = run(validator, input, answer, "", pass, save("candidate-output", result.output));
      set(result.report, "judge_stderr", str(checked.report, "stderr"));
      set(result.report, "message", str(checked.report, "stderr"));
      auto next = feedback / "nextpass.in";
      bool exists = fs::symlink_status(next).type() != fs::file_type::not_found;
      bool accepted = str(checked.report, "exceed") == "none" && checked.report["signal"].get<double>() == 0 && checked.report["exit_code"].get<double>() == 42;
      bool rejected = str(checked.report, "exceed") == "none" && checked.report["signal"].get<double>() == 0 && checked.report["exit_code"].get<double>() == 43;
      set(checked.report, "verdict", accepted ? "AC" : rejected ? "WA" : "IE");
      stage["validator"] = j::value(checked.report);
      phases.push_back(j::value(stage));
      if ((!accepted && !rejected) || (exists && !accepted)) {
        set(result.report, "verdict", "IE");
        string message = exists ? "validator 生成 nextpass.in 时必须返回 42" : "validator 必须正常返回 42 或 43";
        string diagnostic = utf8(read_file(feedback / "judgeerror.txt", 16384, true));
        if (!diagnostic.empty()) message += "\n" + diagnostic;
        set(result.report, "message", message);
        break;
      }
      check_tree(feedback, 16 * MIB);
      string message = utf8(read_file(feedback / "judgemessage.txt", 16384, true));
      if (!message.empty()) set(result.report, "message", message);
      if (rejected) { set(result.report, "verdict", "WA"); break; }
      if (!exists) { set(result.report, "verdict", "AC"); break; }
      if (pass == passes) {
        set(result.report, "verdict", "IE");
        set(result.report, "message", "validator 请求的轮数超过 validation_passes");
        break;
      }
      string data = read_file(next, 8 * MIB + 1);
      require(data.size() <= 8 * MIB, "nextpass.in 超过 8 MiB");
      transferred += data.size();
      input = save("next-input", data);
      // Other feedback persists, but the old request must not trigger another
      // pass unless the validator explicitly creates a new nextpass.in.
      fs::remove(next);
    }
    result.report["phases"] = j::value(phases);
    set(result.report, "passes", phases.size()); set(result.report, "message_bytes", transferred);
    set(result.report, "time_ms", cpu); set(result.report, "memory_kb", memory);
    return result;
  }
};

int main(int argc, char** argv) {
  if (argc == 2 && string(argv[1]) == "--help") {
    std::cout << "lworkflow --request manifest.json --output result.bin\n"
                 "JSON v1 modes: interactive, communication, run-twice, multipass. Prints a JSON report.\n"
                 "Run as the dedicated non-root judge account; programs are already compiled.\n";
    return 0;
  }
  try {
    require(getuid() != 0, "lworkflow must run as a non-root judge account");
    require(argc == 5 && string(argv[1]) == "--request" && string(argv[3]) == "--output", "use --help for invocation");
    j::value value;
    string data = read_file(argv[2], 4 * MIB + 1);
    std::istringstream input(data);
    require(data.size() <= 4 * MIB && j::parse(value, input).empty() && value.is<Obj>(), "invalid request JSON");
    input >> std::ws;
    require(input.eof(), "trailing data in request JSON");
    auto req = value.get<Obj>();
    require(number(req, "version", 1, 1) == 1, "unsupported request version");
    Session session(str(req, "work_root"));
    string mode = str(req, "mode");
    Result result;
    if (mode == "interactive") result = session.interactive(req);
    else if (mode == "communication") result = session.communication(req);
    else if (mode == "run-twice") result = session.twice(req);
    else if (mode == "multipass") result = session.multipass(req);
    else throw std::runtime_error("unsupported workflow mode");
    write_file(argv[4], result.output);
    set(result.report, "backend", "lworkflow / lrun");
    std::cout << j::value(result.report).serialize() << '\n';
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
  return 0;
}
