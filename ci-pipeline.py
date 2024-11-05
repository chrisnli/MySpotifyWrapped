import subprocess
from shutil import which, rmtree
import sys
from os import getcwd
from os.path import basename, isdir

python = "python"
extension = ""
passed_lints = False
passed_tests = True

def ensure_right_cwd():
    print("Ensuring correct working directory")
    if basename(getcwd()) != "SpotifyWrapped":
        sys.exit("Please run this script in the root of the project")

def ensure_system_dependencies():
    print("Ensuring system dependencies are present")
    if which("git") is None:
        sys.exit("Please ensure git is installed")
    if which("python") is None:
        if which("python3") is not None:
            global python
            python = "python3"
        else:
            sys.exit("Please ensure python3 is installed")
    if sys.platform == "windows":
        global extension
        extension = ".exe"

def ensure_venv_dependencies():
    print("Ensuring venv is reproducible and has required dependencies")
    global python
    if isdir(".venv"):
        rmtree(".venv")
    subprocess.run([python, "-m", "venv", ".venv"], check=True)
    python = ".venv/Scripts/python" + extension
    subprocess.run([python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    command = [python, "-m", "pip", "install"]
    with open("requirements.txt", "r") as reqs:
        for req in reqs:
            command.append(req.strip())
    subprocess.run(command, check=True)


def run_lints():
    print("Running formatting checks")
    global passed_lints
    files = subprocess.run(["git", "ls-files", "spotify_wrapped/*.py"], check=True, capture_output=True).stdout
    files = files.decode()
    files = files.replace("\n", " ")
    output = subprocess.run(".venv/Scripts/pylint" + extension + " --load-plugins pylint_django --django-settings-module=spotify_wrapped.settings " + files)
    if output.returncode != 0:
        passed_lints = False
        print("Failed formatting checks")
    else:
        passed_lints = True
        print("Passed formatting checks")

def run_tests():
    print("Running tests")
    global passed_tests
    subprocess.run([".venv/Scripts/coverage" + extension, "run", "manage.py", "test"])
    output = subprocess.run([".venv/Scripts/coverage" + extension, "report", "--fail-under=80"])
    if output.returncode != 0:
        passed_tests = False
        print("Failed tests")
    else:
        passed_tests = True
        print("Passed tests")

def final_grade():
    global passed_lints, passed_tests
    print("\nSummary:")
    if passed_lints and passed_tests:
        print("\tNo issues found")
        sys.exit(0)
    else:
        if not passed_lints:
            print("\tFailed formatting checks")
        if not passed_tests:
            print("\tFailed tests")
        sys.exit(1)

if __name__ == "__main__":
    ensure_right_cwd()
    ensure_system_dependencies()
    ensure_venv_dependencies()
    run_lints()
    run_tests()
    final_grade()