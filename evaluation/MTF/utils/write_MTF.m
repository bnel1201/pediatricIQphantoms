function [status] = write_MTF(filename, freq, mtf)
    fid = fopen(filename, 'w');
    fprintf(fid, 'frequencies [1/mm], MTF\r\n');
    formatSpec = '%3.5g, %3.5g \r\n';
    fprintf(fid, formatSpec, [freq; mtf]);
    status = fclose(fid);
end