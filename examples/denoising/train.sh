save_path=$1
augment=$2
python main.py --data_path /gpfs_projects/brandon.nelson/Mayo_LDGC/images \
               --saved_path /gpfs_projects/brandon.nelson/Mayo_LDGC/numpy_files \
               --load_mode=1 \
               --save_path $save_path \
               --augment $augment