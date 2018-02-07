# Shared rancher config
DOCKER_CERT_PATH	:= ./certs
DOCKER_HOST 		:= tcp://159.89.141.210:2376
DOCKER_MACHINE_NAME := rancher
RANCHER_URL 	    := https://rancher.secretpool.org/

# Default to staging env
ifeq ($(env),)
	env = staging
endif

# staging configuration
ifeq ($(env), staging)
	RANCHER_ACCESS_KEY  := 586FDC65AFECD717FDAA
	RANCHER_SECRET_KEY  := QBrcvFCdWkLsQ5UsM7tL7PrE5qsC99j33xrYoRct
endif

# production configuration
ifeq ($(env), production)
	RANCHER_ACCESS_KEY  := 3BA7530964E964D41964
	RANCHER_SECRET_KEY  := ydxFG1NaoNU3qZHCrSVLtBCDt92XjJBK8fGB36xt
endif

# Make sure variables are exported correctly
export RANCHER_URL 	      := $(RANCHER_URL)
export RANCHER_ACCESS_KEY := $(RANCHER_ACCESS_KEY)
export RANCHER_SECRET_KEY := $(RANCHER_SECRET_KEY)

all: deploy

login:
	docker login r.secretpool.org

build:
	docker build .
	docker tag gearbot:latest r.secretpool.org/admin/gearbot:latest
	docker push r.secretpool.org/admin/gearbot:latest

run: build
	kubectl run gearbot --image=r.secretpool.org/admin/gearbot:latest

deploy: build
	kubectl set image deployment/gearbot gearbot=r.secretpool.org/admin/gearbot:latest

logs:
	kubectl logs deployment/gearbot -f
