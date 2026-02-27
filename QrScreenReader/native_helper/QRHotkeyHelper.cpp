#include <windows.h>
#include <shellapi.h>

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <cwctype>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

namespace {
constexpr UINT kHotkeyId = 100;
constexpr wchar_t kHelperMutexName[] = L"Local\\QrScreenReaderHotkeyHelperMutex";
constexpr wchar_t kReloadEventName[] = L"Local\\QrScreenReaderHotkeyReload";

struct AppConfig {
    bool hotkey_enabled = true;
    std::wstring hotkey = L"Win+Shift+Q";
};

std::wstring Utf8ToWide(const std::string& input) {
    if (input.empty()) {
        return L"";
    }
    int size = MultiByteToWideChar(CP_UTF8, 0, input.c_str(), -1, nullptr, 0);
    if (size <= 0) {
        return L"";
    }
    std::wstring output(static_cast<size_t>(size), L'\0');
    MultiByteToWideChar(CP_UTF8, 0, input.c_str(), -1, output.data(), size);
    if (!output.empty() && output.back() == L'\0') {
        output.pop_back();
    }
    return output;
}

std::string WideToUtf8(const std::wstring& input) {
    if (input.empty()) {
        return "";
    }
    int size = WideCharToMultiByte(CP_UTF8, 0, input.c_str(), -1, nullptr, 0, nullptr, nullptr);
    if (size <= 0) {
        return "";
    }
    std::string output(static_cast<size_t>(size), '\0');
    WideCharToMultiByte(CP_UTF8, 0, input.c_str(), -1, output.data(), size, nullptr, nullptr);
    if (!output.empty() && output.back() == '\0') {
        output.pop_back();
    }
    return output;
}

std::wstring Trim(const std::wstring& value) {
    const auto is_space = [](wchar_t c) { return std::iswspace(static_cast<wint_t>(c)) != 0; };
    size_t start = 0;
    while (start < value.size() && is_space(value[start])) {
        ++start;
    }
    size_t end = value.size();
    while (end > start && is_space(value[end - 1])) {
        --end;
    }
    return value.substr(start, end - start);
}

std::wstring ToUpper(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(),
                   [](wchar_t c) { return static_cast<wchar_t>(std::towupper(static_cast<wint_t>(c))); });
    return value;
}

std::wstring GetConfigPath() {
    wchar_t* appdata_raw = nullptr;
    size_t len = 0;
    if (_wdupenv_s(&appdata_raw, &len, L"APPDATA") != 0 || appdata_raw == nullptr || len == 0) {
        if (appdata_raw != nullptr) {
            free(appdata_raw);
        }
        return L"";
    }

    std::wstring appdata(appdata_raw);
    free(appdata_raw);
    return appdata + L"\\QrScreenReader\\config.json";
}

std::wstring ReadFileText(const std::wstring& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) {
        return L"";
    }

    std::ostringstream ss;
    ss << file.rdbuf();
    return Utf8ToWide(ss.str());
}

bool ReadJsonBool(const std::wstring& json, const std::wstring& key, bool default_value) {
    std::wstring needle = L"\"" + key + L"\"";
    size_t key_pos = json.find(needle);
    if (key_pos == std::wstring::npos) {
        return default_value;
    }

    size_t colon = json.find(L':', key_pos + needle.size());
    if (colon == std::wstring::npos) {
        return default_value;
    }

    size_t value_start = json.find_first_not_of(L" \t\r\n", colon + 1);
    if (value_start == std::wstring::npos) {
        return default_value;
    }

    if (json.compare(value_start, 4, L"true") == 0) {
        return true;
    }
    if (json.compare(value_start, 5, L"false") == 0) {
        return false;
    }

    return default_value;
}

std::wstring ReadJsonString(const std::wstring& json, const std::wstring& key, const std::wstring& default_value) {
    std::wstring needle = L"\"" + key + L"\"";
    size_t key_pos = json.find(needle);
    if (key_pos == std::wstring::npos) {
        return default_value;
    }

    size_t colon = json.find(L':', key_pos + needle.size());
    if (colon == std::wstring::npos) {
        return default_value;
    }

    size_t quote_start = json.find(L'\"', colon + 1);
    if (quote_start == std::wstring::npos) {
        return default_value;
    }

    std::wstring result;
    for (size_t i = quote_start + 1; i < json.size(); ++i) {
        wchar_t c = json[i];
        if (c == L'\\') {
            if (i + 1 < json.size()) {
                result.push_back(json[i + 1]);
                ++i;
            }
            continue;
        }
        if (c == L'\"') {
            return result.empty() ? default_value : result;
        }
        result.push_back(c);
    }

    return default_value;
}

AppConfig LoadConfig() {
    AppConfig cfg;
    std::wstring path = GetConfigPath();
    if (path.empty()) {
        return cfg;
    }

    std::wstring json = ReadFileText(path);
    if (json.empty()) {
        return cfg;
    }

    cfg.hotkey_enabled = ReadJsonBool(json, L"hotkey_enabled", true);
    cfg.hotkey = ReadJsonString(json, L"hotkey", L"Win+Shift+Q");
    return cfg;
}

bool ParseHotkey(const std::wstring& hotkey_text, UINT& modifiers, UINT& vk) {
    modifiers = 0;
    vk = 0;

    std::wstring remaining = hotkey_text;
    size_t pos = 0;
    std::wstring key_token;

    while (true) {
        size_t plus = remaining.find(L'+', pos);
        std::wstring token = plus == std::wstring::npos ? remaining.substr(pos) : remaining.substr(pos, plus - pos);
        token = ToUpper(Trim(token));

        if (!token.empty()) {
            if (token == L"WIN" || token == L"WINDOWS") {
                modifiers |= MOD_WIN;
            } else if (token == L"SHIFT") {
                modifiers |= MOD_SHIFT;
            } else if (token == L"CTRL" || token == L"CONTROL") {
                modifiers |= MOD_CONTROL;
            } else if (token == L"ALT") {
                modifiers |= MOD_ALT;
            } else {
                if (!key_token.empty()) {
                    return false;
                }
                key_token = token;
            }
        }

        if (plus == std::wstring::npos) {
            break;
        }
        pos = plus + 1;
    }

    if (key_token.empty()) {
        return false;
    }

    if (key_token.size() == 1 && ((key_token[0] >= L'A' && key_token[0] <= L'Z') || (key_token[0] >= L'0' && key_token[0] <= L'9'))) {
        vk = static_cast<UINT>(key_token[0]);
        return true;
    }

    if (key_token.size() >= 2 && key_token[0] == L'F') {
        int fn = _wtoi(key_token.c_str() + 1);
        if (fn >= 1 && fn <= 24) {
            vk = static_cast<UINT>(VK_F1 + (fn - 1));
            return true;
        }
    }

    return false;
}

std::wstring GetExecutableDir() {
    wchar_t path[MAX_PATH] = {0};
    DWORD len = GetModuleFileNameW(nullptr, path, MAX_PATH);
    if (len == 0 || len >= MAX_PATH) {
        return L"";
    }

    std::wstring full(path, len);
    size_t pos = full.find_last_of(L"\\/");
    if (pos == std::wstring::npos) {
        return L"";
    }
    return full.substr(0, pos);
}

bool FileExists(const std::wstring& path) {
    DWORD attrs = GetFileAttributesW(path.c_str());
    return attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

std::wstring ParentDir(const std::wstring& path) {
    size_t pos = path.find_last_of(L"\\/");
    if (pos == std::wstring::npos) {
        return L"";
    }
    return path.substr(0, pos);
}

void LaunchSnipWindow() {
    std::wstring dir = GetExecutableDir();
    if (dir.empty()) {
        return;
    }

    std::wstring app = dir + L"\\QRScreenReader.exe";
    std::wstring args = L"--mode snip --disable-hotkey";
    if (FileExists(app)) {
        ShellExecuteW(nullptr, L"open", app.c_str(), args.c_str(), dir.c_str(), SW_SHOWNORMAL);
        return;
    }

    // Dev fallback: helper may run from QrScreenReader\build-helper while app runs via run_dev.bat.
    std::wstring project_dir = ParentDir(dir);
    if (project_dir.empty()) {
        return;
    }

    std::wstring run_dev = project_dir + L"\\run_dev.bat";
    if (!FileExists(run_dev)) {
        return;
    }

    std::wstring cmd_args = L"/c \"\"" + run_dev + L"\" --mode snip --disable-hotkey\"";
    ShellExecuteW(nullptr, L"open", L"cmd.exe", cmd_args.c_str(), project_dir.c_str(), SW_SHOWNORMAL);
}

bool RegisterConfiguredHotkey(const AppConfig& cfg, bool& registered) {
    if (registered) {
        UnregisterHotKey(nullptr, kHotkeyId);
        registered = false;
    }

    if (!cfg.hotkey_enabled) {
        return true;
    }

    UINT mods = 0;
    UINT vk = 0;
    if (!ParseHotkey(cfg.hotkey, mods, vk)) {
        return false;
    }

    if (!RegisterHotKey(nullptr, kHotkeyId, mods, vk)) {
        return false;
    }

    registered = true;
    return true;
}

}  // namespace

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    HANDLE single_instance = CreateMutexW(nullptr, TRUE, kHelperMutexName);
    if (single_instance == nullptr) {
        return 1;
    }
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        CloseHandle(single_instance);
        return 0;
    }

    HANDLE reload_event = CreateEventW(nullptr, FALSE, FALSE, kReloadEventName);

    bool registered = false;
    AppConfig cfg = LoadConfig();
    RegisterConfiguredHotkey(cfg, registered);

    MSG msg;
    while (true) {
        HANDLE handles[1];
        DWORD count = 0;
        if (reload_event != nullptr) {
            handles[count++] = reload_event;
        }

        DWORD result = MsgWaitForMultipleObjects(count, handles, FALSE, INFINITE, QS_ALLINPUT);
        if (reload_event != nullptr && result == WAIT_OBJECT_0) {
            cfg = LoadConfig();
            RegisterConfiguredHotkey(cfg, registered);
            continue;
        }

        while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) {
                if (registered) {
                    UnregisterHotKey(nullptr, kHotkeyId);
                }
                if (reload_event != nullptr) {
                    CloseHandle(reload_event);
                }
                CloseHandle(single_instance);
                return 0;
            }

            if (msg.message == WM_HOTKEY && msg.wParam == kHotkeyId) {
                LaunchSnipWindow();
            }

            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }
}
