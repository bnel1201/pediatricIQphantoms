%NPS measures from catphan scans
% clear all;
addpath('utils')
datadir = fullfile(basedir, 'CCT189/fbp')
outfolder = resultsdir;
if ~exist(outfolder, 'dir')
    mkdir(outfolder)
end
%%Data inputs
all_recon_type = {'fbp'};

run('utils/eval_CCT189_NPS.m')

% exit