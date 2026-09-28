Q1

After running:

uv add mlflow torch torchvision scikit-learn

pyproject.toml was updated to include these libraries as project dependencies.

uv.lock was also updated with the exact versions of these packages and all of their required dependencies. This makes sure the same environment can be reproduced later with the same package versions.

Q2

--backend-store-uri tells MLflow where to store experiment metadata such as runs, parameters, metrics, and run information. In this lab it uses a SQLite database:

sqlite:///mlflow.db

--default-artifact-root tells MLflow where to store larger output files produced by runs, such as trained models and other artifacts. In this lab they are stored in:

./mlruns

Metadata describes the experiment and its results, while artifacts are the actual files produced by a run, such as the saved trained model.

Q3

mlflow.db and mlruns/ should not be tracked by Git because they are local outputs created by MLflow, not source code.

They also should not be tracked by DVC because DVC is being used to version the dataset, while MLflow already manages experiment metadata, metrics, and model artifacts.

Tracking them again with Git or DVC would be unnecessary and would create duplicated or constantly changing files.


We then open another terminal where we run the commands:
echo mlflow.db>>.gitignore
echo mlruns/>>.gitignore
git add .gitignore
git commit -m "Ignore local mlflow tracking files"
git push origin master

Q4

When mlflow.set_experiment("food11") is called for the first time and the experiment does not already exist, MLflow automatically creates a new experiment named "food11".
After refreshing the MLflow UI, I could see the new food11 experiment listed alongside the Default experiment.

Q5

mlflow.log_param is used to record fixed settings chosen before training, such as the learning rate, batch size, number of epochs, and model type.

mlflow.log_metric is used to record values produced during training, such as train loss, validation loss, and validation accuracy.

log_metric uses a step argument because metrics can change over time. In this lab, the step represents the epoch, which allows MLflow to plot how the metrics change during training.

Parameters do not need a step because they stay fixed for the entire run.

Q6

I opened the successful MLflow run and found the logged parameters, including the dataset, epochs, learning rate, batch size, model, device, and training method.

I also found the train_loss, val_loss, val_accuracy, and test_accuracy metrics. The training and validation metrics were logged at every epoch, so MLflow can show how they changed during training.

The trained ResNet18 model was logged using mlflow.pytorch.log_model().

In my MLflow setup, the model is stored separately from the normal run artifacts. The actual model file is stored locally at:

C:\Users\96176\Desktop\MLOps-AI\lab1\mlruns\1\models\m-c9588c776444482e95b85eee7dced920\artifacts\data\model.pth

The MLflow model metadata file is stored at:

C:\Users\96176\Desktop\MLOps-AI\lab1\mlruns\1\models\m-c9588c776444482e95b85eee7dced920\artifacts\MLmodel

Q7

The learning rate that gave the best validation accuracy was:

lr = 0.001

with a val_accuracy of approximately 0.592.

The results were:

lr = 0.01    -> val_accuracy = 0.572
lr = 0.001   -> val_accuracy = 0.592
lr = 0.0001  -> val_accuracy = 0.262

A higher learning rate is not always better. In this experiment, 0.001 performed better than both 0.01 and 0.0001.

This shows that the learning rate needs to be balanced: too low can make learning too slow, while a higher value does not necessarily improve the result.

Q8

From the parallel coordinates plot, the best result was obtained with:

lr = 0.001
batch_size = 32
val_accuracy = 0.592

Using the same learning rate with a larger batch size of 64 reduced the validation accuracy to about 0.559.

The learning rate 0.01 with batch size 32 also performed reasonably well with about 0.572 validation accuracy, while the very small learning rate 0.0001 performed much worse at about 0.262.

The main pattern is that a moderate learning rate of 0.001 with batch size 32 gave the best validation result in these experiments.

Q9

After sorting the runs by val_accuracy in descending order, the best run was:

Run name: spiffy-fox-287
Run ID: 9a7649e5139945ccb4dd64a0173ebde8

Parameters:
lr = 0.001
batch_size = 32
epochs = 5
dataset = mini

Results:
val_accuracy = approximately 0.592
test_accuracy = approximately 0.635

