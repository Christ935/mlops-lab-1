Q1
uv init created the basic Python project structure. .python-version stores the Python version used by the project. pyproject.toml contains the project configuration, metadata, and dependencies. README.md contains documentation for the project. The src/lab1 directory contains the Python package source code, and __init__.py identifies it as a Python package.


Q2
dvc init created the .dvc directory and .dvcignore. .dvc/config contains the DVC project configuration. .dvc/.gitignore prevents internal DVC temporary/cache files from being tracked by Git. .dvc/tmp contains temporary internal DVC files. .dvcignore tells DVC which files it should ignore.
The non-secret DVC configuration files and .dvcignore should be committed to Git, while temporary files should not be committed.


Q3
I configured the DagsHub credentials using:
dvc remote modify origin --global user Christ935
dvc remote modify origin --global password token
Because --global was used, the DagsHub credentials are stored in the user's global DVC configuration outside the Git repository.
Other configuration scopes include the repository-level configuration, --local, and --system.
Credentials and access tokens should never be pushed to GitHub because they are secret.

Q4
After running:
dvc add data
DVC added the data folder to .gitignore.
This prevents Git from tracking the actual dataset because the dataset is managed and versioned by DVC instead.


Q5
The data.dvc file is a DVC pointer file. It contains metadata about the dataset such as its hash/checksum, size, number of files, and path.
Git tracks this small pointer file instead of tracking the actual dataset.
The contents of my data.dvc file were:
outs:
- md5: a3a457d03c51ff8b037a833440f6ad13.dir
  size: 1188442712
  nfiles: 16643
  hash: md5
  path: data


Q6
On GitHub, the project code and the data.dvc pointer file are present, but the actual dataset is not stored there because the data folder is ignored by Git.
The data.dvc file contains the information needed by DVC to identify the correct version of the dataset.
I initially configured DagsHub as the DVC remote, but the upload repeatedly failed because of server disconnections and timeouts.
Therefore, I used the local DVC remote option recommended in the lab instructions.
The full dataset was not successfully uploaded to DagsHub. Instead, the actual dataset is stored in my local DVC remote outside the Git repository.

Q7
I cloned the GitHub repository into a new temporary folder to check if the dataset was included automatically.
Commands used:
git clone https://github.com/Christ935/MLops1.git lab1-test
cd lab1-test
After cloning, the actual data folder was not present because Git only stores the project files and the data.dvc pointer, not the dataset itself.
Because I used a local DVC remote instead of DagsHub, I connected the temporary clone to the same local remote using:
dvc remote add --local localremote C:\Users\96176\Desktop\MLOps-AI\MLOps-DVC-Remote
dvc remote default --local localremote
Then I downloaded the dataset using:
dvc pull
After dvc pull finished, the data/food11_raw folder was restored with the training, evaluation, and validation folders.
This shows that git clone retrieves the code and DVC pointer files, while dvc pull retrieves the actual dataset.

Q8
To test how Git and DVC work together for versioning, I first listed the commits that changed data.dvc:
git log --oneline -- data.dvc
I then switched to the older commit:
git checkout 9d59e23
and restored the dataset version linked to that commit:
dvc checkout
After checking the data folder with:
dir data
only food11_raw was present. The food11_processed and food11_processed_mini folders were no longer there because they did not exist in that older dataset version.
This shows that Git switches the project/code version, while DVC switches the dataset version associated with that commit.
To return to the latest version, I used:
git checkout master
dvc checkout
The latest dataset version was then restored, including food11_raw, food11_processed, and food11_processed_mini.