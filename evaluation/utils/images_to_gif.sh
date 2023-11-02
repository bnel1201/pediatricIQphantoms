inputs=${1-'results/MTF/images/diameter*mm_image_comparison.png'}
output_file=${2-'results/esf_comparison.gif'}


/usr/bin/ffmpeg -f image2 \
                -pattern_type glob \
                -framerate 0.7 \
                -hide_banner \
                -y -i "$inputs" \
                -vf "scale=1000:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
                 $output_file
