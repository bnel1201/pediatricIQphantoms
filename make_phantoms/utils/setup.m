% A set of defaults for quick testing, to specify user defined variables define them BEFORE calling this script or AFTER
addpath(fileparts(mfilename('fullpath')))
addpath('/home/brandon.nelson/Dev/PhantomSimulations/CT_simulator')
if exist('homedir', 'var') == false %checks if setpath has been run
    setpath
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