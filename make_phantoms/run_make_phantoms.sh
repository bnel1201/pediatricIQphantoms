BASE_DIR=$1
EXPERIMENT=$2

orginal_dir=$(pwd)
cd $(dirname $0)

bash make_phantoms.sh $(realpath $BASE_DIR) $(realpath $EXPERIMENT) #get ride of base dir, just want one config file
