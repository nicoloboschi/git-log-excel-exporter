#!/usr/bin/python3

import subprocess, re, argparse

def capture_git_log(directory, git_ref):
    result = subprocess.run(["git", "log", "--reverse", "--pretty=format:%h %s", git_ref],
        capture_output=True, text=True, cwd = directory)
    return result.stdout

def compute_sheets_hyperlink(link, label):
    return "=HYPERLINK(\"%s\",\"%s\")" % (link, label)

def get_cherry_pick_string(sha, repo, cwd): 
    # (cherry picked from commit 46cfd8e55ee159b74b3d8c823cb78eaeb9eb88ee)
    full_message = subprocess.run(["git", "log", "--format=%B", "-n", "1", sha],
        capture_output=True, text=True, cwd = cwd).stdout
    
    cherry_picked_from = re.search('cherry picked from commit (.*)\)', full_message)
    cpick_str = ""
    if (cherry_picked_from):
        cpick_str = "=HYPERLINK(\"https://github.com/%s/commit/%s\",\"Link\")" % (repo, cherry_picked_from.group(1))
    return cpick_str

def out(string):
    print(string)


def output_logs(git_log_result, cwd, repo, cherry_pick_repo):
    splitted = git_log_result.split("\n")
    splitted = list(filter(lambda str: str, splitted))
    result = ""
    for str in splitted:
        sha = str[:11]
        message = str[12:]
        link = compute_sheets_hyperlink("https://github.com/%s/commit/%s" % (repo, sha), "Commit")
        cherry_pick = ""
        if cherry_pick_repo:
            cherry_pick = get_cherry_pick_string(sha, cherry_pick_repo, cwd)
        result += "%s\t%s\t%s\n" % (message, link, cherry_pick)
        
    out(result)


parser = argparse.ArgumentParser()
parser.add_argument("--git-ref", help="Git argument for 'git log'", required=True)
parser.add_argument("--cwd", help="Working directory", default=".")
parser.add_argument("--repository", help="Github repository used to create link to the commits", required=True)
parser.add_argument("--cpick-repository", help="Github repository used to create link to the cherry-pick refs")

args = parser.parse_args()
git_logs = capture_git_log(args.cwd, args.git_ref)
output_logs(git_logs, args.cwd, args.repository, args.cpick_repository)

