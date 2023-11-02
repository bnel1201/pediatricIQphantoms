BASE_DIR=${1-/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/main/anthropomorphic/simulations/} #directory containing simulations
RESULTS_DIR=${2-/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/anthropomorphic}

mkdir -p $RESULTS_DIR
RESULTS_DIR=$(realpath $RESULTS_DIR)
results_csv_name=$RESULTS_DIR/anthro_mse_dataset.csv #csv to be generated containing mean squared error measurements

cd $(dirname $0)
orginal_dir=$(pwd)

patient_info_csv=$(realpath ../../make_phantoms/anthropomorphic/selected_xcat_patients.csv) #selected_xcat_patients.csv #from XCAT

# generate results csv file
python measure_anthro_mse.py $BASE_DIR $patient_info_csv -o $results_csv_name

# plot results
python plot_anthro_mse.py $results_csv_name -o $RESULTS_DIR

cd $orginal_dir
