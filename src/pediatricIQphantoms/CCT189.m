function ell = CCT189(patient_diameter, attenuation_coefficient, lesion_diameter, relative_lesion_location)
    % creates CATPHAN 600 low contrast detectability module but
    % with options for variable patient diameter and lesion diameter
    % <https://www.phantomlab.com/catphan-600>
    % ======= 
    % inputs:
    % patient_diameter: diameter of circle in mm
    %  - lesion_diameter: diameter of lesion diameter relative to patient diameter [unitless], absolute diameter can be found as lesion_diameter*patient_diameter
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

    if ~exist('lesion_diameter', 'var')
        lesion_diameter=false
    end
    if ~lesion_diameter
        lesion_diameter = [0.015 0.025 0.035 0.05] # in order of 14 HU, 7 HU, 5 HU, and 3 HU
    end
    assert(length(lesion_diameter)==4)
    if all(lesion_diameter < 1)
     # if lesion diameters < 1mm, interpret as relative diameters
        r = (patient_diameter * lesion_diameter) / 2;
    else
    # if lesion diameters > 1 interpret as absolute value in mm
        r = lesion_diameter/2;
    end

    d = relative_lesion_location * patient_diameter / 2;

    p = patient_diameter;
    ell = [0 0 p/2 p/2 0 attenuation_coefficient;                                  % water
    d*cosd(45)  d*sind(45)   r(1)  r(1) 0 14/1000*attenuation_coefficient     % 3mm, 14 HU
   -d*cosd(45)  d*sind(45)   r(2)  r(2) 0 7/1000*attenuation_coefficient     % 5 mm, 7 HU
   -d*cosd(45) -d*sind(45)   r(3)  r(3) 0 5/1000*attenuation_coefficient     % 7 mm, 5 HU
    d*cosd(45) -d*sind(45)   r(4)  r(4) 0 3/1000*attenuation_coefficient     % 10 mm, 3 HU
    ];
end