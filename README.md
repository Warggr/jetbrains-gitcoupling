# Coupling analysis in Git repositories

## Features
### Metrics

## Usage

### In a Jupyter notebook
```shell
jupyter notebook ./main.ipynb
```
### As a script
```shell
python <path_to_repo> [{FILES|FILES_X_COMMITS}]
```

## Limitations
- The code only takes into account the main branch

## Future directions

### Implement caching
Parsing the repo can sometimes be slow. Caching the parsed repo (i.e. number of lines per user / file etc.) could improve user experience.

### Use a functional programming language
Most of the functions are already just reducers over iterables. A functional programming language would be very suitable for this project.
