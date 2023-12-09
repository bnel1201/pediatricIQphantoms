function res = ct_sim(phantom, patient_diameter, reference_diameter, relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims)

    warning('off', 'all');
    if ~exist('mirt-main', 'dir')
        unzip('https://github.com/JeffFessler/mirt/archive/refs/heads/main.zip', '.');
    end
    run('mirt-main/setup.m')

    dod = sdd - sid;
    sg = sino_geom('fan', 'units', 'mm', ...
    'nb', nb, 'na', na, 'ds', ds, ...
    'dsd', sdd, 'dod', dod, 'offset_s', offset_s, ...
    'down', down);

    ig = image_geom('nx', nx, 'fov', fov, 'down', down);

    mu_water = 0.2059 / 10;     % in mm-1
    aec_factor = exp(mu_water*patient_diameter)./exp(mu_water*reference_diameter);

    % relative_lesion_diameter = 0.01335; <-- TODO add switch for this in config file
    % relative_lesion_location = 0.4;
    switch lower(phantom)
        case 'uniform'
            ellipse_obj = CCT189(patient_diameter, mu_water, relative_lesion_diameter);
            ellipse_obj = ellipse_obj(1, :);
        case 'cct189'
            ellipse_obj = CCT189(patient_diameter, mu_water, relative_lesion_diameter);
        case 'ctp404'
            relative_lesion_diameter = 0.08;
            relative_lesion_location = 0.38;
            ellipse_obj = CTP404(patient_diameter, mu_water, relative_lesion_diameter);
    end
    ground_truth = ellipse_im(ig, ellipse_obj, 'oversample', 4, 'rot', 0);
    ground_truth_hu = 1000*(ground_truth - mu_water)/mu_water;

    pathlength = ellipse_sino(sg, ellipse_obj, 'oversample', 4);
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

    noiseless_sinogram = I0_afterbowtie .* exp(-pathlength);

    ny = nx;
    vol = zeros(nsims, nx, ny);

    for sim_idx = 1:nsims
        disp(sprintf('%s, simulation: [%d/%d]', mfilename, sim_idx, nsims))
        if add_noise   
            disk_proj = poisson(noiseless_sinogram); %This poisson generator respond to the seed number setby rand('sate',x');
        else
            disk_proj = noiseless_sinogram;
        end
        disk_proj = replace_zeros(disk_proj);
        sinogram = -log(disk_proj ./ I0_afterbowtie);            % noisy fan-beam sinogram
        mu_image = fbp2(sinogram, fg, 'window', fbp_kernel);
        recon = 1000*(mu_image - mu_water)/mu_water;
        vol(sim_idx, :, :) = recon;
    end
    res.recon = vol;
    res.ground_truth = ground_truth_hu;
    res.sinogram_noiseless = noiseless_sinogram;
end