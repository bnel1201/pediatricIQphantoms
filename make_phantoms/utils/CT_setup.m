% A set of defaults for quick testing, to specify user defined variables define them BEFORE calling this script or AFTER
addpath(fileparts(mfilename('fullpath')))
%Download MIRT and include the MIRT path in the MATLAB workspace. 
if ~exist('mirt-main', 'dir')
    unzip('https://github.com/JeffFessler/mirt/archive/refs/heads/main.zip', '.');
end
irtdir = 'mirt-main';
addpath(irtdir)
if(exist('setup.m'))
    setup
end
    
% addpath('./configs')
if exist('reference_dose_level', 'var') == false
    reference_dose_level = 3e5
end
I0_vector = reference_dose_level; %[30 55 70 85 100]/100;

if exist('patient_diameters', 'var') == false
    patient_diameters = [112, 131, 151, 185, 216, 292]; %newborn, 8 yr-old, 18 year old
end

if exist('nsims', 'var') == false
    nsims = 2
end

if exist('aec_on', 'var') == false
    aec_on = true;
end

if exist('add_noise', 'var') == false
    add_noise = true;
end

if exist('offset', 'var') == false
    offset = 0
end

batch = 1:nsims;
rand('state', batch(end));
% Set save folder
if exist('basedataFolder', 'var') == false
    basedataFolder = '/home/brandon.nelson/Data/temp/'; %temporary until /gpfs_projects gets fixed then switch back to above^^^ 
end

% overwrite defaults with config file
if exist('image_matrix_size', 'var')
    nx = image_matrix_size;
end

if exist('nangles', 'var')
    na = nangles;
end

fbp_kernel = 'hanning,2.05'; % 'hanning,xxx', xxx = the cutoff frequency, see fbp2_window.m in MIRT for details.
                        %'hanning,2.05' approximate a sharp kernel D45 in Siemens Force.
                        %'hanning, 0.85' approximate a smooth kernel B30 in
                        %Siemens Force.