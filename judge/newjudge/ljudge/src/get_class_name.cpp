#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <boost/algorithm/string.hpp>
#include <boost/xpressive/xpressive_dynamic.hpp>
#include <boost/wave.hpp>
#include <boost/wave/cpplexer/cpp_lex_token.hpp>
#include <boost/wave/cpplexer/cpp_lex_iterator.hpp>

#define MAX_LINE 11000
#define DEFAULT_CLASS_NAME "Solution"

using namespace boost::xpressive;

std::string strip_comments(std::string const& input) {
	std::string output;
	typedef boost::wave::cpplexer::lex_token<> token_type;
	typedef boost::wave::cpplexer::lex_iterator<token_type> lexer_type;
	typedef token_type::position_type position_type;

	position_type pos;

	lexer_type it = lexer_type(input.begin(), input.end(), pos,
			boost::wave::language_support(
					boost::wave::support_cpp
							| boost::wave::support_option_long_long));
	lexer_type end = lexer_type();

	for (; it != end; ++it) {
		if (*it != boost::wave::T_CCOMMENT
				&& *it != boost::wave::T_CPPCOMMENT) {
			output += std::string(it->get_value().begin(),
					it->get_value().end());
		}
	}
	return output;
}

int main(int argc, char* argv[]) {
	// 第一个参数是文件名
	if (argc < 2 || access(argv[1], F_OK) != 0) {
		std::cout << DEFAULT_CLASS_NAME;
	}
	char line[MAX_LINE] = { 0 };
	std::ifstream input(argv[1]);

	std::string code;
	while (input.getline(line, MAX_LINE) > 0) {
		code = code + line;
		code = code + "\n";
	}

	code = strip_comments(code);

	cregex regex_class_name = cregex::compile("public\\s+class\\s+\\w+");
	cmatch class_name;
	regex_search(code.c_str(), class_name, regex_class_name);

	if (class_name.size() > 0) {
		std::vector<std::string> items;
		std::string match_string = class_name[0];
		boost::split(items, match_string, boost::is_any_of("\r\n\t "),
				boost::token_compress_on);
		if (items.size() != 3) {
			std::cout << DEFAULT_CLASS_NAME;
		} else {
			std::cout << items[2];
		}
	} else {
		std::cout << DEFAULT_CLASS_NAME;
	}
	return 0;
}

