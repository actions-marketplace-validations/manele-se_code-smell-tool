from clang.cindex import *
import os
import sys
import re

verbose = False


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
                comment = comment[2:].strip()
            elif comment[0:2] == '/*':
                comment = comment[2:-2].strip()

            # Check if the comment contains code
            if self.is_code(comment):
                report.append(Smell('Commented code', token.location))

    def is_code(self, code: str):
        return False

WORD_WEIGHT = 3.0
HARD_WEIGHT = 2.0
SOFT_WEIGHT = 1.0
MIN_RATIO = 0.21

class StatisticCommentedCodeScanner(CommentedCodeScanner):
    def is_code(self, code: str):
        word_evidence = len(re.findall(r'\b((::)|(void)|(for)|(while)|(if)|(int)|(double)|(bool)|(std)|(return))\b', code))
        hard_evidence = len(re.findall(r'[;{}:]', code))
        soft_evidence = len(re.findall(r'[-+,*/%<>()".=]', code))

        ratio = (word_evidence * WORD_WEIGHT +
                 hard_evidence * HARD_WEIGHT +
                 soft_evidence * SOFT_WEIGHT) / len(code)

        return ratio >= MIN_RATIO

MIN_CODE_DEPTH = 4
MIN_CODE_SIZE = 6

class ClangParserCommentedCodeScanner(CommentedCodeScanner):
    def is_code(self, code: str):
        # Wrap the code in a function so the parser can work
        code_in_func = 'void f() { ' + code + ' ; }'

        # Parse the code using the Clang parser
        index = Index.create()
        syntax_tree = index.parse('tmp.cpp', unsaved_files=[
                                  ('tmp.cpp', code_in_func)], options=0x200)

        # Walk the syntax tree, measure the size and depth of the tree
        self.tree_size = 0
        self.tree_depth = 0
        self.current_depth = 0
        self.__recurse_code(syntax_tree.cursor)

        # Non-code mostly produces a tree of depth < 5 and size < 7
        # So anything larger than that could be valid code
        return self.tree_depth >= MIN_CODE_DEPTH and self.tree_size >= MIN_CODE_SIZE

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
scanner_classes: list = [StatisticCommentedCodeScanner]


class FileScanner:
    def scan_file(self, file_name: str):
        # Get the full path for this filename
        file_name = os.path.realpath(file_name)

        # For every smell detection class, instantiate the class, now it loops just over one class.
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
    def scan_dir(self, dir_name: str):
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
                    fs.scan_file(full_filename)


ds = DirectoryScanner()
# For each directory name passed as an argument, scan that directory
for dir in sys.argv[1:]:
    print(f'Scanning {dir}...')
    report.clear()
    ds.scan_dir(dir)
    # Print the list of smells
    for smell in report:
        print('  ' + smell.full_description(dir))

# https://clang.llvm.org/doxygen/group__CINDEX__LEX.html
# https://coderedirect.com/questions/611429/using-libclang-to-parse-in-c-in-python
# https://pretagteam.com/question/ast-generated-by-libclangs-python-binding-unable-to-parse-certain-tokens-in-c-source-codes
