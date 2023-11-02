load ../results/aapm2019/nps_I0_240000
marker_opt = {'o-b','o-g','o-r','o-c','o-m'}
all_recon_type = {'fbp_ramp', 'fbp_hann', 'mbir', 'redcnn', 'cnn3'};
dx = 0.664;
df = 1/(2*dx)/32;
[cx,cy,c,dummy]=radial_profiles_fulllength(nps(:,:,1),[0:5:180]);
fr = [0:length(dummy)-1]*df;
figure;
for i=1:5
    [cx,cy,c,mc(:,i)]=radial_profiles_fulllength(nps(:,:,i),[0:5:180]);
    plot(fr,mc(:,i),marker_opt{i}, 'Linewidth',2);
    hold on
end

legend('FBP-ramp', 'FBP-hann','MBIR','RED-CNN','CNN3');
xlabel 'Frequency (lp/mm)'
ylabel 'Amplitude'


