export KUBECONFIG=config/gke.yaml
export GIT_SHA=$(shell git rev-parse --short=8 HEAD)

all: deploy

build:
	docker build . -t gearbot:$(GIT_SHA)
	docker tag gearbot:$(GIT_SHA) gcr.io/secret-pool/gearbot:$(GIT_SHA)
	gcloud docker -- push gcr.io/secret-pool/gearbot:$(GIT_SHA)

create: build
	kubectl create -f pod.yaml

delete:
	kubectl delete -f pod.yaml

deploy: build
	kubectl set image -f pod.yaml gearbot=gcr.io/secret-pool/gearbot:$(GIT_SHA)

status:
	kubectl get pod gearbot -o yaml

logs:
	kubectl logs gearbot -f

ssh:
	kubectl exec -it gearbot -- /bin/bash
