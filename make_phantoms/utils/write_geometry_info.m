function status = write_geometry_info(fname, ig)
    fid = fopen(fname, 'w');
    fprintf(fid, 'nx, %d\r\n', ig.nx);
    fprintf(fid, 'ny, %d\r\n', ig.ny);
    fprintf(fid, 'dx, %2.4g\r\n', ig.dx);
    fprintf(fid, 'dy, %2.4g\r\n', ig.dy);
    fprintf(fid, 'offset_x, %2.4g\r\n', ig.offset_x);
    fprintf(fid, 'offset_y, %2.4g\r\n', ig.offset_y);
    fprintf(fid, 'offsets, %2.4g\r\n', ig.offsets);
    fprintf(fid, 'fov, %2.4g\r\n', ig.fov);
    fprintf(fid, 'down, %2.4g\r\n', ig.down);
    status = fclose(fid);
end