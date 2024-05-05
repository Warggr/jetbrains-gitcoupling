# Coupling analysis in Git repositories

## Usage

### Prerequisites
This program has been tested with Python 3.12 and might not work with other versions.
```shell
pip install -r requirements.txt
```

### In a Jupyter notebook
```shell
jupyter notebook ./main.ipynb
```
### As a script
```shell
python <path_to_repo> [{FILES,FILES_X_LINES}]
```

## Features
First, for each pair of developer, the program computes which files have been edited by both developers.
The program also computes the total number of files edited by each developer.

You can also use the FILES_X_LINES mode, where each file is weighted by the number of lines both developers have edited in that file.

### Metrics

#### Number of files
We could already check which pairs developers have the highest number of edited files in common.
However, this is usually not very interesting because these are usually just the 2 developers who commit most to the repository.

#### IoU (Intersection over Union)
The number of files edited by both developers, divided by the number of files edited by at least one of the two developers.
Formula: `commonFiles / (user1Total + user2Total - commonFiles)`

#### Product of both metrics
This metric multiplies the number of common files by the IoU value.
Formula: `commonFiles^2 / (user1Total + user2Total - commonFiles)`

The program prints each pair of developer, sorted by this final metric (product of both previous metrics).

## Limitations
- The code only takes into account the main branch

## Future directions

### Non-symmetric coupling
Take into account situations when developer A contributes only to the files that developer B also contributes to, but developer B is very
prolific and also contributes to a lot of other files. There could be two different values, one telling whether developer A has a lot in
common with developer B (this value would be high) and one whether developer B has a lot in common with A (this would be low).

### Implement caching
Parsing the repo can sometimes be slow. Caching the parsed repo (i.e. number of lines per user / file etc.) could improve user experience.

### Use a functional programming language
Most of the functions are already just reducers over iterables. A functional programming language would be very suitable for this project.
