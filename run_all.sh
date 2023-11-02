EXPERIMENT=${1-./experiments/main}

# load experiment parameters
EXPERIMENT=$(realpath $EXPERIMENT)
source $EXPERIMENT/protocol
# make phantoms
bash make_phantoms/run_make_phantoms.sh ${BASE_DIR} ${EXPERIMENT}
