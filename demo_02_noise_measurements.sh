IMAGE_DIR=results/test/CCT189

python evaluation/denoise.py ${IMAGE_DIR}

python evaluation/evaluate_noise.py results/test/CCT189/ -o dose_size_dependence.png