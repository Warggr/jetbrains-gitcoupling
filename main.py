from collections import defaultdict
from tqdm import tqdm
import pandas as pd
from typing import Dict, Tuple, NoReturn, Iterable

import git
from git import Repo

CommitterId = str
Path = str

def count_lines_per_user_per_file(repo: Repo) -> Dict[ Path, Dict[CommitterId, int] ]:
    lines_per_user_per_file : Dict[ Path, Dict[CommitterId, int] ] = defaultdict(lambda: defaultdict(lambda: 0))

    for commit in tqdm(repo.iter_commits()):
        for file, lines in commit.stats.files.items():
            if lines['lines'] != 0: # This can happen for non-text files
                lines_per_user_per_file[file][commit.author.name] += lines['lines']
    return lines_per_user_per_file

def count_total_lines_per_user(lines_per_user_per_file : Dict[ Path, Dict[CommitterId, int] ]):
    lines_per_user = defaultdict(int)
    for lines_per_user_for_one_file in lines_per_user_per_file.values():
        for user, lines in lines_per_user_for_one_file.items():
            lines_per_user[user] += lines
    return lines_per_user

def count_total_files_per_user(lines_per_user_per_file : Dict[ Path, Dict[CommitterId, int] ]):
    files_per_user = defaultdict(int)
    for lines_per_user_for_one_file in lines_per_user_per_file.values():
        for user in lines_per_user_for_one_file.keys():
            files_per_user[user] += 1
    return files_per_user

def get_pairs_of_developers(lines_per_user_per_file : Dict[Path, Dict[CommitterId, int]]) -> Iterable[Tuple[CommitterId, CommitterId, int, int]]:
    for file, lines_per_user in lines_per_user_per_file.items():
        users = list(lines_per_user.keys())
        for i in range(len(users)):
            for j in range(i+1, len(users)):
                userA, userB = sorted([ users[i], users[j] ])
                yield userA, userB, lines_per_user[userA], lines_per_user[userB]

def count_common_files_per_pair(
    pairs_of_developers : Iterable[Tuple[CommitterId, CommitterId, int, int]]
) -> Dict[Tuple[CommitterId, CommitterId], int]:
    common_files_per_pair : Dict[Tuple[CommitterId, CommitterId], int] = defaultdict(lambda: 0)

    for userA, userB, _, _ in pairs_of_developers:
        common_files_per_pair[userA, userB] += 1
    return common_files_per_pair

def count_common_lines_per_pair(
    pairs_of_developers : Iterable[Tuple[CommitterId, CommitterId, int, int]]
) -> Dict[Tuple[CommitterId, CommitterId], Tuple[int, int]]:
    common_lines_per_pair : Dict[Tuple[CommitterId, CommitterId], int] = defaultdict(lambda: [0, 0])

    for userA, userB, userAValue, userBValue in pairs_of_developers:
        assert userAValue != 0 and userBValue != 0
        common_lines_per_pair[userA, userB][0] += userAValue
        common_lines_per_pair[userA, userB][1] += userBValue
    return common_lines_per_pair

analysis_types = ['FILES', 'FILES_X_LINES']

def create_developer_pair_dataset(repo: Repo, count: str) -> pd.DataFrame:
    """ Creates dataset with all relevant info.

    @param count: what to count; either 'FILES' or 'FILES_X_LINES'
    """
    lines_per_user_per_file = count_lines_per_user_per_file(repo)
    lines_per_pair = get_pairs_of_developers(lines_per_user_per_file)
    if count == 'FILES':
        data = count_common_files_per_pair(lines_per_pair)
        dataset = pd.DataFrame(data=([*users, commonFiles] for users, commonFiles in data.items()), columns=['User 1', 'User 2', 'Common Files'])

        total_per_user = count_total_files_per_user(lines_per_user_per_file)
        dataset['% User 1'] = [ value / total_per_user[user1Name] for value, user1Name in zip(dataset['Common Files'], dataset['User 1']) ]
        dataset['% User 2'] = [ value / total_per_user[user2Name] for value, user2Name in zip(dataset['Common Files'], dataset['User 2']) ]

        relevant_value = 'Common Files'

    elif count == 'FILES_X_LINES':
        data = count_common_lines_per_pair(lines_per_pair)
        dataset = pd.DataFrame(data=([*users, *commonLines] for users, commonLines in data.items()), columns=['User 1', 'User 2', 'Lines User 1', 'Lines User 2'])

        total_per_user = count_total_lines_per_user(lines_per_user_per_file)
        dataset['% User 1'] = [ user1value / total_per_user[user1Name] for user1value, user1Name in zip(dataset['Lines User 1'], dataset['User 1']) ]
        dataset['% User 2'] = [ user2value / total_per_user[user2Name] for user2value, user2Name in zip(dataset['Lines User 2'], dataset['User 2']) ]
        dataset['Sum Lines'] = [ user1 + user2 for user1, user2 in zip(dataset['Lines User 1'], dataset['Lines User 2']) ]
        relevant_value = 'Sum Lines'
    # Intersection over union
    dataset['IoU'] = [
        value / (total_per_user[user1Name] + total_per_user[user2Name] - value)
        for value, user1Name, user2Name in zip(dataset[relevant_value], dataset['User 1'], dataset['User 2'])
    ]
    # Product metric
    dataset['product'] = [
        (value ** 2) / (total_per_user[user1Name] + total_per_user[user2Name] - value)
        for value, user1Name, user2Name in zip(dataset[relevant_value], dataset['User 1'], dataset['User 2'])
    ]
    dataset = dataset.sort_values(by='product', ascending=False)

    dataset.style.format({'% User 1': "{:.2%}".format, '% User 2': "{:.2%}".format})
    return dataset

def help() -> NoReturn:
    print(f"Usage: {sys.argv[0]} <path_to_repo> [{{{ '|'.join(analysis_types) }}}]")
    sys.exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) <= 1: help()
    repo = Repo(sys.argv[1])
    count = 'FILES'
    if len(sys.argv) > 2:
        count = sys.argv[2]
        if count not in analysis_types: help()
    dataset = create_developer_pair_dataset(repo, count=count)
    print(dataset.to_string(index=False))
