import unittest
from sniff import CommentedCodeScanner

class CommentedCodeScannerTests(unittest.TestCase):
    def setUp(self):
        self.scanner = CommentedCodeScanner()
    
    def test_positives(self):
        true_positives = [
            """
  int z = 5, x;
  int y = 20;
  x = y + z * 10;
  """,
            "int y = 20",
            "y = 30;",
            "return 0;",
            """
   This comment starts with some text, but then has a lot of code:
void main(int argc, char **argv) {
    if (argc < 2) {
        puts("Missing argument");
        return;
    }
    sprintf("Hi, %s!\n", argv[1]);
}
""",
            "int FrameBuffer::get_freq() noexcept { return frame_buf.get_freq(); }",
            """
  ANY = 1,
  ALL = 2,
  ONE = 3,
  """
        ]
        for tp in true_positives:
            self.assertTrue(self.scanner.is_code(tp), tp)

    def test_negatives(self):
        true_negatives = [
            "Not commented code!",
            "This is not code (even though is has parenthesis and a semicolon);",
            "TODO: Fix this",
            """
            key | value
            -----------
            X1  |   128
            X2  |    32
            X3  |     2
            """
        ]
        for tn in true_negatives:
            self.assertFalse(self.scanner.is_code(tn), tn)
