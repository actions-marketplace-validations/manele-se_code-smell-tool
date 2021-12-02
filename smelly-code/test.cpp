void with_comments() {
  int x = 10;
  int a;
  /*
  int z = 5, x;
  int y = 20;
  x = y + z * 10;
  */

  /* int y = 20 */
  /* int hello */
  /* int hello; */

  // Not commented code!

  // return 0;
}

/*
   This comment starts with some text, but then has a lot of code:
void main(int argc, char **argv) {
    if (argc < 2) {
        puts("Missing argument");
        return;
    }
    sprintf("Hi, %s!\n", argv[1]);
}
*/

// This is not code (even though is has parenthesis and a semicolon);

// public static func(int x, char **y, double fluff);

// int FrameBuffer::get_freq() noexcept { return frame_buf.get_freq(); }

enum Foo {
  NONE = 0,
  /*
  ANY = 1,
  ALL = 2,
  ONE = 3,
  */
  CUSTOM = 0x000000ff
};
