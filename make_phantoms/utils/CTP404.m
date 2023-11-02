function ell = CTP404(patient_diameter, attenuation_coefficient, relative_lesion_diameter, relative_lesion_location)
    % creates CATPHAN 600 low contrast detectability module but
    % with options for variable patient diameter and lesion diameter
    % ======= 
    % inputs:
    % patient_diameter: diameter of circle in mm
    %  - relative_lesion_diameter: diameter of lesion diameter relative to patient diameter [unitless], absolute diameter can be found as relative_lesion_diameter*patient_diameter
    %  - attenuation_coefficient:  [units: 1/mm] default is for water at 60 keV, if taking values from standard tables which report in 1/cm, be sure to divide by 10 to convert to 1/mm
    if exist('patient_diameter', 'var') == false
        patient_diameter = 150;
    end

    if exist('attenuation_coefficient', 'var') == false
        attenuation_coefficient = 0.2;
    end

    if exist('relative_lesion_diameter', 'var') == false
        relative_lesion_diameter = 0.08;
    end

    if exist('relative_lesion_location', 'var') == false
        relative_lesion_location = 0.38;
    end

    p = patient_diameter;
    r = relative_lesion_diameter * patient_diameter/2;
    d = relative_lesion_location * patient_diameter;
    % Set location of ellipses with format:
    % [x_center y_center x_radius y_radius angle_degrees mu(60 keV)]
    ell = [0 0 p/2 p/2 0 attenuation_coefficient;                              % water
           0           d           r r 0 (15/1000 + 1)*attenuation_coefficient;       % custom insert of 15 HU
           d*cosd(45)  d*sind(45)  r r 0 (-35/1000 + 1)*attenuation_coefficient;      % polystyrene (-35 HU)
           d           0           r r 0 (-100/1000 + 1)*attenuation_coefficient;     % LDPE, -100 HU
           d*cosd(45)  -d*sind(45) r r 0 (-200/1000 + 1)*attenuation_coefficient;     % PMP, -200 HU
           0           -d          r r 0 0;                            % air
           -d*cosd(45) -d*sind(45) r r 0 (990/1000 + 1)*attenuation_coefficient;      % teflon, 990 HU
           -d          0           r r 0 (340/1000 + 1)*attenuation_coefficient;      % Delrin, 340 HU
           -d*cosd(45) d*sind(45)  r r 0 (120/1000 + 1)*attenuation_coefficient;      % Acrylic, 120 HU
           0 0 0.25 0.25 0 (6000/1000 + 1)*attenuation_coefficient                    % 0.5mm bead, 1200 HU
          ];
    mu_desired = ell(:,6);
    ell(2:end, 6) = mu_desired(2:end) - attenuation_coefficient;
end