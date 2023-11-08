EXPERIMENT=$1

orginal_dir=$(pwd)
cd $(dirname $0)

bash make_phantoms.sh $EXPERIMENT #just want one config file
