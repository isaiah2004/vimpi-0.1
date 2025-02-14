from src.main import VimPi
from src.main import VimPi, TextViewer
import os
import logging
import pytest
from pathlib import Path
import tempfile
import os
import shutil
import time

from src.utils.Utils import Drive

async def test_screens():
    app = VimPi()
    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"
        
        assert app.query_one("#home-screen") is not None
        
from src.main import VimPi, TextViewer
import os


# TEST SCREEN SWITCHING
async def test_editor_screen_switching():
    path = os.getcwd()
    app = VimPi(path)

    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        await pilot._wait_for_screen(0.30)
        # (app.screen_stack)
        assert app.screen.name == "FileExplorer"

        await pilot.press("ctrl+f")
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        assert app.screen.name == "FileExplorer"


# test editor screen layout
async def test_layout():
    app = VimPi()

    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        assert app.screen.name == "FileExplorer"

        assert app.query_one("#FileExplorerPanel") is not None

        assert app.query_one("#editor") is not None
        childrenNodes = app.query_one("#FileExplorerPanel").query_children()
        assert childrenNodes is not None


# test file loading
async def test_file_loading():
    app = VimPi()
    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        assert app.screen.name == "FileExplorer"

        fileContent = "This is a text file that is built solely for testing"
        with open("test.txt", "w") as f:
            f.write(fileContent)
            f.close()

        await pilot.press("tab")
        StepsToTestFile = os.listdir(os.getcwd()).index("test.txt") + 2

        for i in range(StepsToTestFile):
            await pilot.press("down")
        await pilot.press("enter")

        LoadedText = app.query_one(TextViewer).text
        assert "This is a text file that is built solely for testing" in LoadedText


# test file saving
async def test_file_saving():
    app = VimPi()
    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        assert app.screen.name == "FileExplorer"

        fileContentBeforeEdit = "This is a text file that is built solely for testing\nthe capabilities of file loading\n"
        with open("test.txt", "w") as f:
            f.write(fileContentBeforeEdit)
            f.close()

        t = [
            i
            for i in os.listdir(os.getcwd())
            if os.path.isdir(os.path.join(os.getcwd(), i))
        ] + [
            i
            for i in os.listdir(os.getcwd())
            if not os.path.isdir(os.path.join(os.getcwd(), i))
        ]
        StepsToTestFile = t.index("test.txt") + 1
        await pilot.press("tab")
        for i in range(StepsToTestFile):
            await pilot.press("down")
        await pilot.press("enter")

        await pilot.press("tab")
        for i in range(3):
            await pilot.press("down")
        await pilot.press("h", "e", "l", "l", "o")
        await pilot.press("ctrl+s")

        with open("test.txt", "r") as f:
            assert "hello" in "".join(f.readlines())

# tests/test_drive.py



@pytest.fixture(scope='session')
def test_environment():
    # Initialize Drive object
    credentials_path = Path(__file__).parent.parent  # Adjust as needed
    drive = Drive(credentials_path=credentials_path, use_service_account=True)

    # Create a unique test folder name
    test_folder_name = f"vim_pi_test_{int(time.time())}"

    # Create test folder in Google Drive
    test_folder_id = drive.get_or_create_folder(test_folder_name)

    # Create a temporary local directory
    temp_dir = tempfile.mkdtemp()

    # Yield the drive object, test folder ID, and temp directory
    yield drive, test_folder_id, temp_dir

    # Clean up after tests
    # Delete test folder from Google Drive
    drive.delete_file_or_folder(test_folder_id)

    # Remove temporary local directory
    shutil.rmtree(temp_dir)

def test_get_or_create_folder(test_environment):
    drive, test_folder_id, temp_dir = test_environment

    # Try to get or create a subfolder in the test folder
    subfolder_name = 'test_subfolder'
    folder_id = drive.upload_folder(subfolder_name, test_folder_id)

    # The folder should be created, check that folder_id is not None
    assert folder_id is not False

    # Clean up: delete the created folder
    drive.delete_file_or_folder(folder_id)

def test_upload_and_download_file(test_environment):
    drive, test_folder_id, temp_dir = test_environment

    # Create a test file in the local temp directory
    test_file_name = 'test_file.txt'
    test_file_path = os.path.join(temp_dir, test_file_name)

    with open(test_file_path, 'w') as f:
        f.write('This is a test file.')

    # Upload the file to Google Drive
    uploaded_file = drive.upload_file(test_file_name, temp_dir, test_folder_id)

    # Check that uploaded_file is not False
    assert uploaded_file is not False

    # Now delete the local file
    os.remove(test_file_path)

    # Now download the file from Google Drive
    drive.download_file(test_file_name, temp_dir, uploaded_file['id'])

    # Check that the file has been downloaded
    assert os.path.exists(test_file_path)

    # Check that the content matches
    with open(test_file_path, 'r') as f:
        content = f.read()
    assert content == 'This is a test file.'

def test_list_files(test_environment):
    drive, test_folder_id, temp_dir = test_environment

    # Upload a test file to Google Drive
    test_file_name = 'test_file_list.txt'
    test_file_path = os.path.join(temp_dir, test_file_name)

    with open(test_file_path, 'w') as f:
        f.write('File for listing test.')

    drive.upload_file(test_file_name, temp_dir, test_folder_id)

    # List files in the test folder
    files = drive.list_files(test_folder_id)

    # Check that the uploaded file is in the list
    assert test_file_name in files['names']

def test_upload_folder(test_environment):
    drive, test_folder_id, temp_dir = test_environment

    # Create a local subfolder with a test file
    subfolder_name = 'test_upload_folder'
    subfolder_path = os.path.join(temp_dir, subfolder_name)
    os.mkdir(subfolder_path)

    test_file_name = 'test_file_in_folder.txt'
    test_file_path = os.path.join(subfolder_path, test_file_name)

    with open(test_file_path, 'w') as f:
        f.write('File inside a folder.')

    # Upload the folder to Google Drive
    folder_id = drive.upload_folder(subfolder_name, test_folder_id)
    assert folder_id is not False

    # Upload the file inside the folder
    uploaded_file = drive.upload_file(test_file_name, subfolder_path, folder_id)
    assert uploaded_file is not False

    # List files in the uploaded folder
    files = drive.list_files(folder_id)
    assert test_file_name in files['names']

    # Clean up: delete the created folder
    drive.delete_file_or_folder(folder_id)

def test_synchronize(test_environment):
    drive, test_folder_id, temp_dir = test_environment

    # Create some files and folders in the local temp directory
    # File 1
    test_file_name1 = 'sync_file1.txt'
    test_file_path1 = os.path.join(temp_dir, test_file_name1)
    with open(test_file_path1, 'w') as f:
        f.write('This is sync test file 1.')

    # Subfolder
    subfolder_name = 'sync_subfolder'
    subfolder_path = os.path.join(temp_dir, subfolder_name)
    os.mkdir(subfolder_path)

    # File 2 inside subfolder
    test_file_name2 = 'sync_file2.txt'
    test_file_path2 = os.path.join(subfolder_path, test_file_name2)
    with open(test_file_path2, 'w') as f:
        f.write('This is sync test file 2.')

    # Synchronize local directory with Google Drive folder
    drive.synchronize(temp_dir, test_folder_id)

    # List files in Google Drive folder
    files = drive.list_files(test_folder_id)
    assert test_file_name1 in files['names']
    assert subfolder_name in files['names']

    # List files in subfolder on Google Drive
    subfolder_id = next((item['id'] for item in files['all'] if item['name'] == subfolder_name), None)
    assert subfolder_id is not None

    subfolder_files = drive.list_files(subfolder_id)
    assert test_file_name2 in subfolder_files['names']

    # Now modify a local file and synchronize again
    with open(test_file_path1, 'w') as f:
        f.write('This is the updated content of sync test file 1.')

    drive.synchronize(temp_dir, test_folder_id)

    # Refresh the file list after synchronization
    files = drive.list_files(test_folder_id)

    # Download the file from Google Drive and check content
    file_id = next((item['id'] for item in files['all'] if item['name'] == test_file_name1), None)
    assert file_id is not None, f"File {test_file_name1} not found in Google Drive folder"

    # Create a new directory for downloaded files
    download_dir = os.path.join(temp_dir, 'downloaded')
    os.makedirs(download_dir, exist_ok=True)

    # Download the file
    drive.download_file(test_file_name1, download_dir, file_id)

    # Add a small delay to ensure the file has been downloaded
    time.sleep(2)

    # Check if file exists before opening
    download_path = os.path.join(download_dir, test_file_name1)
    assert os.path.exists(download_path), f"Downloaded file not found at {download_path}"

    with open(download_path, 'r') as f:
        content = f.read()
    assert content == 'This is the updated content of sync test file 1.'

    # Clean up: delete downloaded file and directory
    os.remove(download_path)
    os.rmdir(download_dir)
    


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

#test file loading
async def test_copy():
    app = VimPi()
    async with app.run_test() as pilot:
        await pilot._wait_for_screen(0.30)
        assert app.screen.name == "Home"

        await pilot.press("ctrl+f")
        assert app.screen.name == "FileExplorer"

        await pilot.press("tab")
        StepsToTestFile = os.listdir(os.getcwd()).index('test.txt')+2

        for i in range(StepsToTestFile):
            await pilot.press("down")
        await pilot.press("enter")
        
        await pilot.press('tab')
        
        for i in range(3):
            await pilot.press('shift+down')
        await pilot.press('ctrl+insert')
        await pilot.press('right')
        await pilot.press('enter')
        await pilot.press('enter')
        await pilot.press('alt+insert')
        
        FinalText = app.query_one(TextViewer).text
        
        expectedText=r'''This is a text file that is built solely for testing
the capabilities of file loading
hello

This is a text file that is built solely for testing
the capabilities of file loading
hello'''

        assert FinalText == expectedText