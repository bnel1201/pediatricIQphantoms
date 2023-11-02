%% plotting examples

global ninserts ndoses nobservers res_table insert_HUs ...
       observers patient_diameters dose_levels recons

results_dir = "results_main";
res_table = readtable(fullfile(results_dir,'LCD_results.csv')); %optional to reload results from file
observers = unique(res_table.observer);
patient_diameters = unique(res_table.patient_diameter_mm);
dose_levels = unique(res_table.dose_level_pct);
insert_HUs = unique(res_table.insert_HU);
recons = unique(res_table.recon);

ninserts = length(insert_HUs);
ndoses = length(dose_levels);
nobservers = length(observers);

patient_diameters
%% adults
patient_diameter = patient_diameters(6)
recon = 'fbp';
res_type = 'snr';
f1 = figure(1);
f1.Position = [0 1600 800 800];
plot_results_vs_dose(res_type, recon, patient_diameter)
sgtitle(sprintf("FBP %d mm patient diameter", patient_diameter));

recon = 'dl_REDCNN';
f2 = figure(2);
f2.Position = [800 1600 800 800];
plot_results_vs_dose(res_type, recon, patient_diameter)
sgtitle(sprintf("DLIR %d mm patient diameter", patient_diameter));

f3 = figure(3);
f3.Position = [1600 1600 800 800];
plot_results_vs_dose(res_type, ["fbp", "dl_REDCNN"], patient_diameter);
sgtitle(sprintf("DLIR AUC - FBP AUC %d mm patient diameter", patient_diameter));

%% peds
patient_diameter = patient_diameters(1)
recon = 'fbp';
f4 = figure(4);
f4.Position = [0 300 800 800];
plot_results_vs_dose(res_type, recon, patient_diameter)
sgtitle(sprintf("FBP %d mm patient diameter", patient_diameter));

recon = 'dl_REDCNN';
f5 = figure(5);
f5.Position = [800 300 800 800];
plot_results_vs_dose(res_type, recon, patient_diameter)
sgtitle(sprintf("DLIR %d mm patient diameter", patient_diameter));

f6 = figure(6);
f6.Position = [1600 300 800 800];
plot_results_vs_dose(res_type, ["fbp", "dl_REDCNN"], patient_diameter);
sgtitle(sprintf("DLIR AUC - FBP AUC %d mm patient diameter", patient_diameter));

%% everything
res_types = ["auc", "snr"];

for r = 1:length(res_types)
    for d = 1:length(patient_diameters)
        res_type = res_types(r);
        output_dir = fullfile(results_dir, res_type);
        if ~exist(output_dir, 'dir')
           mkdir(output_dir) 
        end
        patient_diameter = patient_diameters(d);
        recon = 'fbp';
        f4 = figure(4);
        f4.Position = [0 300 800 800];
        plot_results_vs_dose(res_type, recon, patient_diameter)
        sgtitle(sprintf("FBP %d mm patient diameter", patient_diameter));
        saveas(f4, fullfile(output_dir, sprintf("%s_%dmm_%s.png", recon, patient_diameter, res_type)));

        recon = 'dl_REDCNN';
        f5 = figure(5);
        f5.Position = [800 300 800 800];
        plot_results_vs_dose(res_type, recon, patient_diameter)
        sgtitle(sprintf("DLIR %d mm patient diameter", patient_diameter));
        saveas(f5, fullfile(output_dir, sprintf("%s_%dmm_%s.png", recon, patient_diameter, res_type)));

        f6 = figure(6);
        f6.Position = [1600 300 800 800];
        plot_results_vs_dose(res_type, ["fbp", "dl_REDCNN"], patient_diameter);
        sgtitle(sprintf("DLIR AUC - FBP AUC %d mm patient diameter", patient_diameter));
        saveas(f6, fullfile(output_dir,sprintf("%s_%dmm_%s.png", "delta", patient_diameter, res_type)));
    end
end

function insert_size = get_insert_size(insert_HU)
    switch insert_HU
        case 3
            insert_size = "10 mm";
        case 5
            insert_size = "7 mm";
        case 7
            insert_size = "5 mm";
        case 14
            insert_size = "3 mm";
        otherwise
            insert_size = "";
    end
end

function [means, stds] = get_res_mean_std(res, recon, patient_diameter, insert_idx)
    global nobservers ndoses insert_HUs res_table observers dose_levels
    means = zeros(ndoses, nobservers);
    stds = zeros(ndoses, nobservers);
    insert_HU = insert_HUs(insert_idx);
    for obsv_idx = 1:nobservers
        for dose_idx = 1:ndoses
            table_filter = res_table.insert_HU == insert_HU & ...
                           string(res_table.observer) == string(observers(obsv_idx)) & ...
                           res_table.dose_level_pct == dose_levels(dose_idx) & ...
                           res_table.recon == string(recon) & ...
                           res_table.patient_diameter_mm == patient_diameter;
                       
            if strcmpi(res, "auc")
                means(dose_idx, obsv_idx) = mean(res_table.auc(table_filter));
                stds(dose_idx, obsv_idx) = std(res_table.auc(table_filter));
            elseif strcmpi(res, "snr")
                means(dose_idx, obsv_idx) = mean(res_table.snr(table_filter));
                stds(dose_idx, obsv_idx) = std(res_table.snr(table_filter));
            end
        end
    end
end

function plot_results_vs_dose(res_type, recon, patient_diameter)
    global ninserts dose_levels nobservers insert_HUs observers
    recon = string(recon);
    for inst_idx = 1:ninserts
        
        if length(recon) > 1
            [means1, stds1] = get_res_mean_std(res_type, recon(1), patient_diameter, inst_idx);
            [means2, stds2] = get_res_mean_std(res_type, recon(2), patient_diameter, inst_idx);
            means = means2 - means1;
            stds = sqrt(stds2.^2 + stds1.^2);
        else
            [means, stds] = get_res_mean_std(res_type, recon, patient_diameter, inst_idx);
        end
        subplot(2,2,inst_idx);
        errorbar(repmat(dose_levels, [1 nobservers]), means, stds)
        
        insert_HU = insert_HUs(inst_idx);
        insert_size = get_insert_size(insert_HU);
        title(sprintf('%s, %d HU insert', insert_size, insert_HU))
        ylabel_str = "";
        if length(recon) > 1
            ylabel_str = ylabel_str + "\Delta";
            if  strcmpi(res_type, "auc")
                ylim([-0.5 0.5]);
            end
        else
            if strcmpi(res_type, "auc")
                ylim([0.4 1.1]);
            end
        end

        ylabel_str = ylabel_str + string(res_type);
        ylabel(ylabel_str)
        xlabel('dose level %')
        if inst_idx == 1
            legend(observers)
        end
    end
end

