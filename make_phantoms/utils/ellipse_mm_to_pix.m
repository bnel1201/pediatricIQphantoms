function ell_pixels = ellipse_mm_to_pix(ell, fov, nx)
    ell_pixels = ell;
    ell_pixels(:, 1:4) = ell(:, 1:4) * nx/fov;
    ell_pixels(:, 1:2) = round(ell_pixels(:, 1:2) + nx/2);
end