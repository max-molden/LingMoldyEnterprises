#include <FL/Fl.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Choice.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Window.H>

#include <cerrno>
#include <charconv>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <limits>
#include <optional>
#include <sstream>
#include <string>

namespace {

constexpr int kWindowWidth = 430;
constexpr int kWindowHeight = 240;
constexpr std::size_t kMaxInputLength = 64;
constexpr double kZeroTolerance = 1e-15;

bool is_allowed_char(char c) {
    return (c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-' || c == 'e' || c == 'E';
}

std::optional<double> parse_double_strict(const char* raw) {
    if (raw == nullptr) {
        return std::nullopt;
    }

    const std::string s(raw);
    if (s.empty() || s.size() > kMaxInputLength) {
        return std::nullopt;
    }

    for (const char c : s) {
        if (!is_allowed_char(c)) {
            return std::nullopt;
        }
    }

    double value = 0.0;
    const char* begin = s.data();
    const char* end = s.data() + s.size();
    const auto result = std::from_chars(begin, end, value, std::chars_format::general);

    if (result.ec != std::errc() || result.ptr != end || !std::isfinite(value)) {
        return std::nullopt;
    }

    return value;
}

std::string format_double(double value) {
    std::ostringstream out;
    out.setf(std::ios::fixed, std::ios::floatfield);
    out << std::setprecision(10) << value;
    return out.str();
}

struct AppState {
    Fl_Input* lhs_input = nullptr;
    Fl_Input* rhs_input = nullptr;
    Fl_Choice* op_choice = nullptr;
    Fl_Box* result_box = nullptr;
};

void set_result(Fl_Box* box, const std::string& text) {
    if (box == nullptr) {
        return;
    }
    box->copy_label(text.c_str());
    box->redraw();
}

void on_calculate(Fl_Widget*, void* user_data) {
    auto* state = static_cast<AppState*>(user_data);
    if (state == nullptr || state->lhs_input == nullptr || state->rhs_input == nullptr ||
        state->op_choice == nullptr || state->result_box == nullptr) {
        return;
    }

    const std::optional<double> lhs = parse_double_strict(state->lhs_input->value());
    const std::optional<double> rhs = parse_double_strict(state->rhs_input->value());

    if (!lhs.has_value() || !rhs.has_value()) {
        set_result(state->result_box, "Error: Enter valid numeric inputs.");
        return;
    }

    const int op_idx = state->op_choice->value();
    double result = 0.0;

    switch (op_idx) {
        case 0:
            result = *lhs + *rhs;
            break;
        case 1:
            result = *lhs - *rhs;
            break;
        case 2:
            result = *lhs * *rhs;
            break;
        case 3:
            if (std::fabs(*rhs) <= kZeroTolerance) {
                set_result(state->result_box, "Error: Division by zero.");
                return;
            }
            result = *lhs / *rhs;
            break;
        default:
            set_result(state->result_box, "Error: Unknown operation.");
            return;
    }

    if (!std::isfinite(result)) {
        set_result(state->result_box, "Error: Non-finite result.");
        return;
    }

    set_result(state->result_box, "Result: " + format_double(result));
}

}  // namespace

int main() {
    Fl_Window window(kWindowWidth, kWindowHeight, "SecureCalc");

    Fl_Box title(20, 12, 390, 24, "SecureCalc - Safe C++ Calculator");
    title.labelsize(16);

    Fl_Input lhs_input(20, 50, 180, 30, "A:");
    lhs_input.align(FL_ALIGN_TOP_LEFT);
    lhs_input.maximum_size(static_cast<int>(kMaxInputLength));

    Fl_Input rhs_input(230, 50, 180, 30, "B:");
    rhs_input.align(FL_ALIGN_TOP_LEFT);
    rhs_input.maximum_size(static_cast<int>(kMaxInputLength));

    Fl_Choice op_choice(20, 105, 120, 30, "Operation:");
    op_choice.align(FL_ALIGN_TOP_LEFT);
    op_choice.add("+");
    op_choice.add("-");
    op_choice.add("*");
    op_choice.add("/");
    op_choice.value(0);

    Fl_Button calc_button(160, 105, 110, 32, "Calculate");
    Fl_Box result_box(20, 158, 390, 45, "Result:");
    result_box.box(FL_DOWN_BOX);
    result_box.align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE);
    result_box.labelsize(14);

    AppState state{};
    state.lhs_input = &lhs_input;
    state.rhs_input = &rhs_input;
    state.op_choice = &op_choice;
    state.result_box = &result_box;

    calc_button.callback(on_calculate, &state);

    window.end();
    window.resizable(&window);
    window.show();

    return Fl::run();
}
