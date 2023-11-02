function [water_lin_attten_pixel] = get_water_atten_per_pix(patient_filename)
    [phantom_dir, patient, ~] = fileparts(patient_filename);
    text = fileread(fullfile(phantom_dir,[erase(patient, 'atn_1') 'log']));
    pattern_base = '(Linear Attenuation Coefficients \(1\/pixel\):\n   Body \(water\)   =';
    pattern = [pattern_base '\s+)(\d.\d+)'];
    res = regexp(text, pattern, 'match');
    res = regexp(res{1}, '\d.\d+', 'match');
    water_lin_attten_pixel = str2double(res{1});
end