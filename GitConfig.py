'''
Loads repository information from a json file.
Clones two versions of a project from a repository.
Builds both versions and applies patches for regression and bug fix issues.
@author: Alekh Meka <alekhmeka@gmail.com>
'''
import re
import subprocess
import os
import json
from shutil import copyfile
from sys import platform
from pathlib import Path

class VersionTool:
    """
    Used to maintain all repository and commit information pertaining to the two versions of a project
    Generates a project folder that contains "oldVersion" and "newVersion"
    Each corresponding version folder contains the repository at a particular commit
    Builds both versions of the project after making changes to the pom.xml file
    """
    def __init__(self, repo_str, project_name, description, cwd, old_version_commit, old_version_patch, old_version_build, new_version_commit, new_version_patch, new_version_build):
        self.repo_str = repo_str
        self.project_name = project_name
        self.description = description
        self.old_version_directory = cwd + "/" + self.project_name + "/oldVersion/"
        self.old_version_commit = old_version_commit
        self.old_version_patch = old_version_patch
        self.old_version_build = old_version_build
        self.new_version_directory = cwd + "/" + self.project_name + "/newVersion/"
        self.new_version_commit = new_version_commit
        self.new_version_patch = new_version_patch
        self.new_version_build = new_version_build
        self.repo_name = self.obtainRepoName()

    def obtainRepoName(self):
        """
        Strips the repository url so that we obtain the name
        :return: No return value - Updates self.repo_name in __init__
        """
        repo_len = len(self.repo_str)
        index = 0
        for i in reversed(range(0, repo_len)):
            if self.repo_str[i] == '/':
                index = i
                break
        repo_name = self.repo_str[index + 1:-4] + "/"
        return repo_name

    def createFolders(self):
        """
        Creates folders pertaining the two versions of the repository
        project_name specified in the .json will be the name of the root directory
        :return: No return value - Updates the file hierarchy
        """
        try:
            os.mkdir(self.project_name)
            oldVersion = self.project_name + "/oldVersion/"
            newVersion = self.project_name + "/newVersion/"
            os.mkdir(oldVersion)
            os.mkdir(newVersion)
        except FileExistsError as e:
            print("Folder already exists! Please change 'project_name' in .json to create a new folder!")
            print(e.args)
            exit(0)

    def cloneRepos(self):
        """
        Clones the repositories by using synchronous method calls in shell
        Loads both versions into two different directories at commit specified
        :return: No return value - Repositories are generated in corresponding version folders
        """
        subprocess.call(["git", "clone", self.repo_str], cwd=self.old_version_directory)
        subprocess.call(["git", "checkout", self.old_version_commit], cwd=self.old_version_directory + self.repo_name)
        subprocess.call(["git", "clone", self.repo_str], cwd=self.new_version_directory)
        subprocess.call(["git", "checkout", self.new_version_commit], cwd=self.new_version_directory + self.repo_name)

    def applyPatches(self):
        """
        Applies bug_fix or regression test case to corresponding alternate version.
        Bug_fix implies that the patch is applied to old version.
        Regression implies that the patch is applied to the new version.
        Once the patch has been applied, one of the versions will fail when building because of the failing test case.
        """
        if platform == "linux" or platform == "linux2":
            if self.old_version_patch != "None":
                directoryPath = self.project_name + "/oldVersion/" + self.repo_name
                cmd = "patch -p1 -d " + directoryPath + "<" + self.old_version_patch
                subprocess.call(cmd, shell=True)
            if self.new_version_patch != "None":
                directoryPath = self.project_name + "/newVersion/" + self.repo_name
                cmd = "patch -p1 -d " + directoryPath + "<" + self.new_version_patch
                subprocess.call(cmd, shell=True)
        elif platform == "win32" or platform == "win64":
            if self.old_version_patch != "None":
                directoryPath = "--directory=" + self.project_name + "/oldVersion/" + self.repo_name
                cmd = "powershell -Command Get-Content " + self.old_version_patch + " | " + "git apply " + directoryPath
                subprocess.call(cmd, shell=True)
            if self.new_version_patch != "None":
                directoryPath = "--directory=" + self.project_name + "/newVersion/" + self.repo_name
                cmd = "powershell -Command Get-Content " + self.new_version_patch + " | " + "git apply " + directoryPath
                subprocess.call(cmd, shell=True)

    def buildOldVersion(self):
        if self.old_version_build == "maven":
            subprocess.call("mvn install", cwd=self.old_version_directory + self.repo_name, shell=True)
        elif self.old_version_build == "ant":
            if os.environ["ANT_HOME"]:
                subprocess.call("ant", cwd=self.old_version_directory + self.repo_name, shell=True)
            else:
                raise Exception("ANT_HOME environment variable not set!")

    def buildNewVersion(self):
        if self.new_version_build == "maven":
            subprocess.call("mvn install", cwd=self.new_version_directory + self.repo_name, shell=True)
        elif self.new_version_build == "ant":
            if os.environ["ANT_HOME"]:
                subprocess.call("ant", cwd=self.new_version_directory + self.repo_name, shell=True)
            else:
                raise Exception("ANT_HOME environment variable not set!")


def configureJava8Dependancy():
    """
    Sets the JAVA_HOME environmental variable to jdk1.8.* only during execution of this script.
    Linux : Assumes that the jdk installation is found in ~/jdk/
    Windows : Assumes that the jdk installation is found in C:/Program Files/Java
    If installation is not found, an exception is raised.
    """
    if "JAVA_HOME" in os.environ and "jdk1.8" in os.environ["JAVA_HOME"]:  # jdk1.8.* is already set as JAVA_HOME env variable
        return True
    if platform == "linux" or platform == "linux2":  # linux
        home = str(Path.home())
        p = Path(home + "/jvm/")
        javaFolderPaths = [x for x in p.iterdir() if x.is_dir()]  # Obtain list of possible paths in 'Java' directory
        jdk8 = None
        for folder in javaFolderPaths:
            m = re.search("jdk1.8.*", str(folder))  # Regex to find jdk1.8
            if m is not None:
                jdk8 = m.string  # Found a match so we set jdk8
        if jdk8 is not None:
            os.environ["JAVA_HOME"] = jdk8  # Valid version of jdk1.8 found so we set the env variable
            return True
        raise Exception("jdk1.8 is not installed in ~/jvm/")  # Did not find a compatible version
    elif platform == "win32" or platform == "win64":  # windows
        p = Path("C:/Program Files/Java/")
        javaFolderPaths = [x for x in p.iterdir() if x.is_dir()]  # Obtain list of possible paths in 'Java' directory
        jdk8 = None
        for folder in javaFolderPaths:
            m = re.search("jdk1.8.*", str(folder))  # Regex to find jdk1.8
            if m is not None:
                jdk8 = m.string  # Found a match so we set jdk8
        if jdk8 is not None:
            os.environ["JAVA_HOME"] = jdk8  # Valid version of jdk1.8 found so we set the env variable
            return True
        raise Exception("jdk1.8 is not installed in C:/Program Files/Java")  # Did not find a compatible version


def loadData():
    """
    Loads data from the json file specified. Each json file pertains to a different bug fix/regression raised.
    :return: VersionTool object with repository/commit information
    """
    file = open("CLI-185Config/ApacheCommonsCLI185.json", )  # Specify the json file containing all repository information
    data = json.load(file)
    return VersionTool(data["repo_url"], data["project_name"], data["description"], os.getcwd(), data["old_version"]["commit_id"],  data["old_version"]["patch"], data["old_version"]["build"],
                       data["new_version"]["commit_id"], data["new_version"]["patch"], data["new_version"]["build"])


def main():
    configureJava8Dependancy()
    vt = loadData()
    vt.createFolders()
    vt.cloneRepos()
    vt.applyPatches()
    vt.buildOldVersion()
    vt.buildNewVersion()
    print(vt.description)


main()

