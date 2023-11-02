# datadir=${1-'/home/brandon.nelson/Data/temp/CCT189/monochromatic'}
datadir=${1-'/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/main/geometric/CCT189/monochromatic/'}
results_dir=${2-'../../results/NPS'}

orginal_dir=$(pwd)
cd $(dirname $0)


# plot NPS curves
python plot_NPS_curves.py -d $datadir -o $results_dir

# plot images
images_dir=$results_dir/images
python plot_2D_nps_images.py -d $datadir -o $images_dir

bash ../utils/images_to_gif.sh $images_dir'/diameter*mm_noise_comparison.png' $results_dir'/nps_comparison.gif'
cd $orginal_dir