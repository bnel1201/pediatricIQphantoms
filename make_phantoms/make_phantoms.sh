orginal_dir=$(pwd)
cd $(dirname $0)

BASE_DIR=${1-/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/}
experiment_dir=${2-../experiments/main}

XCAT_PATIENTS_CSV=anthropomorphic/selected_xcat_patients.csv # <-- patients to be simulated

source $experiment_dir/protocol 
n_experiments=$(ls $experiment_dir/*.phantom | wc -l) 
sim_num=0
for sim in $experiment_dir/*.phantom
do
    echo $sim
    source $(realpath $sim)
    ((sim_num++))
    echo [$phantom] Simulation series $sim_num/$n_experiments

    if [ $phantom == anthropomorphic ]; then
    python ./anthropomorphic/make_anthro_phantom.py $BASE_DIR $XCAT_PATIENTS_CSV
    fi

    matlab -nodesktop -nodisplay -r "basedataFolder='${BASE_DIR}';\
                                     nsims=${nsims};\
                                     image_matrix_size=${image_matrix_size};\
                                     nangles=${nangles};\
                                     patient_diameters=${patient_diameters};\
                                     aec_on=${aec_on};\
                                     add_noise=${add_noise};\
                                     reference_dose_level=${reference_dose_level};\
                                     reference_diameter=${reference_diameter};\
                                     reference_fov=${reference_fov};\
                                     offset=${offset};\
                                     run('./${phantom}/make_${phantom}.m');\
                                     exit;"
done

cd $orginal_dir