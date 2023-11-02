function width = MTF_width(halfmtf, threshold, freq_vector)
% function width = MTF_width(halfmtf,_f_cutoff)
% Compute MTF width at the specified "threshold" value (default 50%). 
%
% RZeng, FDA/CDRH/OSEL/DIDSR, 
% 12/6/2019

%the MTF should have a maximum of 1. if not, normalize it first. 
mtf_max = max(halfmtf);
if mtf_max~=1
    halfmtf = halfmtf/mtf_max;
end
    
delta = halfmtf - threshold;

%Find the zero cross points
sign_delta = sign(delta(1:end-1).*delta(2:end));
id_cross_list = find(sign_delta <= 0);
id_cross = id_cross_list(1);

if sign_delta(id_cross)==0
    width = freq_vector(id_cross+1);
else
    %perform a linear interpolation to find the crossing frequency.
    x1 = freq_vector(id_cross(1));   
    y1 = halfmtf(id_cross(1));
    x2 = freq_vector(id_cross+1);   
    y2 = halfmtf(id_cross+1);
    m = (y2-y1)/(x2-x1);
    width =  1/m * (threshold - y1 + m*x1);
end
