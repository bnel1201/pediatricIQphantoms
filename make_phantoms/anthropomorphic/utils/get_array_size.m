function [array_size] = get_array_size(patient_filename)
    [phantom_dir, patient, ~] = fileparts(patient_filename);
    text = fileread(fullfile(phantom_dir,[erase(patient, 'atn_1') 'log']));
    res = regexp(text, '(array_size =\s+)(\d.\d+)', 'match');
    array_size = str2double(erase(res{1}, 'array_size = '));
end