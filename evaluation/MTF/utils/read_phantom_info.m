function [ell] = read_phantom_info(filename)
    %x center, y center, x radius, y radius, angle degree, mu [60 keV]
    out_struct = importdata(filename);
    ell = out_struct.data;
end