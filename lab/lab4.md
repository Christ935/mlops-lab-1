Q1
Without a volume, everything MLflow writes to /mlflow-data stays inside that specific container. Stopping the container keeps the data, but once we remove the container, the data is lost. When we started a new container from the same image, MLflow was fresh again with no previous runs, models, or registry data.

Q2
A named volume is useful because Docker manages it separately from the containers, so the MLflow database and artifacts survive container removal and recreation. A bind mount would also work, but it depends on a specific folder on the host machine. For this Compose setup, a named volume is cleaner and more portable.

Q3
In Lab 3, MLflow was running directly on the host, so the inference container needed host.docker.internal to reach it. In Lab 4, MLflow and inference are on the same Docker Compose network. Docker provides internal DNS, so the hostname mlflow automatically points to the MLflow container and we can use http://mlflow:5000.

Q4
INFERENCE_URL is stored in an environment variable so the same frontend image can work in different environments. Inside Compose we use http://inference:8000, while if we run the frontend separately we can use http://127.0.0.1:8000 or another address without changing the Python code.

Q5
The inference service does not need a published host port because only the frontend communicates with it. Inside the Compose network, the frontend reaches it using http://inference:8000. We only published ports for services we needed to open from the host: MLflow on 5000 and the frontend on 8501.

Q6
depends_on only makes sure the MLflow container starts before inference. It does not guarantee that MLflow is already ready to accept requests. Since serve.py loads the model at startup, inference can fail and exit if MLflow is not ready yet. Retry logic or a health check would make this more reliable.

Q7
Our docker compose ps showed that MLflow published port 5000 and the frontend published port 8501. Inference only showed 8000/tcp internally and had no host mapping. This matched our docker-compose.yml exactly.

Q8
When we registered Version 2 and moved the champion alias from Version 1 to Version 2, the running inference container did not automatically switch models. It kept using the model it had already loaded at startup. After running:
docker compose restart inference

the service started again and loaded the new model pointed to by champion.

Q9
A restart was enough because the inference application code and dependencies were already inside the Docker image. The actual MLflow model is fetched when the container starts. So changing the model version does not require rebuilding the image; restarting inference is enough to load the new champion model.

Q10
After docker compose down followed by docker compose up, our MLflow runs and model versions were still there because the mlflow-data named volume was preserved. After running docker compose down -v, the volume was deleted too. When we started the stack again, MLflow was completely fresh, with only the default experiment, and the inference service exited because food11@champion no longer existed.

Q11
Docker Compose is mainly designed for running services on one machine. To run several inference replicas behind a load balancer or survive a machine failure, we would need a distributed orchestrator such as Kubernetes or Docker Swarm. We would also need shared persistent storage and an external database/artifact store for MLflow so its data is not tied to one machine.