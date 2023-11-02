
% Purpose: calculate NPS from water phantom scans

% clear all;
addpath('/home/brandon.nelson/Dev/PhantomSimulations/CT_simulator')
if ~exist('homedir', 'var') %checks if setpath has been run
    setpath
end
% addpath('utils')
addpath([dirname(fileparts(mfilename('fullpath')), 2) '/utils'])

% if ~exist('folder_path', 'var')
%     folder_path = '/home/brandon.nelson/Data/temp/CCT189/monochromatic/';
% end

dir_contents = dir(datadir);
diams = dir_contents(3:end);

filenames = [];
phantom_diameter_mm = [];
fov_size_mm =[];
pixel_size_mm = [];
recon = [];
dose_photons = [];
sample_mean = [];
sample_std = [];
nps_peak_cyc_per_pix = [];
nps_mean = [];
nps_std = [];
rmse = [];

for diam_idx = 1:length(diams)
    diameter_dir = fullfile(diams(diam_idx).folder, diams(diam_idx).name);
    diameter = get_diameter(diameter_dir);
    for recon_idx = 1:length(all_recon_type)
        recon_type = all_recon_type{recon_idx};
        if strcmpi(recon_type, 'fbp')
            dose_dirs = dir([diameter_dir, '/I0_*0']);
        else
            dose_dirs = dir([diameter_dir, '/I0_*0_processed']);
        end
        for dose_idx = 1:length(dose_dirs)
            dose_dir = fullfile(dose_dirs(dose_idx).folder, dose_dirs(dose_idx).name);
            dose_level = get_dose_level(dose_dirs(dose_idx).name);
        
            folder_path = fullfile(dose_dir, 'bkg');

            results_path = fullfile(outfolder, '2D NPS', num2str(diameter), recon_type); % <-- change this to the actual results paths
            if ~exist(results_path)
                mkdir(results_path)
            end

            fileinfo = dir(folder_path);
            nfile = length(fileinfo)-2;
            nsim = nfile;

            % image information
            parentfolder = dirname(folder_path, 2);

            ig = read_geometry_info([parentfolder '/geometry_info.csv']);
            nx = ig.nx;
            dx = ig.dx; %in mm
            fov = ig.fov; %in mm

            relative_roisize = 1/3;
            half_roisize = nx*relative_roisize/2;
            % half_roisize = 32;
            roi_xfov = nx/2+[-half_roisize:half_roisize-1];
            roi_yfov = roi_xfov;
            nx_roi = length(roi_xfov);
            
            fid = fopen(fullfile(parentfolder, 'true_bkg.raw'));
            xtrue = fread(fid, [nx nx], 'int16');
            fclose(fid);
            
            %Read in the repeatitive noisy scans
            img = zeros(nx,nx,nsim);

            for i=1:nsim
                filename = fileinfo(i+2).name;
                filepath = fullfile(folder_path, filename);
                fnames{i} = filepath;
                fid = fopen(filepath);
                img(:,:,i) = fread(fid,[nx nx], 'int16');
                fclose(fid);
            end

            % measure error image from ground truth to calculate root
            % mean square error (RMSE)
            error_image = img - xtrue;
            rmse = [rmse; squeeze(sqrt(mean(error_image.^2, [1 2])))];
            
            %extract noise only images
            img_mean = mean(img,3);
            noise_roi = zeros(nx_roi, nx_roi, nsim); 
            for i=1:nsim
                noise = img(:,:,i) - img_mean;
                noise_roi(:,:,i) =  noise(roi_xfov, roi_yfov);
            end

            noise_roi = noise_roi * sqrt(nsim/(nsim-1)); %Bias correction

            %Compute NPS
            nps = compute_nps(noise_roi);

            maxnps = max(nps(:));
            if(nps(half_roisize+1,half_roisize+1)==maxnps) 
               nps(half_roisize+1+[-1:1],half_roisize+1+[-1:1]) = 0;
            end

            %extract the 1D radial shape
            ang = [0:1:180];
            [cx, cy,c, mc] = radial_profiles_fulllength(nps, ang);
            nps1d = mc;
            fr = 1/2 *linspace(0, 1, (length(nps1d)));

            parts = regexp(parentfolder, '/', 'split');

            nps_raw_fname = fullfile(results_path, sprintf('%d_2D_nps_float32_%d.raw', dose_level, nx_roi));
            my_write_rawfile(nps_raw_fname, single(nps), 'single');
            %check mean HU variations in the set of images
            tiny_roi = round(nx/10/2);
            t=(img(nx/2+[-tiny_roi:tiny_roi],nx/2+[-tiny_roi:tiny_roi],:));
            diam = parts(end);
            tmean=mean(reshape(t, numel(t(:,:,1)), nsim));
            tstd=std(reshape(t, numel(t(:,:,1)), nsim));

            disp(sprintf('%s NPS evaluation. Center ROI summary of %d simulations', diam{:}, nsim))
            disp(sprintf('mean of means: %3.4f, std of means: %3.4f', mean(tmean), std(tmean)))
            disp(sprintf('mean of stds: %3.4f, std of stds: %3.4f', mean(tstd), std(tstd)))

            roi_stats_csv_fname = fullfile(results_path, 'roi_stats.csv');
            fid = fopen(roi_stats_csv_fname, 'w');
            fprintf(fid, '%s\r\n', 'filename, mean [HU], std [HU]');
            for i = 1:nsim
                fprintf(fid, '%s, %3.4f, %3.4f\r\n', fnames{i}, tmean(i), tstd(i));
            end
            fclose(fid);
            % nps_csv_fname = fullfile(results_path, 'nps_results.csv');
            nps_csv_fname = fullfile('nps_results.csv');

            Fs = 1/dx; %units of lp/mm
            dfr = Fs/(nx_roi-1);
            fr = dfr*(0:length(nps1d)-1);

            dfr_dft = 1/(nx_roi-1);
            fr_dft = dfr_dft*(0:length(nps1d)-1); %freq points in cyc/pix;

            [m, argmax] = max(nps1d);
            peak_freq = fr_dft(argmax);
            
            nps_1d_csv_fname = fullfile(results_path, '1D_nps.csv');
            fid = fopen(nps_1d_csv_fname, 'w');
            fprintf(fid, '%s\r\n', 'spatial frequency [cyc/pix], magnitude');
            fprintf(fid, '%3.4f, %3.4f\r\n', cat(1, fr_dft, nps1d));
            fclose(fid);
            disp('files written:')
            disp(sprintf('%s\r\n', nps_raw_fname, roi_stats_csv_fname, nps_1d_csv_fname))
            disp(repmat('-', 1, 20))
            
            for i = 1:nsim
                filenames = [filenames; string(fnames{i})];
                phantom_diameter_mm = [phantom_diameter_mm; diameter];
                fov_size_mm = [fov_size_mm; fov];
                pixel_size_mm = [pixel_size_mm; dx];
                recon = [recon; string(recon_type)];
                dose_photons = [dose_photons; dose_level];
                sample_mean = [sample_mean; tmean(i)];
                sample_std = [sample_std; tstd(i)];
                nps_peak_cyc_per_pix = [nps_peak_cyc_per_pix; peak_freq];
                nps_mean = [nps_mean; sum(nps1d/sum(nps1d).*fr_dft)];
                
            end
        end
    end
end

dose_level_pct = round(100*dose_photons ./ max(dose_photons));
res_table = table(recon, phantom_diameter_mm, fov_size_mm,...
                  pixel_size_mm, dose_photons, dose_level_pct,...
                  sample_mean, sample_std, nps_peak_cyc_per_pix,...
                  nps_mean, rmse)
results_fname = fullfile(outfolder, 'NPS_results.csv')
writetable(res_table, results_fname)
              
function dose_level = get_dose_level(dose_level_dir_name)
    temp = split(dose_level_dir_name, '_');
    dose_level = str2double(temp{2});
end

function diameter = get_diameter(diameter_dir_name)
    temp = split(diameter_dir_name, 'diameter');
    temp = split(temp{2}, 'mm');
    diameter = str2double(temp{1});
end