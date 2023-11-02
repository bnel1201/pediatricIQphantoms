function [values] = circle_roi(img, x, y, r)
%circle_roi
%   Grab a circle roi at center (x, y) and radius r then return those
%   values as a list for doing statistics on e.g. mean or std
[xgrid, ygrid] = meshgrid(1:size(img,2), 1:size(img,1));
mask = ((xgrid-y).^2 + (ygrid-x).^2) <= r.^2;
% values = mask;
values = img(mask);
end

