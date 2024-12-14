class Parser:
    def __init__(self, lexer):
        self.token = None  # Current token
        self.lexeme = None  # Current lexeme
        self.instr_address = 1  # Instruction address counter
        self.instr_table = []  # Instruction table
        self.symbol_table = {}  # Symbol table with types
        self.jump_stack = []  # Stack for jump addresses
        self.memory_address = 9000  # Start address for identifiers
        self.lexer = lexer  # Injected lexer instance

    def lexer_next(self):
        """Fetch the next token from the lexer."""
        token_lexeme = self.lexer.next_token()
        if token_lexeme:
            self.token, self.lexeme = token_lexeme
        else:
            self.token, self.lexeme = None, None


    def gen_instr(self, op, oprnd):
        """Generate an instruction and add it to the instruction table."""
        self.instr_table.append({"address": self.instr_address, "op": op, "oprnd": oprnd})
        self.instr_address += 1

    def get_address(self, id):
        """Retrieve the memory address for an identifier."""
        return self.symbol_table.get(id, {}).get("address")

    def insert_symbol(self, id, var_type):
        """Insert a new identifier with its type into the symbol table."""
        if id in self.symbol_table:
            self.error_message(f"Identifier '{id}' already declared.")
        else:
            self.symbol_table[id] = {"address": self.memory_address, "type": var_type}
            self.memory_address += 1

    def error_message(self, message):
        """Display an error message and advance to the next token."""
        print(f"Error: {message}. Current token: {self.token}, lexeme: {self.lexeme}")
        self.lexer_next()  # Advance to avoid repeated errors

    def print_symbol_table(self):
        """Print the symbol table."""
        print("Lexeme\tMemory Address\tType")
        for lexeme, details in self.symbol_table.items():
            print(f"{lexeme}\t{details['address']}\t{details['type']}")

    def print_instr_table(self):
        """Print the instruction table."""
        print("Address\tOp\tOprnd")
        for instr in self.instr_table:
            print(f"{instr['address']}\t{instr['op']}\t{instr['oprnd']}")

    def A(self):
        """Assignment Statement: A -> id = E { gen_instr (POPM, get_address(id)) }"""
        if self.token == "identifier":
            save = self.lexeme
            if save not in self.symbol_table:
                self.error_message(f"Identifier '{save}' not declared.")
            self.lexer_next()
            if self.token == "operator" and self.lexeme == "=":
                self.lexer_next()
                self.E()
                address = self.get_address(save)
                if address is None:
                    self.error_message(f"Identifier '{save}' not declared.")
                else:
                    self.gen_instr("POPM", address)
                if self.token == "separator" and self.lexeme == ";":
                    self.lexer_next()  # Consume ';'
                else:
                    self.error_message("; expected")
            else:
                self.error_message("= expected")
        else:
            self.error_message("identifier expected")

    def E(self):
        """Expression: E -> T E'"""
        self.T()
        self.E_prime()

    def E_prime(self):
        """Expression Prime: E' -> + T { gen_instr (ADD, nil) } E' | epsilon"""
        if self.token == "operator" and self.lexeme == "+":
            self.lexer_next()
            self.T()
            self.gen_instr("ADD", None)
            self.E_prime()

    def T(self):
        """Term: T -> F T'"""
        self.F()
        self.T_prime()

    def T_prime(self):
        """Term Prime: T' -> * F { gen_instr (MUL, nil) } T' | epsilon"""
        if self.token == "operator" and self.lexeme == "*":
            self.lexer_next()
            self.F()
            self.gen_instr("MUL", None)
            self.T_prime()

    def F(self):
        """Factor: F -> id { gen_instr (PUSHM, get_address(id)) } | integer { gen_instr (PUSHI, integer) }"""
        if self.token == "identifier":
            if self.lexeme not in self.symbol_table:
                self.error_message(f"Identifier '{self.lexeme}' not declared.")
            address = self.get_address(self.lexeme)
            if address is None:
                self.error_message(f"Identifier '{self.lexeme}' not declared.")
            else:
                self.gen_instr("PUSHM", address)
            self.lexer_next()
        elif self.token == "integer":
            self.gen_instr("PUSHI", self.lexeme)
            self.lexer_next()
        elif self.token == "real":
            self.gen_instr("PUSHF", self.lexeme)
            self.lexer_next()
        else:
            self.error_message("identifier or literal expected")


    def compound_statement(self):
        """Compound Statement: <Compound> -> { <Statements> }"""
        if self.token == "separator" and self.lexeme == "{":
            self.lexer_next()
            while self.token != "separator" or self.lexeme != "}":
                self.S()
            if self.token == "separator" and self.lexeme == "}":
                self.lexer_next()
            else:
                self.error_message("} expected")
        else:
            self.error_message("{ expected")

    def get_statement(self):
        """Get Statement: <Get> -> get ( id )"""
        if self.token == "keyword" and self.lexeme == "get":
            self.lexer_next()
            if self.token == "separator" and self.lexeme == "(":
                self.lexer_next()
                if self.token == "identifier":
                    if self.lexeme not in self.symbol_table:
                        self.error_message(f"Identifier '{self.lexeme}' not declared.")
                    address = self.get_address(self.lexeme)
                    self.gen_instr("STDIN", None)
                    self.gen_instr("POPM", address)
                    self.lexer_next()
                    if self.token == "separator" and self.lexeme == ")":
                        self.lexer_next()
                        if self.token == "separator" and self.lexeme == ";":
                            self.lexer_next()  # Consume ';'
                        else:
                            self.error_message("; expected")
                    else:
                        self.error_message(") expected")
                else:
                    self.error_message("identifier expected")
            else:
                self.error_message("( expected")
        else:
            self.error_message("get expected")

    def if_statement(self):
        """If Statement: I -> if ( C ) S fi"""
        if self.token == "keyword" and self.lexeme == "if":
            self.lexer_next()  # Consume 'if'
            if self.token == "separator" and self.lexeme == "(":
                self.lexer_next()  # Consume '('
                self.C()  # Evaluate the condition
                if self.token == "separator" and self.lexeme == ")":
                    self.lexer_next()  # Consume ')'
                    self.S()  # Execute the statement inside the if block
                    if self.token == "keyword" and self.lexeme == "fi":
                        self.lexer_next()  # Consume 'fi'
                    else:
                        self.error_message("fi expected")
                else:
                    self.error_message(") expected")
            else:
                self.error_message("( expected")
        else:
            self.error_message("if expected")

    def put_statement(self):
        """Put Statement: <Put> -> put ( <Expression> )"""
        if self.token == "keyword" and self.lexeme == "put":
            self.lexer_next()
            if self.token == "separator" and self.lexeme == "(":
                self.lexer_next()
                self.E()
                self.gen_instr("STDOUT", None)
                if self.token == "separator" and self.lexeme == ")":
                    self.lexer_next()
                    if self.token == "separator" and self.lexeme == ";":
                        self.lexer_next()  # Consume ';'
                    else:
                        self.error_message("; expected")
                else:
                    self.error_message(") expected")
            else:
                self.error_message("( expected")
        else:
            self.error_message("put expected")

    def S(self):
        """Statement: <S> -> <A> | <Get> | <Put> | <Compound>"""
        if self.token == "identifier":
            self.A()
        elif self.token == "keyword" and self.lexeme == "get":
            self.get_statement()
        elif self.token == "keyword" and self.lexeme == "put":
            self.put_statement()
        elif self.token == "keyword" and self.lexeme == "if":
            self.if_statement()
        elif self.token == "separator" and self.lexeme == "{":
            self.compound_statement()
        else:
            self.error_message("Invalid statement")

    def while_statement(self):
        """While Statement: W -> while ( C ) S"""
        if self.token == "keyword" and self.lexeme == "while":
            addr = self.instr_address
            self.gen_instr("LABEL", None)
            self.lexer_next()
            if self.token == "separator" and self.lexeme == "(":
                self.lexer_next()
                self.C()
                if self.token == "separator" and self.lexeme == ")":
                    self.lexer_next()
                    self.S()
                    self.gen_instr("JUMP", addr)
                    self.back_patch(self.instr_address)
                else:
                    self.error_message(") expected")
            else:
                self.error_message("( expected")
        else:
            self.error_message("while expected")

    def C(self):
        """Condition: C -> E R E"""
        self.E()
        if self.token == "operator" and self.lexeme in ["<", ">", "==", "!=", "<=", ">="]:
            op = self.lexeme
            self.lexer_next()
            self.E()
            if op == "<":
                self.gen_instr("LES", None)
            elif op == ">":
                self.gen_instr("GRT", None)
            elif op == "==":
                self.gen_instr("EQU", None)
            elif op == "!=":
                self.gen_instr("NEQ", None)
            elif op == "<=":
                self.gen_instr("LEQ", None)
            elif op == ">=":
                self.gen_instr("GEQ", None)
            self.jump_stack.append(self.instr_address)
            self.gen_instr("JUMPZ", None)
        else:
            self.error_message("Relational operator expected")

    def back_patch(self, jump_addr):
        """Back-patch the JUMPZ instruction."""
        addr = self.jump_stack.pop()
        self.instr_table[addr - 1]["oprnd"] = jump_addr
