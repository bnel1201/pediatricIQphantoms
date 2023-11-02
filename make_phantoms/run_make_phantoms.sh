BASE_DIR=$1
EXPERIMENT=$2

orginal_dir=$(pwd)
cd $(dirname $0)

cmd="bash make_phantoms.sh ${BASE_DIR} ${EXPERIMENT}"
if [ $(hostname) == openhpc ]; then
    bash ../ssh_node.sh "$cmd; exit"
else
    $cmd
fi

cd $orginal_dir