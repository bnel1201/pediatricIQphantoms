function [status] = write_results(filename, mtf50s, mtf10s)
    fid = fopen(filename, 'w');
    fprintf(fid, '%s', '50% MTF, 10% MTF');
    formatSpec = '\r\n %3.5g, %3.5g';
    fprintf(fid, formatSpec, [mtf50s; mtf10s]);
    status = fclose(fid);
end