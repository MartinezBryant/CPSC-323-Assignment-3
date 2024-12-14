import re

# Token definitions
KEYWORDS = {"function", "integer", "boolean", "real", "if", "else", "fi", "while", "return", "get", "put"}
OPERATORS = {"==", "!=", ">", "<", "<=", ">=", "+", "-", "*", "/", "="}
SEPARATORS = {"(", ")", "{", "}", ";", ","}

# Updated regular expressions for FSM
identifier_re = r'[a-zA-Z][a-zA-Z0-9]*'
integer_re = r'[0-9]+'
real_re = r'[0-9]+\.[0-9]+'

# Token types
TOKEN_IDENTIFIER = "identifier"
TOKEN_INTEGER = "integer"
TOKEN_REAL = "real"
TOKEN_KEYWORD = "keyword"
TOKEN_OPERATOR = "operator"
TOKEN_SEPARATOR = "separator"
TOKEN_COMMENT = "comment"
TOKEN_UNKNOWN = "unknown"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []  # List to hold generated tokens
        self.current_index = 0  # Tracks the current token position during parsing

    def is_keyword(self, word):
        return word in KEYWORDS

    def is_operator(self, char):
        return char in OPERATORS

    def is_separator(self, char):
        return char in SEPARATORS

    def tokenize(self):
        # Removing comments
        self.source_code = re.sub(r'\[\*.*?\*\]', '', self.source_code)

        # Split source code into tokens
        pattern = re.compile(r'\s+|([(){};,])|([<>!=]=|[-+*/=<>])')
        raw_tokens = pattern.split(self.source_code)
        raw_tokens = [t for t in raw_tokens if t and not t.isspace()]  # Remove empty tokens and spaces

        for token in raw_tokens:
            # Identifiers and Keywords
            if re.match(identifier_re, token):
                if self.is_keyword(token):
                    self.tokens.append((TOKEN_KEYWORD, token))
                else:
                    self.tokens.append((TOKEN_IDENTIFIER, token))

            # Integers
            elif re.match(integer_re, token):
                self.tokens.append((TOKEN_INTEGER, token))

            # Real numbers
            elif re.match(real_re, token):
                self.tokens.append((TOKEN_REAL, token))

            # Operators
            elif self.is_operator(token):
                self.tokens.append((TOKEN_OPERATOR, token))

            # Separators
            elif self.is_separator(token):
                self.tokens.append((TOKEN_SEPARATOR, token))

            else:
                self.tokens.append((TOKEN_UNKNOWN, token))

    def next_token(self):
        """Fetch the next token from the list."""
        if self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            self.current_index += 1
            return token
        return None

    def print_tokens(self):
        """Print all tokens."""
        print(f"{'Token':<15}{'Lexeme':<15}")
        print("-" * 30)
        for token, lexeme in self.tokens:
            print(f"{token:<15}{lexeme:<15}")

    def write_tokens_to_file(self, output_file):
        """Write tokens to a file."""
        with open(output_file, 'w') as f:
            f.write("Token\tLexeme\n")
            for token, lexeme in self.tokens:
                f.write(f"{token}\t{lexeme}\n")
