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

# S3 Scoped -- but doesn't work?
# export AWS_ACCCESS_KEY_ID 	 := AKIAJLG5ZJO5CRH5KWXA
# export AWS_SECRET_ACCESS_KEY := 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

# TODO: Stop using zeekay id/key
aws_key_id = AKIAIBAJS4WNLLKDY3ZA
aws_secret = 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
aws_region = us-west-2

all: run

run:
	AWS_DEFAULT_REGION=$(aws_region) \
	AWS_ACCCESS_KEY_ID=$(aws_key_id) \
	AWS_SECRET_ACCESS_KEY=$(aws_secret) \
	RANCHER_CLIENT_DEBUG=true \
	rancher-compose --debug up

logs:
	docker logs pkr-api -f
