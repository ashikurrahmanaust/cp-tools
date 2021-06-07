# This is a codeforces contest parser

import sys, os, threading, requests, time
from bs4 import BeautifulSoup

# Provie the path where the problem should sit to
PATH = "~/git_workspace/all_contest/"

CONNECTION_LOST_MSG = "Connection failed."

# Remove leading and trailing bad characters
def purify(txt):
    bad_chars = [' ', '\n', '\t', '\r']
    for i in range(len(bad_chars)):
        for bad in bad_chars:
            txt = txt.lstrip(bad)
            txt = txt.rstrip(bad)
    return txt

class Problem_Parser(threading.Thread):
    page = None
    def __init__(self, problem_link, problem_name, path):
        threading.Thread.__init__(self)
        self.problem_link = problem_link
        self.problem_name = problem_name
        self.problem_path = path + self.problem_name + "/"
    
    def make_directories(self):
        try:
            os.system("mkdir " + self.problem_path + " 2> /dev/null")
        except:
            pass
        try:
            os.system("mkdir " + self.problem_path + "input/ 2> /dev/null")
        except:
            pass
        try:
            os.system("mkdir " + self.problem_path + "output/ 2> /dev/null")
        except:
            pass
        try:
            os.system("mkdir " + self.problem_path + "expected/ 2> /dev/null")
        except:
            pass
        
    def parse_problem(self):
        html_req = None
        try:
            html_req = requests.get(self.problem_link)
        except:
            print(CONNECTION_LOST_MSG)
            exit(0)
        self.page = BeautifulSoup(html_req.text, "html.parser")
        sample_tests = self.page.find("div", class_ = "sample-test")
        sample_input = sample_tests.find_all("div", class_ = "input")
        sample_output = sample_tests.find_all("div", class_ = "output")
        assert(len(sample_input) == len(sample_output))
        
        # Problem info
        problem_title = self.page.find('div', attrs = {'class':'title'}).string
        try:
            cmd = "echo \"Problem " + problem_title + "\"" + " > " + self.problem_path + "README.md"
            os.system(cmd)
        except:
            pass
        
        # sample input section
        for i in range(len(sample_input)):
            val = sample_input[i].find("pre")
            pure_val = val.string
            pure_val = purify(pure_val)
            try:
                cmd = "echo \"" + pure_val + "\" > " + self.problem_path + "input/data" + str(i) + " 2> /dev/null"
                os.system(cmd)
            except:
                pass
        
        #sample output
        for i in range(len(sample_output)):
            val = sample_output[i].find("pre")
            pure_val = val.string
            pure_val = purify(pure_val)
            try:
                cmd = "echo \"" + pure_val + "\" > " + self.problem_path + "expected/data" + str(i) + " 2> /dev/null"
                os.system(cmd)
            except:
                pass
    
    def run(self):
        self.make_directories()
        self.parse_problem()

class Contest_Parser:
    site_url = "https://codeforces.com"
    page = None
    contest_id = None
    local_path = None
    def __init__(self, contest_id):
        contest_url = self.site_url + "/contest/" + str(contest_id)
        html_req = None
        try:
            html_req = requests.get(contest_url)
        except:
            print(CONNECTION_LOST_MSG)
            exit(0)
        self.page = BeautifulSoup(html_req.text, "html.parser")
        self.contest_id = str(contest_id)
    
    def make_contest(self):
        if (self.contest_id == None):
            return 
        name = "cf-" + str(self.contest_id)
        self.local_path = PATH + name + "/"
        try:
            os.system("mkdir " + self.local_path + " 2> /dev/null")
        except:
            pass
        try :
            cmd = "echo -n \"Created: \"" + " > " + self.local_path + "README.md"
            os.system(cmd)
            cmd = "date \'+%d-%m-%Y\'" + " >> " + self.local_path + "README.md"
            os.system(cmd)
            curr_name = str(self.page.title.string)
            curr_name = curr_name.replace('Dashboard - ', '')
            curr_name = curr_name.rstrip(' - Codeforces')
            cmd = "echo \"Name: " + str(curr_name) + "\" >> " + self.local_path + "\README.md"
            os.system(cmd)
        except:
            pass
        
    def get_problems(self):
        table = self.page.find("table", class_ = "problems")
        rows = table.find_all("tr")
        # Skip the first row. It doesn't cotains problem
        problems = []
        for i in range(1, len(rows)):
            problem_data = rows[i].find('a')
            problem_link = problem_data.get("href")
            problem_name = problem_data.string
            problem_name = purify(problem_name)
            problem_name = problem_name.lower()
            problems.append((problem_name, problem_link))
        return problems
    
    def driver(self) -> None:
        self.make_contest()
        problems = self.get_problems()
        problem_parsers = []
        for problem in problems:
            problem_parser = Problem_Parser(self.site_url + problem[1], problem[0], self.local_path)
            problem_parsers.append(problem_parser)
        for pp in problem_parsers:
            pp.start()
        for pp in problem_parsers:
            pp.join()
        
        
if (__name__ == "__main__"):
    if (len(sys.argv) < 2):
        print("Please provie a contest ID.")
        exit(0)
    contest_parser = Contest_Parser(sys.argv[1])
    contest_parser.driver()
    print("All set. Solve the problems. All the best.")
    
