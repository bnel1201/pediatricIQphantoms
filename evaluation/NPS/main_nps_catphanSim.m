%NPS measures from catphan scans
% clear all;
addpath('utils')
if ~exist('basedir', 'var')
    disp('basedir not specified, using defaults')
    basedir = '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/main/geometric'; %see ../../make_phantoms/make_phantoms.m
end

datadir = fullfile(basedir, 'CCT189/monochromatic/')

if ~exist('resultsdir', 'var')
    disp('resultsdir not specified, using defaults')
    resultsdir = '/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/NPS'; %see ../../make_phantoms/make_phantoms.m
end

outfolder = resultsdir;
if ~exist(outfolder, 'dir')
    mkdir(outfolder)
end
%%Data inputs
all_recon_type = {'fbp','dl_REDCNN'};

run('utils/eval_CCT189_NPS.m')

% exit