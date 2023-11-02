function loc = gget_loc(fname, img_sz)
    %graphical get loc function, give raw image file and select coordinates and return result
    fid = fopen(file1);
    img = fread(fid,[img_sz img_sz], 'int16');
    fclose(fid);
    imagesc(img',[-500 900]); daspect([1 1 1]); colormap(gray);
    disp 'Go to the figure and click the center of a disk for a ROI cropping.' 
    [xi, yi] = ginput(1);
    loc = [round(xi) round(yi)]
end