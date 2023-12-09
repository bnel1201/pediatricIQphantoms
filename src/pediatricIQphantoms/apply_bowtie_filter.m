function I0_afterbowtie = apply_bowtie_filter(I0, sg, mu_water, patient_diameter)
    if exist('patient_diameter', 'var') == false
        patient_diameter = 200;
    end
    ell_disk = [0 0 patient_diameter/2 patient_diameter/2 0 1];
    pathlength = ellipse_sino(sg, ell_disk, 'oversample',4);
    maxpl = max(pathlength(:));
    bowtie = mu_water*(maxpl-pathlength);
    I0_afterbowtie=I0*exp(-bowtie);           
end 