# code-smell-tool
Prototype of a code smell detection tool to add to the CI chain

## How to use as a Github Action

By using **Manele Code Smell Scanner** in your workflows, your C/C++ code is scanned for commented-out code every time you push changes. You will also get the list of commented-out code as a comment in your pull requests.

Add the following `uses` section to a step in your workflow `.yml` file:

```
      - uses: "manele-se/code-smell-tool@v0.3.6"
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

The tool defaults to scanning the contents of your repository's `src` folder, but this can be overridden by adding a `source-location` value:

```
      - uses: "manele-se/code-smell-tool@v0.3.6"
        with:
          source-location: project/main/code
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## How to use manually

### Preparations

Make sure that clang is installed.

On Windows, download and install 32 bit LLVM from here: https://github.com/llvm/llvm-project/releases

Install libclang in python:

```
pip install libclang
```

### Running the tool

Start the `sniff.py` script and pass the root directory of your C/C++ project as a parameter:

```
python sniff.py my/project/src
```
