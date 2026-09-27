import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights


# --------------------------------------------------
# Keep CPU usage moderate
# --------------------------------------------------
torch.set_num_threads(4)
torch.set_num_interop_threads(2)


# --------------------------------------------------
# Command-line arguments
# --------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument(
    "--dataset",
    choices=["processed", "mini"],
    default="mini"
)

parser.add_argument(
    "--epochs",
    type=int,
    default=5
)

parser.add_argument(
    "--lr",
    type=float,
    default=0.001
)

parser.add_argument(
    "--batch-size",
    type=int,
    default=32
)

args = parser.parse_args()


# --------------------------------------------------
# MLflow setup
# --------------------------------------------------
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("food11")


# --------------------------------------------------
# Dataset paths
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]

if args.dataset == "mini":
    DATA_DIR = ROOT / "data" / "food11_processed_mini"
else:
    DATA_DIR = ROOT / "data" / "food11_processed"

train_dir = DATA_DIR / "training"
val_dir = DATA_DIR / "validation"
test_dir = DATA_DIR / "evaluation"


# --------------------------------------------------
# Image transforms
# --------------------------------------------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# Load datasets
# --------------------------------------------------
train_dataset = datasets.ImageFolder(
    train_dir,
    transform=transform
)

val_dataset = datasets.ImageFolder(
    val_dir,
    transform=transform
)

test_dataset = datasets.ImageFolder(
    test_dir,
    transform=transform
)

assert len(train_dataset.classes) == 11, (
    f"Expected 11 classes, found {len(train_dataset.classes)}"
)


train_loader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=args.batch_size,
    shuffle=False,
    num_workers=0
)

test_loader = DataLoader(
    test_dataset,
    batch_size=args.batch_size,
    shuffle=False,
    num_workers=0
)


# --------------------------------------------------
# Device
# --------------------------------------------------
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Using device: {device}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


# --------------------------------------------------
# Pretrained ResNet18
# --------------------------------------------------
weights = ResNet18_Weights.DEFAULT

model = resnet18(weights=weights)


# Freeze pretrained layers to reduce training load
for parameter in model.parameters():
    parameter.requires_grad = False


# Replace ResNet18's 1000-class output layer
# with an 11-class Food-11 output layer
model.fc = nn.Linear(
    model.fc.in_features,
    11
)

model = model.to(device)


# --------------------------------------------------
# Loss and optimizer
# --------------------------------------------------
criterion = nn.CrossEntropyLoss()

# Only train the new final layer
optimizer = torch.optim.Adam(
    model.fc.parameters(),
    lr=args.lr
)


# --------------------------------------------------
# Evaluation function
# --------------------------------------------------
def evaluate(loader):

    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            total_loss += loss.item()

            _, predictions = torch.max(
                outputs,
                1
            )

            total += labels.size(0)

            correct += (
                predictions == labels
            ).sum().item()

    average_loss = total_loss / len(loader)
    accuracy = correct / total

    return average_loss, accuracy


# --------------------------------------------------
# MLflow training run
# --------------------------------------------------
with mlflow.start_run():

    # Log hyperparameters
    mlflow.log_params({
        "dataset": args.dataset,
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "model": "resnet18",
        "device": str(device),
        "training": "final_layer_only"
    })


    # --------------------------------------------------
    # Training loop
    # --------------------------------------------------
    for epoch in range(args.epochs):

        model.train()

        total_train_loss = 0.0

        for images, labels in train_loader:

            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            loss.backward()

            optimizer.step()

            total_train_loss += loss.item()


        train_loss = (
            total_train_loss /
            len(train_loader)
        )


        # Validation
        val_loss, val_accuracy = evaluate(
            val_loader
        )


        print(
            f"Epoch {epoch + 1}/{args.epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Accuracy: {val_accuracy:.4f}"
        )


        # Log metrics for each epoch
        mlflow.log_metric(
            "train_loss",
            train_loss,
            step=epoch
        )

        mlflow.log_metric(
            "val_loss",
            val_loss,
            step=epoch
        )

        mlflow.log_metric(
            "val_accuracy",
            val_accuracy,
            step=epoch
        )


    # --------------------------------------------------
    # Final test
    # --------------------------------------------------
    test_loss, test_accuracy = evaluate(
        test_loader
    )


    print(
        f"Final Test Accuracy: "
        f"{test_accuracy:.4f}"
    )


    mlflow.log_metric(
        "test_accuracy",
        test_accuracy
    )


    # --------------------------------------------------
    # Save trained model to MLflow
    # --------------------------------------------------

    # --------------------------------------------------
# Save trained model to MLflow
# --------------------------------------------------
input_example = torch.randn(
    1,
    3,
    128,
    128
)

mlflow.pytorch.log_model(
    model,
    name="model",
    input_example=input_example,
    serialization_format="pickle"
)