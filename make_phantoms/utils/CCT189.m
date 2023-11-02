function ell = CCT189(patient_diameter, attenuation_coefficient, relative_lesion_diameter, relative_lesion_location)
    % creates CATPHAN 600 low contrast detectability module but
    % with options for variable patient diameter and lesion diameter
    % ======= 
    % inputs:
    % patient_diameter: diameter of circle in mm
    %  - relative_lesion_diameter: diameter of lesion diameter relative to patient diameter [unitless], absolute diameter can be found as relative_lesion_diameter*patient_diameter
    %  - attenuation_coefficient:  [units: 1/mm] default is for water at 60 keV, if taking values from standard tables which report in 1/cm, be sure to divide by 10 to convert to 1/mm
    if ~exist('patient_diameter', 'var')
        patient_diameter = 150;
    end

    if ~exist('relative_lesion_location', 'var')
        relative_lesion_location = 0.4;
    end

    if ~exist('attenuation_coefficient', 'var')
        attenuation_coefficient = 0.2;
    end

    if ~exist('relative_lesion_diameter', 'var')
        relative_lesion_diameter = false;
    end


    standard_radii = [3/2 5/2 7/2 10/2];
    if relative_lesion_diameter
        r = relative_lesion_diameter * patient_diameter/2 * standard_radii;
    else
        r = standard_radii
    end
    d = relative_lesion_location * patient_diameter / 2;

    p = patient_diameter;
    ell = [0 0 p/2 p/2 0 attenuation_coefficient;                                  % water
    d*cosd(45)  d*sind(45)   r(1)  r(1) 0 14/1000*attenuation_coefficient;     % 3mm, 14 HU
   -d*cosd(45)  d*sind(45)   r(2)  r(2) 0 7/1000*attenuation_coefficient;     % 5 mm, 7 HU
   -d*cosd(45) -d*sind(45)   r(3)  r(3) 0 5/1000*attenuation_coefficient;     % 7 mm, 5 HU
    d*cosd(45) -d*sind(45)   r(4)  r(4) 0 3/1000*attenuation_coefficient;     % 10 mm, 3 HU
    ];
end