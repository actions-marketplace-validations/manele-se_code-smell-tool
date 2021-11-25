# code-smell-tool
Prototype of a code smell detection tool to add to the CI chain

## Preparations
Make sure that clang is installed.

On Windows, download and install 32 bit LLVM from here: https://github.com/llvm/llvm-project/releases

Install libclang in python:

```
pip install libclang
```

## How to use
Start the `sniff.py` script and pass the root directory of your C/C++ project as a parameter:

```
python sniff.py my/project/src
```
