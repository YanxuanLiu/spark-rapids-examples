import docker
import time
client=docker.from_env()
containers=client.containers.list(filters={"name": "spark-triton"})
if containers:
    print(">>>> containers: {}".format([c.short_id for c in containers]))
else:
    container=client.containers.run(
        "nvcr.io/nvidia/tritonserver:24.08-py3", "tritonserver --model-repository=/models",
        detach=True,
        device_requests=[docker.types.DeviceRequest(device_ids=["0"], capabilities=[['gpu']])],
        name="spark-triton",
        network_mode="host",
        remove=True,
        shm_size="64M",
        # volumes={triton_models_dir: {"bind": "/models", "mode": "ro"}}
    )
    print(">>>> starting triton: {}".format(container.short_id))

    # wait for triton to be running
    time.sleep(15)
    client = grpcclient.InferenceServerClient("localhost:8001")
    ready = False
    while not ready:
        try:
            ready = client.is_server_ready()
        except Exception as e:
            time.sleep(5)
        