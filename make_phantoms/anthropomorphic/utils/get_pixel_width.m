function [pixel_width_mm] = get_pixel_width(patient_filename)
    [phantom_dir, patient, ~] = fileparts(patient_filename);
    text = fileread(fullfile(phantom_dir,[erase(patient, 'atn_1') 'log']));
    res = regexp(text, '(pixel width =  )(\d.\d+)', 'match');
    pixel_width_mm = str2double(erase(res{1}, 'pixel width =  '))*10;
end