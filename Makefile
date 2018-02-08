export KUBECONFIG=config/do.yaml

all: deploy

login:
	docker login r.secretpool.org

build:
	docker build . -t gearbot:latest
	docker tag gearbot:latest r.secretpool.org/admin/gearbot:latest
	docker push r.secretpool.org/admin/gearbot:latest

create: build
	kubectl create -f pod.yaml

deploy: build
	kubectl apply -f pod.yaml

delete:
	kubectl delete gearbot

status:
	kubectl get pod gearbot -o yaml

create-secret:
	kubectl create secret docker-registry r.secretpool.org \
		--docker-server=r.secretpool.org \
		--docker-username=admin \
		--docker-password='wMl2?5VgSuEaVCbC' \
		--docker-email=admin@secretpool.org

logs:
	kubectl logs gearbot -f

ssh:
	kubectl exec -it gearbot -- /bin/bash
