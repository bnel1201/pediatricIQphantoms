
% Purpose: calculate MTf and accuracy from CTP404 Sensitometry scans
% Brandon J. Nelson
% Note (2023-03-08):
% a lot of this is repeat boiler plate code as NPSand LCD evaluation
% (mostly looping through all the different combinations of phantom size,
% dose, and recon type and could be refactored such that there is only one
% file with all this looping and a different analysis function and dataset
% are inserted for each
addpath('/home/brandon.nelson/Dev/PhantomSimulations/CT_simulator')
if ~exist('homedir', 'var') %checks if setpath has been run
    setpath
end
if ~exist('folder_path', 'var')
    folder_path = '/home/brandon.nelson/Data/temp/CTP404/monochromatic/diameter112mm/I0_3000000/fbp_sharp/';
end

addpath([dirname(fileparts(mfilename('fullpath')), 2) '/utils'])

datadir = fullfile(basedir, 'CTP404/monochromatic/');
dose_level = 'I0_3000000_processed';
kernel = 'fbp_sharp';
dir_contents = dir(datadir);
diams = dir_contents(3:end);

filenames = [];
phantom_diameter_mm = [];
fov_size_mm =[];
pixel_size_mm = [];
recon = [];
dose_photons = [];
expected_HU = [];
measured_HU = [];
MTF50 = [];
MTF25 = [];
MTF15 = [];
MTF10 = [];

fnames_MTF50_id = fopen(fullfile(resultsdir, 'results_MTF50.csv'), 'w');
fnames_MTF10_id = fopen(fullfile(resultsdir, 'results_MTF10.csv'), 'w');

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
            folder_path = fullfile(dose_dir, 'fbp_sharp'); % add another loop here if using different kernels (other than dlir v not dlir)
            outfolder = resultsdir;
            phantom_info = read_phantom_info([diameter_dir '/phantom_info_pix_idx.csv']);
            ig = read_geometry_info([diameter_dir '/geometry_info.csv']);
            loc = phantom_info(2:end-1, 1:2);

            ii = importdata([diameter_dir '/image_info.csv']);
            offset = ii.data;
            img_sz = ig.nx;
            fileinfo = dir(folder_path);
            nfile = length(fileinfo)-2;

            find_disk_loc = 0;

            %display a image to assist a manual localization of the disk area.
            if(find_disk_loc==1)
                file1 = [folder_path fileinfo(3).name]
                loc = gget_loc(file1, img_sz)
            end

            disk_radius = phantom_info(2, 3); %first and last disks are special, all middle disks are the measured inserts
            water_atten = phantom_info(1, 6);
            disk_HUs = sort(1000*(phantom_info(2:9,6))/water_atten);
            roisz = ceil(disk_radius*2*1.6);
            roi = round([-roisz/2:roisz/2]);
            pixelsz = ig.dx;

            fprintf(fnames_MTF50_id, '%s', 'filenames');
            for hu_idx = 1:length(disk_HUs)
                fprintf(fnames_MTF50_id, ', %d HU', disk_HUs(hu_idx));
            end

            fprintf(fnames_MTF10_id, '%s', 'filenames');
            for hu_idx = 1:length(disk_HUs)
                fprintf(fnames_MTF10_id, ', %d HU', disk_HUs(hu_idx));
            end

            for i=1:nfile
                disp(['Simulation [' num2str(i) '/' num2str(nfile) ']'])
                filename = fileinfo(i+2).name;
                filepath = fullfile(folder_path, filename);
                fid = fopen(filepath);
                img = fread(fid,[img_sz img_sz], 'int16') - offset;
                fclose(fid);

                fprintf(fnames_MTF50_id, '\r\n%s', filename);
                fprintf(fnames_MTF10_id, '\r\n%s', filename);

                mtf_fid = fopen([dirname(folder_path, 2) filesep filename(1:end-4) '_mtf.csv'], 'w');
                esf_fid = fopen([dirname(folder_path, 2) filesep filename(1:end-4) '_esf.csv'], 'w');

                fprintf(mtf_fid, 'frequencies [1/mm]');
                fprintf(mtf_fid, ', %d HU', round(disk_HUs));
                fprintf(esf_fid, 'distance [mm]');
                fprintf(esf_fid, ', %d HU', round(disk_HUs));

                for j=1:length(loc)
                    %Crop the disk ROI
                    disk_img = double(img(loc(j,1)+roi, loc(j,2)+roi)); %change from unit16 to double
                    expected = round(disk_HUs(j));
                    measured = round(mean(mean(disk_img(floor(disk_radius):end-floor(disk_radius), floor(disk_radius):end-floor(disk_radius)))));
                    disp(['     ' num2str(expected) ' HU disk (actual: ' num2str(measured) ' HU) [' num2str(j) '/' num2str(length(disk_HUs)) ']'])
                    if abs(measured - expected) > 10 %error threshold in HU
                        disp(sprintf('Warning: Measured Disk HUs (%d HU) do not match expected (%d HU)', measured, expected))
                    end
                    %estimate the MTF
                    try
                    [mtf, freq, esf] = MTF_from_disk_edge(disk_img);
                    catch
                       warning('Dose too low to calc MTF assigning 0')
                       mtf = 0;
                       freq = 0;
                       esf = 0;
                    end
                    if isnan(mtf) | length(mtf) < (length(esf)/2 - 10)
                        mtf = 0;
                        esf = 0;
                    end
                    
                    freq_vector = freq/pixelsz;
                    dist_vector = ig.dx*(0:length(esf)-1);

                    if j == 1
                        clear mtf_data esf_data
                        mtf_data(1, :) = freq_vector;
                        esf_data(1, :) = dist_vector;
                    end
                    if (length(mtf) ~= length(mtf_data) | length(freq_vector) ~= length(mtf_data)) & (mtf ~= 0)
                        mtf_data(j + 1, :) = interp1(freq_vector, mtf, mtf_data(1, :)); % <-- double check this later... meant to account for slight differences in array length from MTF_from_disk_edge due to rounding errors
                        esf_data(j + 1, :) = interp1(dist_vector, esf, esf_data(1, :));
                    else
                        mtf_data(j + 1, :) = mtf;
                        esf_data(j + 1, :) = esf;
                    end
                    

                    %Estimate the mtf50% and mtf10% values
                    if mtf
                    mtf50_all(i, j) = MTF_width(mtf, 0.5, freq_vector);
                    mtf10_all(i, j) = MTF_width(mtf, 0.1, freq_vector);
                    else
                    mtf50_all(i, j) = 0;
                    mtf10_all(i, j) = 0;
                    end
                    
                    expected_HU = [expected_HU; expected];
                    measured_HU = [measured_HU; measured];
                    
                    filenames = [filenames; string(filepath)];
                    phantom_diameter_mm = [phantom_diameter_mm; diameter];
                    fov_size_mm =[fov_size_mm; ig.data.fov];
                    pixel_size_mm = [pixel_size_mm; pixelsz];
                    recon = [recon; string(recon_type)];
                    dose_photons = [dose_photons; dose_level];
     
                    if mtf | isnan(mtf)
                        MTF50 = [MTF50; MTF_width(mtf, 0.5, freq_vector)];
                        MTF25 = [MTF25; MTF_width(mtf, 0.25, freq_vector)];
                        MTF15 = [MTF15; MTF_width(mtf, 0.15, freq_vector)];
                        MTF10 = [MTF10; MTF_width(mtf, 0.1, freq_vector)];
                    else
                        MTF50 = [MTF50; 0];
                        MTF25 = [MTF25; 0];
                        MTF15 = [MTF15; 0];
                        MTF10 = [MTF10; 0];
                    end

                    fprintf(fnames_MTF50_id, ', %3.5g', [mtf50_all(i, j)]);
                    fprintf(fnames_MTF10_id, ', %3.5g', [mtf10_all(i, j)]);
                end
                fprintf(mtf_fid, ['\r\n%3.5g' repmat(', %3.5g', 1, length(disk_HUs))], mtf_data);
                fclose(mtf_fid);

                fprintf(esf_fid, ['\r\n%3.5g' repmat(', %3.5g', 1, length(disk_HUs))], esf_data);
                fclose(esf_fid);

            end
        end
    end
end
fclose(fnames_MTF50_id);
fclose(fnames_MTF10_id);

dose_level_pct = round(100*dose_photons ./ max(dose_photons));
res_table = table(recon, phantom_diameter_mm, fov_size_mm,...
                  pixel_size_mm, dose_photons, dose_level_pct,...
                  expected_HU, measured_HU, MTF50, MTF25, MTF15, MTF10)
results_fname = fullfile(outfolder, 'MTF_results.csv')
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
