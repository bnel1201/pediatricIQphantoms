function writemha(fn,A,offset,spacing,type, savefmt)
%% writemha(fn,A,offset,spacing,type)
%% fn filename
%% A Volume
%% offset
%% spacing
%% type 'uchar','float', or 'short'
%% savefmt 'slice' or 'brick'
%% Adapted From https://pinggejiang.github.io/research/2016/11/08/mha_matlab/



if ~exist("offset", "var")
    offset = 0;
end

if ~exist("spacing", "var")
    spacing = repmat(1, [1 ndims(A)]);
end

if ~exist("type", "var")
    type = "short";
end

if ~exist("savefmt", "var")
    savefmt = "slice";
end

if ismatrix(A)
    savefmt = "brick";
end

Asz = size(A);

if strcmpi(savefmt, "slice")
    fn = write_slices(fn, A, type);
else
    write_volume(fn, A, type)
end

write_header(fn, Asz, offset, spacing, type)

end

%% This works for 3D (A stays the same), and 4D (shift left 1)
function fn_list = write_slices(fn, A, type)
    nslices = size(A, 3);
    [fpath, fname, ext] = fileparts(fn);
    fn_list = [fn];
    for s=1:nslices
       slice_fname = fullfile(fpath, sprintf("%s_%04d%s", fname, s, ext));
       write_volume(slice_fname, A(:,:,s), type)
       fn_list = [fn_list; slice_fname];
    end
end

function fn = write_volume(fn, A, type)
fp = fopen(fn, 'w');
A = shiftdim(A,3);

switch(lower(type))
 case 'uchar'
  fwrite (fp,A,'uint8');
 case 'short'
  fwrite (fp,A,'int16');
 case 'ushort'
  fwrite (fp,A,'uint16');
 case 'uint32'
  fwrite (fp,A,'uint32');
 case 'float'
  fwrite (fp,A,'real*4');
 otherwise
  fclose(fp);
  error ('Sorry, unsupported type');
end
fclose(fp);
end

function write_header(fn, Asz, offset, spacing, type)
    if is_octave
        fn = cellstr(fn);
    end
    if length(fn) > 1
        for i = 2:length(fn)
            fn_temp = fn(i);
            if is_octave
                fn_temp = char(fn_temp);
            end
            [fpath, fname, ext] = fileparts(fn_temp);
            fn(i) = strcat(fname, ext);
        end
        fn_temp = fn(1);
        if is_octave
           fn_temp = char(fn_temp);
        end
        [fpath, fname, ext] = fileparts(fn_temp);
    else
        if is_octave
            fn = char(fn);
        end
        [fpath, fname, ext] = fileparts(fn);
        fn = strcat(fname, ".raw");
    end
    header_filename = fullfile(fpath, strcat(fname, ".mhd"))

    fh = fopen(header_filename,'w');
    if (fh == -1)
      error ('Cannot open mha file for writing');
    end

    fprintf (fh,'ObjectType = Image\n');
    fprintf (fh,'NDims = %d\n', length(Asz));
    fprintf (fh,'BinaryData = True\n');
    fprintf (fh,'BinaryDataByteOrderMSB = False\n');
    fprintf (fh,'Offset = ');
    fprintf (fh,' %g',offset);
    fprintf (fh,'\n');
    fprintf (fh,'ElementSpacing = ');
    fprintf (fh,' %g',spacing);
    fprintf (fh,'\n');
    fprintf (fh,'DimSize = ');
    fprintf (fh,' %d',Asz);
    fprintf (fh,'\n');
    fprintf (fh,'AnatomicalOrientation = RAI\n');
    if (length(Asz) == 4)
      fprintf(fh,'ElementNumberOfChannels = 3\n');
    end

    switch(lower(type))
     case 'uchar'
      fprintf (fh,'ElementType = MET_UCHAR\n');
     case 'short'
      fprintf (fh,'ElementType = MET_SHORT\n');
     case 'ushort'
      fprintf (fh,'ElementType = MET_USHORT\n');
     case 'uint32'
      fprintf (fh,'ElementType = MET_UINT\n');
     case 'float'
      fprintf (fh,'ElementType = MET_FLOAT\n');
        otherwise
      error ('Sorry, unsupported type');
    end
    
    if length(fn) > 1
        fprintf (fh, 'ElementDataFile = LIST\n');
        fn_temp = fn(2:end);
        if is_octave
          fn_temp = char(fn_temp);
        end
        fprintf (fh, '%s\n', fn_temp);
    else
        fprintf (fh,'ElementDataFile = %s\n', fn);
    end

    fclose(fh);
end
