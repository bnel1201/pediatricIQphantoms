function [status] = write_phantom_info(filename, ell)
    fid = fopen(filename, 'w');
    fprintf(fid, 'x center, y center, x radius, y radius, angle degree, mu [60 keV] \r\n');
    formatSpec = '%3.5g, %3.5g, %3.5g, %3.5g, %3.5g, %3.5g \r\n';
    fprintf(fid, formatSpec, ell');
    status = fclose(fid);
end