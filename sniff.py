from clang.cindex import *
import os
import sys

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

# List of Smell objects
report: list = []

# Base class for all token-based code smell detectors
class TokenScanner:
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
                report.append(Smell('Commented code', token.location))
    
    def __is_code(self, code: str):
        # First naive attempt:
        # return ('(' in code and ')' in code) or \
        #        ('{' in code and '}' in code) or \
        #        ';' in code or \
        #        '->' in code

        # Wrap the code in a function so the parser can work
        code_in_func = 'void f() { ' + code + ' ; }'

        # Parse the code using the Clang parser
        index = Index.create()
        syntax_tree = index.parse('tmp.cpp', args=['c++'], unsaved_files=[('tmp.cpp', code_in_func)], options=0)

        # Walk the syntax tree, measure the size and depth of the tree
        self.tree_size = 0
        self.tree_depth = 0
        self.current_depth = 0
        self.__recurse_code(syntax_tree.cursor)

        # Even non-code produces a tree of depth 2 and size 3
        # So anything larger than that could be valid code
        return self.tree_depth > 2 or self.tree_size > 3
    
    def __recurse_code(self, cursor: Cursor):
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
        file_name = os.path.realpath(file_name)
        scanners = [scanner_class() for scanner_class in scanner_classes]
        index = Index.create()
        translation_unit = index.parse(file_name, args=['-x', 'c++'])
        for token in translation_unit.cursor.get_tokens():
            for scanner in scanners:
                scanner.visit(token)
    
class DirectoryScanner:
    fs = FileScanner()

    def scan(self, dir_name: str):
        # Recursively walk through all directories and files in the dir
        for dir, subdirs, filenames in os.walk(dir_name):
            # Look at each file in each sub-directory
            for filename in filenames:
                # We are only interested in C/C++ source files
                _, file_extension = os.path.splitext(filename.lower())
                if (file_extension in ['.c', '.cpp', '.cxx', '.cc', '.c++']):
                    full_filename = os.path.join(dir, filename)
                    # Scan this file
                    self.fs.scan(full_filename)

        # Print the list of smells
        for smell in report:
            filename = os.path.relpath(smell.filename, dir_name)
            print(f'{smell.description}: {filename}, line {smell.line}, column {smell.column}')


ds = DirectoryScanner()
ds.scan(sys.argv[1])

# https://clang.llvm.org/doxygen/group__CINDEX__LEX.html
# https://coderedirect.com/questions/611429/using-libclang-to-parse-in-c-in-python
# https://pretagteam.com/question/ast-generated-by-libclangs-python-binding-unable-to-parse-certain-tokens-in-c-source-codes
