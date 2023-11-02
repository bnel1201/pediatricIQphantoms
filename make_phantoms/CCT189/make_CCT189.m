% make_CCT189.m
% Author: Brandon Nelson, Rongping Zeng
% date: August 1, 2022

% Purpose: To simulate the MITA LCD body phantom CCT189 and a uniform phantom. This generates 
% multiple noise realization for a range of noise levels, specified by
% 'I0_vector'.
%
% Derived from </home/rxz4/ct_deeplearning/make_phantom/make_CCT189_wD45_B30.m>
% which was written by Sarah Divel & Rongping Zeng
% Date: July 23, 2018

% Run path setup
run('../configs/SiemensSomatomDefinitionAS.m')

run('../utils/setup.m') % need to double check that this isn't overwriting anything from the base config

sg = sino_geom('fan', 'units', 'mm', ...
    'nb', nb, 'na', na, 'ds', ds, ...
    'dsd', sdd, 'dod', dod, 'offset_s', offset_s, ...
    'down', down);

sampleFolder = fullfile(basedataFolder, 'geometric', 'CCT189/')
if ~exist(sampleFolder, 'dir')
    mkdir(sampleFolder)
end
physics_type_folder = [sampleFolder 'monochromatic/'];
if ~exist(physics_type_folder, 'dir')
    mkdir(physics_type_folder)
end

mu_water = 0.2059 / 10;     % in mm-1
if ~exist('reference_diameter', 'var')
    reference_diameter = 200; % in mm, from /home/rxz4/ct_deeplearning/make_phantom/make_CCT189_wD45_B30.m line 81
end
if ~any(patient_diameters == reference_diameter)
    patient_diameters = [reference_diameter patient_diameters]
end
if ~exist('reference_fov', 'var')
    reference_fov = 340
end

aec_factors = exp(mu_water*patient_diameters)./exp(mu_water*reference_diameter);
ndiams = length(patient_diameters); 
for diam_idx=1:ndiams
    patient_diameter = patient_diameters(diam_idx);

    if patient_diameter == reference_diameter
        fov = reference_fov;
        % patient_folder = [physics_type_folder '/reference_diameter' num2str(patient_diameter) 'mm/']
    else
        fov = 1.1*patient_diameter;
    end
    patient_folder = [physics_type_folder '/diameter' num2str(patient_diameter) 'mm/']
    aec_factor = aec_factors(diam_idx);

    ig = image_geom('nx', nx, 'fov', fov, 'down', down);

    if ~exist(patient_folder, 'dir')
        mkdir(patient_folder)
    end

    close all;
    sg.plot(ig)
    hold off; titlef('Scanner FOV = %g mm, Recon FOV = %g mm', round(2*sg.rfov), round(fov)); hold on;
    saveas(gca, fullfile(patient_folder, 'image_geometry.png'))

    for I0=I0_vector
        I0_string = ['I0_' sprintf('%07d', I0)];

        files_disk = [patient_folder I0_string '/disk/'];
        if(~exist(files_disk,'dir'))
            mkdir(files_disk);
        end
        files_bkg = [patient_folder I0_string '/bkg/'];
        if(~exist(files_bkg,'dir'))
            mkdir(files_bkg);
        end

        % relative_lesion_diameter = 0.01335; <-- TODO add switch for this in config file
        relative_lesion_diameter = false;
        relative_lesion_location = 0.4;
        disk_ell = CCT189(patient_diameter, mu_water, relative_lesion_diameter);
        disk_true = ellipse_im(ig, disk_ell, 'oversample', 4, 'rot', 0);
        disk_true_hu = 1000*(disk_true - mu_water)/mu_water + offset;

        bkg_ell = disk_ell(1, :);
        bkg_true = ellipse_im(ig, bkg_ell, 'oversample', 4, 'rot', 0);
        bkg_true_hu = 1000*(bkg_true - mu_water)/mu_water + offset;

        filename = [patient_folder  '/' 'true_disk.raw'];
        write_phantom_info([patient_folder filesep 'phantom_info_mm.csv'], disk_ell);
        write_phantom_info([patient_folder filesep 'phantom_info_pix_idx.csv'], ellipse_mm_to_pix(disk_ell, fov, nx));
        ii.offset = offset;
        write_image_info([patient_folder filesep 'image_info.csv'], ii);
        write_geometry_info([patient_folder filesep 'geometry_info.csv'], ig);
    
        my_write_rawfile(filename, disk_true_hu, 'int16');
        filename = [patient_folder  '/' 'true_bkg.raw'];
        my_write_rawfile(filename, bkg_true_hu, 'int16');

        disk_sino = ellipse_sino(sg, disk_ell, 'oversample', 4);
        bkg_sino = ellipse_sino(sg, bkg_ell, 'oversample', 4);

        % FBP reconstruction operator
        fg = fbp2(sg, ig,'type','std:mat'); %choose 'std:mat' to be able to using different recon filter
                                            %default would be 'std:mex' but only ramp filter was implemented in it
        if aec_on
            I0 = aec_factor*I0; %accounts for different patient size
        end

        if has_bowtie
            I0_afterbowtie=apply_bowtie_filter(I0, sg, mu_water, patient_diameter);           
        else
            I0_afterbowtie=I0;            
        end

        disk_proj_noisefree = I0_afterbowtie .* exp(-disk_sino);
        bkg_proj_noisefree = I0_afterbowtie .* exp(-bkg_sino);

        for sim_idx = batch
            total_idx = sim_idx+(diam_idx-1)*nsims;
            total_sim = ndiams*nsims;
            disp(sprintf('%s, diameter: %dmm (FOV: %dmm) [%d/%d], simulation: [%d/%d], Total: %3.2f%% [%d/%d]', mfilename, patient_diameter, round(fov), diam_idx, ndiams, sim_idx, nsims, total_idx/total_sim*100, total_idx, total_sim))
            if add_noise   
                disk_proj = poisson(disk_proj_noisefree); %This poisson generator respond to the seed number setby rand('sate',x');
                bkg_proj = poisson(bkg_proj_noisefree); %is it ok if these are different noise instances?
            else
                disk_proj = disk_proj_noisefree;
                bkg_proj = bkg_proj_noisefree;
            end

            disk_proj = replace_zeros(disk_proj);
            bkg_proj = replace_zeros(bkg_proj);

            disk_sino_log = -log(disk_proj ./ I0_afterbowtie);            % noisy fan-beam sinogram
            bkg_sino_log = -log(bkg_proj ./ I0_afterbowtie);            % noisy fan-beam sinogram

            disk_fbp = fbp2(disk_sino_log, fg, 'window', 'hann205');
            disk_fbp_hu = 1000*(disk_fbp - mu_water)/mu_water + offset;

            bkg_fbp = fbp2(bkg_sino_log, fg, 'window', 'hann205');
            bkg_fbp_hu = 1000*(bkg_fbp - mu_water)/mu_water + offset;

            file_prefix = [files_disk 'fbp_sharp_'];
            file_num = sim_idx;
            filename_disk_fbp = [file_prefix 'v' sprintf('%03d', file_num) '.raw'];
            my_write_rawfile(filename_disk_fbp, disk_fbp_hu, 'int16');

            file_prefix = [files_bkg 'fbp_sharp_'];
            file_num = sim_idx;
            filename_bkg_fbp = [file_prefix 'v' sprintf('%03d', file_num) '.raw'];
            my_write_rawfile(filename_bkg_fbp, bkg_fbp_hu, 'int16');
        end
    end
end
