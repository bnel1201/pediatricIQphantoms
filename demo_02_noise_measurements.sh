EXPERIMENT=experiments/test

# Do Not Edit Below
source $EXPERIMENT/protocol
mkdir -p $RESULTS_DIR
cd $(dirname $0)
orginal_dir=$(pwd)

# NPS
bash evaluation/NPS/_1_run_NPS_analysis.sh $BASE_DIR

bash evaluation/NPS/_2_generate_NPS_plots.sh $BASE_DIR/CCT189/monochromatic/ $RESULTS_DIR/NPS
