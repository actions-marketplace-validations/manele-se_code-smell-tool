#include <iostream>

void with_comments() {
  int x = 10;
  std::cout << "The value is " << x << std::endl;
  /*
  int y = 20;
  std::cout << "The other value is " << y << std::endl;
  */
  // This is not commented code!
  // this->is(definitely.some["commented code"])
}

// A long function, full of just nonsense code
int long_function() {
  int x = 0;
  int y = 10;

  with_comments();
  std::atoi("hejsan");
  if (1 == 1) {
    long_function();
  } else if (2 == 2) {
    with_comments();
  } else if (3 == 3) {
    std::atol("hoppsan");
  } else
    switch (x) {
    case 1:
      std::cout << "One";
      break;
    case 2:
      std::cout << "Two";
      break;
    case 3:
      std::cout << "Three";
      break;
    default:
      std::cerr << "Not one, two or three!";
      break;
    }

  while (std::cin >> y) {
    long_function();
    with_comments();
    int a = x + y;
    int b = 4 - 2;
    int c = 0;
    bool d = ((a + b) == c);
    for (int i = 0; i < 100; i++) {
      long_function();
    }
  }
  return 0;
}
