# datadir=${1-'/home/brandon.nelson/Data/temp/CTP404/monochromatic'}
datadir=${1-'/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic'}
results_dir=${2-'../../results/MTF'}

orginal_dir=$(pwd)
cd $(dirname $0)
## plot ESF cirves
plots_dir=$results_dir/plots

output_fname=$plots_dir/esf_curve_comparison.png
python plot_esf_curves.py -d $datadir -o $output_fname
## plot MTF curves

# plot fbp baseline mtf
output_fname=$plots_dir/fbp_mtf_baseline.png
python plot_mtf_curves.py -d $datadir -o $output_fname

# plot redcnn mtf
output_fname=$plots_dir/mtf_redcnn.png
python plot_mtf_curves.py -d $datadir -o $output_fname --processed

## plot MTF cutoff values
output_fname=$plots_dir/mtf_cutoff_vals_baseline.png
python plot_mtf_cutoffs.py -d $datadir -o $output_fname

output_fname=$plots_dir/mtf_cutoff_vals_processed.png
python plot_mtf_cutoffs.py -d $datadir -o $output_fname --processed

output_fname=$plots_dir/mtf_cutoff_vals_rel.png
python plot_mtf_cutoffs_compare.py -d $datadir -o $output_fname --contrasts "15 35 120 200 340 990 1000"

python plot_sharpness_v_contrast_heatmap.py -d $results_dir
# plot images
images_dir=$results_dir/images
python plot_images.py -d $datadir -o $images_dir
bash ../utils/images_to_gif.sh $images_dir'/diameter*mm_image_comparison.png' $results_dir'/esf_comparison.gif'
cd $orginal_dir
