orginal_dir=$(pwd)
cd $(dirname $0)

base_datadir=/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic

mkdir -p geometries

for patient_dir in $(ls $base_datadir)
do
    cp $base_datadir/$patient_dir/image_geometry.png geometries/"${patient_dir}_image_geometry.png"
done

inputs='geometries/diameter*mm_image_geometry.png'
output_file='image_geometry_comparison.gif'
/usr/bin/ffmpeg -f image2 \
                -pattern_type glob \
                -framerate 0.7 \
                -hide_banner \
                -y -i "$inputs" \
                -vf "scale=1000:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
                 $output_file

cd $orginal_dir