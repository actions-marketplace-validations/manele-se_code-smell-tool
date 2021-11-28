from clang.cindex import *
import os
import sys

MIN_CODE_DEPTH = 5
MIN_CODE_SIZE = 7
verbose = False

# TODO: Add to CI

# https://stackoverflow.com/questions/26000876/how-to-solve-the-loading-error-of-clangs-python-binding
# https://github.com/llvm-mirror/clang/tree/master/bindings/python
if os.name == 'nt':
    Config.set_library_file("C:/Program Files (x86)/LLVM/bin/libclang.dll")

# Information about an identified smell
class Smell:
    filename: str
    line: int
    column: int
    description: str

    def __init__(self, description: str, location: SourceLocation):
        self.description = description
        self.filename = str(location.file)
        self.line = location.line
        self.column = location.column
    
    def __str__(self):
        return f'{self.description}: {self.filename}, line {self.line}, column {self.column}'
    
    def full_description(self, root_dir: str):
        filename = os.path.relpath(self.filename, root_dir)
        return f'{self.description}: {filename}, line {self.line}, column {self.column}'

# List of Smell objects
report: list = []

# Base class for all token-based code smell detectors
class TokenScanner:
    # An implementation of the Visitor pattern
    def visit(self, token: Token):
        print(token.kind.name)

# Detector for Commented Code
class CommentedCodeScanner(TokenScanner):
    def visit(self, token: Token):
        # We are only interested in COMMENT tokens
        if token.kind == TokenKind.COMMENT:
            # Extract the contents of the comment
            comment = token.spelling

            # Remove the // or the /* */
            if comment[0:2] == '//':
                comment = comment[2:].strip().lower()
            elif comment[0:2] == '/*':
                comment = comment[2:-2].strip().lower()
            
            # Check if the comment contains code
            if self.__is_code(comment):
                # report.append(Smell(f'Commented code (tree_size={self.tree_size}, tree_depth={self.tree_depth}', token.location))
                report.append(Smell(f'Commented code', token.location))
    
    def __is_code(self, code: str):
        # Wrap the code in a function so the parser can work
        code_in_func = 'void f() { ' + code + ' ; }'

        # Parse the code using the Clang parser
        index = Index.create()
        syntax_tree = index.parse('tmp.cpp', unsaved_files=[('tmp.cpp', code_in_func)], options=0x200)

        # Walk the syntax tree, measure the size and depth of the tree
        self.tree_size = 0
        self.tree_depth = 0
        self.current_depth = 0
        self.__recurse_code(syntax_tree.cursor)
        if verbose:
            indent = ' ' * (self.current_depth * 2)
            print(f'depth: {self.tree_depth}, size: {self.tree_size}')

        # Non-code mostly produces a tree of depth < 5 and size < 7
        # So anything larger than that could be valid code
        return self.tree_depth >= MIN_CODE_DEPTH and self.tree_size >= MIN_CODE_SIZE
    
    def __recurse_code(self, cursor: Cursor):
        if verbose:
            indent = ' ' * (self.current_depth * 2)
            print(f'{indent}{cursor.kind} {cursor.spelling}')
        # Increase the total size
        self.tree_size = self.tree_size + 1

        # Keep track of the maximum depth
        if self.current_depth > self.tree_depth:
            self.tree_depth = self.current_depth
        
        # Increase current depth, recursively loop over all children, and decrease depth again
        self.current_depth = self.current_depth + 1
        for child in cursor.get_children():
            self.__recurse_code(child)
        self.current_depth = self.current_depth - 1

# In the future, we can put more code smell detection classes here
scanner_classes: list = [CommentedCodeScanner]

class FileScanner:
    def scan(self, file_name: str):
        # Get the full path for this filename
        file_name = os.path.realpath(file_name)

        # For every smell detection class, instantiate the class
        scanners = [scanner_class() for scanner_class in scanner_classes]

        # Tokenize the code using Clang tokenixer
        index = Index.create()

        # Start reading this file
        translation_unit = index.parse(file_name)

        # Use the tokenizer to loop over all tokens
        for token in translation_unit.cursor.get_tokens():
            # For each token, let each scanner look at the token
            for scanner in scanners:
                scanner.visit(token)
    
class DirectoryScanner:
    def scan(self, dir_name: str):
        fs = FileScanner()
        # Recursively walk through all directories and files in the dir
        for dir, subdirs, filenames in os.walk(dir_name):
            # Look at each file in each sub-directory
            for filename in filenames:
                # We are only interested in C/C++ source files
                _, file_extension = os.path.splitext(filename.lower())
                if (file_extension in ['.c', '.cpp', '.cxx', '.cc', '.c++']):
                    full_filename = os.path.join(dir, filename)
                    # Scan this file
                    fs.scan(full_filename)

ds = DirectoryScanner()
# For each directory name passed as an argument, scan that directory
for dir in sys.argv[1:]:
    if dir == "-v" or dir == "--verbose":
        verbose = True
        continue
    print(f'Scanning {dir}...')
    report.clear()
    ds.scan(dir)
    # Print the list of smells
    for smell in report:
        print(smell.full_description(dir))

# https://clang.llvm.org/doxygen/group__CINDEX__LEX.html
# https://coderedirect.com/questions/611429/using-libclang-to-parse-in-c-in-python
# https://pretagteam.com/question/ast-generated-by-libclangs-python-binding-unable-to-parse-certain-tokens-in-c-source-codes
