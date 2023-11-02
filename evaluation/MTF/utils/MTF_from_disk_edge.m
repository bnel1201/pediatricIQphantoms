function [mtf, freq_vector, esf, success] = MTF_from_disk_edge(imgdisk)
% function [mtf, freq_vector, esf] = MTF_from_disk_edge(imgdisk)
% Estimate the mtf function from disk images. 
% Input:
%   imgdisk: a 3D array containing multiple realization of a disk image.
% Outputs:
%   mtf, freq_vector: 'mtf' is the estimated modulation transfer function at the corresponding 'freq_vector' values.
%   esf: estimated edge spreaf function;
%   success: '0' or '1' indicating a successful estimation or not.  
% 12/13/2019, R Zeng, FDA/CDRH/OSEL/DIDSR

[nx, ny, nz] = size(imgdisk);
roisz = min(nx,ny);
[yy, xx] = meshgrid([1:nx], [1:ny]);

%predefined uniform sampling points
nn = 5; %presampling rate 
delta = 1/nn;
min_dist = 1;
dist_uniform = 1 : delta : roisz/2; 
esfi = zeros(nz,length(dist_uniform));

for iz = 1:nz 
    disk_img = imgdisk(:,:,iz);
    %  find the center of the disk
    disk_mean = round(mean(mean(disk_img(round(roisz/2)+[-4:4], round(roisz/2)+[-4:4]))));
    bkg_mean = round(mean(mean(disk_img(1:5,:))));
    if(disk_mean<bkg_mean) %if negtive contrast, invert the scale
        neg_contrast = 1;
        disk_img = -disk_img;
        disk_mean = -disk_mean;
        bkg_mean = -bkg_mean;
    end
    edge_thr = (bkg_mean*0.4+disk_mean*0.6):10:disk_mean;
    for jj = 1:length(edge_thr)
        a(jj) = mean(xx(disk_img>edge_thr(jj))); 
        b(jj) = mean(yy(disk_img>edge_thr(jj)));
    end
    a=a(~isnan(a));
    b=b(~isnan(b));
    x0 = mean(a); y0 = mean(b);    
    
    %get the distance matrix
    dist_to_ctr = sqrt((xx - x0).^2+(yy - y0).^2); % distance to center
    dist_to_ctr = dist_to_ctr(:);
    [dist_sampled, sort_idx] = sort(dist_to_ctr(:));
    [dist_unique, temp, unique_idx] = unique(dist_sampled); 
    
    %Get ESF    
    esf_temp = disk_img(:);
    esf_temp = esf_temp(sort_idx);
    esf_unique = accumarray(unique_idx, esf_temp, [], @mean);
    esf_fitted = interp1(dist_unique, esf_unique, dist_uniform,'linear');
    
    esfi(iz,:) = esf_fitted;
end

%align the edge and then average
halflen = round(length(dist_uniform)/4);%3);
esfi_aligned = zeros(nz, 2*halflen+1);
for iz=1:nz
    l_flt = 11;%9;
    smoothflt = hann(l_flt);%hann(9);
    smoothflt = smoothflt/sum(smoothflt); %Normalize
    esfi_smth = conv(smoothflt, esfi(iz,:));
    esfi_smth = esfi_smth(l_flt:end-l_flt+1); %Only take the valid part w/o zero padded in convlution.
    lsf_smth = (-esfi_smth(3:end)+esfi_smth(1:end-2))/(2*delta);
    f = fit((1:length(lsf_smth))', lsf_smth(:), 'gauss1');
    [lsf_max, edge_pix] = max(f(1:length(lsf_smth)));
%	iz, edge_pix, halflen,%for debug
    if(edge_pix+halflen>length(esfi)|edge_pix-halflen<1)
         disp('MTF failed because the disk image is too noisy.');
         mtf=0; freq_vector = 0; esf = 0;
         success = 0;
         return;
    end

    esfi_aligned(iz,:) = esfi(iz,edge_pix+[-halflen:halflen]);
    
end
if(nz>1)
    esf_edge = mean(esfi_aligned);
else
    esf_edge = esfi;
end

esf = esf_edge;

% apply sigmoid fit to the edge spread function to reduce the disturbance of noise on the flat part of the curve.
apply_sigmoid_fit=true;
if(apply_sigmoid_fit)
midseg = round(length(esf)/2)+[-round(length(esf)/2.5):floor(length(esf)/2.5)];% 1:length(esf_edge);
sigm_param = sigm_fit((1:length(esf_edge(midseg)))', esf_edge(midseg));
fsigm = @(param,xval) param(1)+(param(2)-param(1))./(1+10.^((param(3)-xval)*param(4)));
x=1:length(esf);
y=fsigm(sigm_param,x);
dummy=corrcoef(y(midseg), esf_edge(midseg));
rho = dummy(1,2);
if(rho<0.8)
   disp('MTF failed because the disk image is too noisy.');
   mtf=0; freq_vector = 0; esf = 0;
   success = 0;
   return;
end
esf = y; 
end

% lsf: take derivative of ESF 
lsf = (-esf(3:end)+esf(1:end-2))/(2*delta);
%f = fit((1:length(lsf))', lsf(:), 'gauss1'); %to make the center easier to be located
f= lsf;

% Center LSF
[lsf_max, center_pix] = max(f(1:length(lsf)));
%lsf = f(1:length(lsf));%test, estimate the mtf using the gaussian fitted curve
shortside_len = min(center_pix-1, length(lsf)-center_pix);
lsf_centered = lsf(center_pix+[-shortside_len:shortside_len]);
dist_centered = [-shortside_len:shortside_len]*delta;

% filter lsf by hann filter of window size 20 pixels
filter_hann = 0.5*(1+cos(2*pi*dist_centered/20));
lsf_filtered = lsf_centered.*filter_hann;
%lsf_disk = lsf_filtered; %for output
lsf_disk = lsf_centered;
%MTF
lsf_fft = fftshift(abs(fft(lsf_filtered)))/sum(lsf_filtered);
freq_vector = 1/(2*delta)*linspace(0, 1, (length(lsf_fft)+1)/2);
mtf_center_pix = round(length(lsf_fft)/2); 
mtf = lsf_fft(mtf_center_pix:end);

success = 1;




