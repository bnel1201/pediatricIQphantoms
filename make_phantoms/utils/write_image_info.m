function status = write_image_info(fname, ii)
    fid = fopen(fname, 'w');
    fprintf(fid, 'HU_offset, %2.4g\r\n', ii.offset);
    status = fclose(fid);
end
