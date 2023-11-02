include experiments/main/protocol

.PHONY : results
results : 
	bash evaluation/run_all_evaluations.sh $(BASE_DIR) $(RESULTS_DIR)

.PHONY : phantoms
phantoms : $(BASEDIR)/diameter112mm/I0_3000000/fbp_sharp/fbp_sharp_v001.raw
	bash ssh_node.sh "cd make_phantoms; bash ./run_make_phantoms.sh; exit; cd .."

.PHONY : denoise
denoise :
	bash denoising/run_denoising.sh $(BASE_DIR) $(MODEL_FOLDER)

.PHONY : all
all : 
	bash run_all.sh experiments/main

# .PHONY : plots
# plots : $(MTF_RESULTS)/plots/fbp_mtf_baseline.png $(MTF_RESULTS)/plots/mtf_redcnn.png $(MTF_RESULTS)/plots/mtf_cutoff_vals.png $(MTF_RESULTS)/plots/mtf_cutoff_vals_processed.png

# # plot MTF curves
# $(MTF_RESULTS)/plots/fbp_mtf_baseline.png : $(BASEDIR)/diameter112mm/I0_3000000/fbp_sharp_v001_mtf.csv
# 	python evaluation/MTF/plot_mtf_curves.py $^ -o $@

# $(MTF_RESULTS)/plots/mtf_redcnn.png : $(BASEDIR)/diameter112mm/I0_3000000_processed/fbp_sharp_v001_mtf.csv
# 	python evaluation/MTF/plot_mtf_curves.py $^ -o $@ --processed

# # plot MTF cutoff values

# $(MTF_RESULTS)/plots/mtf_cutoff_vals.png : $(BASEDIR)/diameter112mm/I0_3000000/results_MTF50.csv
# 	python evaluation/MTF/plot_mtf_cutoffs.py $^ -o $@

# $(MTF_RESULTS)/plots/mtf_cutoff_vals_processed.png : $(BASEDIR)/diameter112mm/I0_3000000_processed/results_MTF50.csv
# 	python evaluation/MTF/plot_mtf_cutoffs.py $^ -o $@ --processed

.PHONY : clean_tests
clean_tests :
	rm -rf test/results
	rm -rf /gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/test/

.PHONY : tests
tests :
	rm -rf test/results
	bash run_all.sh experiments/test

.PHONY : clean
clean :
	rm -rf results