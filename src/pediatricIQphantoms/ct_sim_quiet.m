function res = ct_sim_quiet(phantom, patient_diameter, reference_diameter, relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims)
 % ct_sim using evalc to mute std output
    echo off
    function disp(x)
    end
    evalc("res = ct_sim(phantom, patient_diameter, reference_diameter, relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims);");
end