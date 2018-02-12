export KUBECONFIG=config/gke.yaml

all: deploy

build:
	docker build . -t gearbot:latest
	docker tag gearbot:latest gcr.io/secret-pool/gearbot:latest
	gcloud docker -- push gcr.io/secret-pool/gearbot:latest

create: build
	kubectl create -f pod.yaml

delete: delete
	kubectl delete -f pod.yaml

deploy: delete create

status:
	kubectl get pod gearbot -o yaml

logs:
	kubectl logs gearbot -f

ssh:
	kubectl exec -it gearbot -- /bin/bash
