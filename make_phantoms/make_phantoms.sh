# convert this script to python so I can do toml or json files to get the config as one file
orginal_dir=$(pwd)
cd $(dirname $0)

experiment_dir=${1-../experiments/test}

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
    python ./anthropomorphic/make_anthro_phantom.py $OUTPUT_DIR $XCAT_PATIENTS_CSV
    fi
# octave -qf --eval 
    matlab -r "basedataFolder='${OUTPUT_DIR}';\
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