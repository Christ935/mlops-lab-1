Q1
The model was registered as Version 1.
A logged model artifact belongs to a specific MLflow training run and stores the actual model files produced by that run. A registered model gives that model a permanent name and version in the Model Registry, making it easier to manage, compare, and deploy independently of the original run.

Q2
Aliases such as champion and challenger replace the old fixed stages like Staging and Production. Model versions are separate from runs so multiple trained models can be managed under one registered model name. An alias is more flexible because it can be moved from one model version to another without changing the version itself.

Q3
We load the model using models:/food11@champion instead of a .pth file because MLflow manages the model version, dependencies, and metadata for us. The champion alias points to the model version we want to serve. To serve a newer version, we register the new model and move the champion alias to it. The API code does not need to change; we only need to restart the API/container so it loads the new champion model.

Q4
We copy pyproject.toml and uv.lock first so Docker can cache the dependency-installation layer. If only serve.py changes, Docker can reuse the already-built dependency layer and only rebuild the later source-code layer, making rebuilds much faster.

Q5
The naive single-stage image is 6.32 GB, while the multi-stage image is 6.24 GB, so the multi-stage build saves about 80 MB (around 1.3%).
Using docker history, the largest layer in the multi-stage image is the copied virtual environment at about 6.11 GB. This contains heavy dependencies such as PyTorch, torchvision, and MLflow. The actual source-code layer is only about 23.2 KB.
The size difference is relatively small because most of the image size comes from runtime Python dependencies, which are required in both images. The multi-stage build mainly removes build-only tools and temporary files.

Q6
Forgetting .dockerignore makes the build context much larger, which slows builds and can increase image size if unnecessary files are copied. Large folders like data/, .venv/, mlruns/, and .git/ are especially unnecessary. A local .venv/ can also cause problems if copied because it was built for the host system rather than the container environment.

Q7
The container cannot use 127.0.0.1:5000 to reach MLflow on the host because 127.0.0.1 inside the container refers to the container itself, not the Windows host machine. On Windows and macOS, host.docker.internal resolves to the host machine so the container can access services such as the MLflow server running on port 5000.

Q8
Yes. After stopping the container and starting a new container from the same Docker image, the model still loaded and predictions worked without rebuilding the image. The application code and Python dependencies are baked into the Docker image, while the model itself is fetched from MLflow at runtime using models:/food11@champion. This means the champion model can be updated without rebuilding the Docker image.

Q9
What is still missing is a container registry. The image currently exists only on my local machine. To allow another machine, CI runner, or Kubernetes cluster to reliably run the exact same image, I would need to tag and push it to a registry such as Docker Hub or GitHub Container Registry. For reproducibility, the deployment should use a specific immutable image tag or image digest rather than only latest. The running container also needs network access to the MLflow server because the champion model is fetched at runtime.