% Config file for Siemens Definition/Sensation
%  Values from in mm from Zeng R, Lin CY, Li Q, et al. Performance of a deep learning-based CT image denoising method: Generalizability over dose, reconstruction kernel, and slice thickness. Medical Physics. 2022;49(2):836-853. doi:10.1002/mp.15430
sid = 595;          % source-to-isocenter distance (value based on AAPM data dicom header)
sdd = 1085.6;          % source-to-detector distance
dod = sdd - sid;    % isocenter-to-detector distance

nb = 900;           % number of detector columns (Value based on ZengEtAl2015-IEEE-NuclearScience-v6n5)
na = 580; %from 580 % number of views in a roatation

ds = 1;        % detector column size 
offset_s = 1.25;    % lateral shift of detector
fov = 380; % 
nx = 256; %matrix size
down = 1;
has_bowtie = 0;