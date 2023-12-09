function proj = replace_zeros(proj)
    if any(proj(:) == 0)
        warn('%d of %d values are 0 in sinogram!', ...
            sum(proj(:)==0), length(proj(:)));
        proj(proj==0) = 1;
    end
end