from lexer import Lexer
from parser import Parser


def process_file(file_path, output_file):
    """Process the source code file and write the output to an output file."""
    with open(output_file, 'w') as out_file:
        out_file.write(f"Processing file: {file_path}\n")
        
        # Read the source code
        with open(file_path, 'r') as file:
            source_code = file.read()
            out_file.write(f"Test Case Content:\n{source_code}\n")
        
        # Tokenize the source code
        lexer = Lexer(source_code)
        lexer.tokenize()

        # Initialize the parser with the lexer
        parser = Parser(lexer)
        parser.lexer_next()  # Initialize the first token

        # Parse the source code
        while parser.token:
            if parser.token == "keyword" and parser.lexeme == "integer":
                # Handle declarations
                parser.lexer_next()  # Consume 'integer'
                while parser.token != "separator" or parser.lexeme != ";":
                    if parser.token == "identifier":
                        parser.insert_symbol(parser.lexeme, "integer")
                    parser.lexer_next()
                parser.lexer_next()  # Consume ';'
            elif parser.token in {"identifier", "keyword"}:
                if parser.lexeme == "while":
                    parser.while_statement()
                elif parser.lexeme == "if":
                    parser.if_statement()
                elif parser.lexeme in {"get", "put"}:
                    parser.S()
                else:
                    parser.A()  # Assume an assignment
            else:
                parser.error_message("Unexpected token")

        # Output the results to the file
        out_file.write("\nGenerated Assembly Code (Instruction Table):\n")
        for instr in parser.instr_table:
            out_file.write(f"{instr['address']}\t{instr['op']}\t{instr['oprnd']}\n")
        
        out_file.write("\nGenerated Symbol Table:\n")
        for lexeme, details in parser.symbol_table.items():
            out_file.write(f"{lexeme}\t{details['address']}\t{details['type']}\n")


if __name__ == "__main__":
    # Test files to process
    files = ["test1.txt", "test2.txt", "test3.txt"]

    for i, file in enumerate(files, start=1):
        output_file = f"output_test{i}.txt"  # Output file for each test case
        process_file(file, output_file)
        print(f"Results for {file} written to {output_file}")
        print("\n" + "=" * 50 + "\n")
