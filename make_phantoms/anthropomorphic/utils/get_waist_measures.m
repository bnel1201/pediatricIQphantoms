function [short_axis, long_axis] = get_waist_measures(patient_filename)
    [phantom_dir, patient, ~] = fileparts(patient_filename);
    text = fileread(fullfile(phantom_dir,[erase(patient, 'atn_1') 'log']));
    waist_line = regexp(text, 'Waist\n  Short axis \(AP\)\s+\d+.\d+ mm\n  Long axis \(LAT\)\s+\d+.\d+ mm', 'match');
    res = regexp(waist_line{1}, '\d+.\d+', 'match');
    short_axis = str2double(res{1});
    long_axis = str2double(res{2});
end