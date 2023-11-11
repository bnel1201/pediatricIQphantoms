EXPERIMENT=experiments/test

# Do Not Edit Below
source $EXPERIMENT/protocol
mkdir -p $RESULTS_DIR

# NPS
bash evaluation/NPS/_1_run_NPS_analysis.sh $EXPERIMENT

bash evaluation/NPS/_2_generate_NPS_plots.sh $OUTPUT_DIR/CCT189/fbp/ $RESULTS_DIR/NPS
