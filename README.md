# Manele Code Smell Scanner

Prototype of a code smell detection tool to add to the CI chain

## How to use as a Github Action

By using **Manele Code Smell Scanner** in your workflows, your C/C++ code is scanned for commented-out code every time you push changes. You will also get the list of commented-out code as a comment in your pull requests.

Add the following `uses` section to a step in your workflow `.yml` file:

```
      - uses: "manele-se/code-smell-tool@v1.0.0"
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

The tool defaults to scanning the contents of your repository's `src` folder, but this can be overridden by adding a `source-location` value:

```
      - uses: "manele-se/code-smell-tool@v1.0.0"
        with:
          source-location: project/main/code
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

If your project does not yet have a GitHub Actions workflow, you can create one by addoing a file called `smell-check.yml` in the `.github` directory, with the following contents:

```
name: Check code smells
on: [push, pull_request]
jobs:
  smell-check:
    name: Smell check
    runs-on: ubuntu-latest
    steps:
      - uses: "actions/checkout@v2"
      - uses: "manele-se/code-smell-tool@v1.1.4"
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          source-location: CODE_DIRECTORY
```

Replace the `CODE_DIRECTORY` with the name of the directory containing your C/C++ source code, for example `src`. If the source code is in the root directory of your repository, replace `CODE_DIRECTORY` with a single `.` (dot) character.

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
