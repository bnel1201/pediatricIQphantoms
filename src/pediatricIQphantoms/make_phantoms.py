from pathlib import Path
import argparse
import tomli
import numpy as np
import os

from oct2py import octave
import pydicom
from datetime import datetime
import SimpleITK as sitk

class CTobj():
    """
    A class to hold CT simulation data
    """
    def __init__(self, phantom='CCT189', patient_diameter=200, reference_diameter=200,
                 reference_fov=340, I0=3e5, nb=900, na=580, ds=1, sid=595, sdd=1085.6,
                 offset_s=1.25, down=1, has_bowtie=False, add_noise=True, aec_on=True,
                 nx=512, fov=340, fbp_kernel='hanning,2.05', nsims=1, relative_lesion_diameter=False, age=0,
                 patientname="", patientid=0, studyname="", studyid=0, seriesname="", seriesid=0) -> None:
        self.phantom=phantom
        self.patient_diameter=patient_diameter
        self.reference_diameter=reference_diameter
        self.reference_fov=reference_fov
        self.I0=I0
        self.ndetectors=nb
        self.nangles=na
        self.detector_size_mm=ds
        self.sid=sid
        self.sdd=sdd
        self.detector_offset=offset_s
        self.down_sampling=down
        self.has_bowtie=has_bowtie
        self.add_noise=add_noise
        self.aec=aec_on
        self.matrix_size=nx
        self.fov=fov
        self.kernel=fbp_kernel
        self.nsims=nsims
        self.relative_lesion_diameter=relative_lesion_diameter
        self.age=age
        self.patientname=patientname
        self.patientid=patientid
        self.studyname=studyname
        self.studyid=studyid
        self.seriesname=seriesname
        self.seriesid=seriesid
        self.recon=None
        self.projections=None
        self.groundtruth=None

    def run(self):
        phantom=self.phantom
        patient_diameter=self.patient_diameter
        reference_diameter=self.reference_diameter
        reference_fov=self.reference_fov
        relative_lesion_diameter=self.relative_lesion_diameter
        I0=self.I0
        nb=self.ndetectors
        na=self.nangles
        ds=self.detector_size_mm
        sdd=self.sdd
        sid=self.sid
        offset_s=self.detector_offset
        down=self.down_sampling
        has_bowtie=self.has_bowtie
        add_noise=self.add_noise
        aec_on=self.aec
        nx=self.matrix_size
        fov=self.fov
        fbp_kernel=self.kernel
        nsims=self.nsims

        resdict = mirt_sim(phantom=phantom, patient_diameter=patient_diameter, reference_diameter=reference_diameter, reference_fov=reference_fov,
                           I0=I0, nb=nb, na=na, ds=ds, sid=sid, sdd=sdd, offset_s=offset_s, down=down, has_bowtie=has_bowtie,
                           add_noise=add_noise, aec_on=aec_on, nx=nx, fov=fov, fbp_kernel=fbp_kernel, nsims=nsims, relative_lesion_diameter=relative_lesion_diameter)
        self.recon = resdict['recon']
        self.projections = resdict['sinogram_noiseless']
        self.groundtruth = resdict['ground_truth']
        return self
    
    def write_to_dicom(self, fname, groundtruth=False):
        fpath = pydicom.data.get_testdata_file("CT_small.dcm")
        ds = pydicom.dcmread(fpath)
        # update meta info
        ds.Manufacturer = 'Siemens (simulated)'
        ds.ManufacturerModelName = 'Definition AS+ (simulated)'
        time = datetime.now()
        ds.InstanceCreationDate = time.strftime('%Y%m%d')
        ds.InstanceCreationTime = time.strftime('%H%M%S')
        ds.InstitutionName = 'FDA/CDRH/OSEL/DIDSR'
        ds.StudyDate = ds.InstanceCreationDate
        ds.StudyTime = ds.InstanceCreationTime
        
        ds.PatientName = self.patientname
        ds.SeriesNumber = self.seriesid
        
        ds.PatientAge = f'{int(self.age):03d}Y'
        ds.PatientID = f'{int(self.patientid):03d}'
        del(ds.PatientWeight)
        del(ds.ContrastBolusRoute)
        del(ds.ContrastBolusAgent)
        ds.ImageComments = f"effctive diameter [cm]: {self.patient_diameter}"
        ds.ScanOptions = 'AXIAL MODE'
        ds.ReconstructionDiameter = self.fov
        ds.ConvolutionKernel ='fbp D45'
        ds.Exposure = self.I0
        
        # load image data
        ds.StudyDescription = f"{self.I0} photons " + self.seriesname + " " + ds.ConvolutionKernel
        if self.recon.ndim == 2: self.recon = self.recon[None]
        nslices, ds.Rows, ds.Columns = self.recon.shape
        assert nslices == self.nsims
        ds.SpacingBetweenSlices = ds.SliceThickness
        ds.DistanceSourceToDetector = self.sdd
        ds.DistanceSourceToPatient = self.sid
        
        ds.PixelSpacing = [self.fov/self.matrix_size, self.fov/self.matrix_size]
        ds.SliceThickness = ds.PixelSpacing[0]

        ds.KVP = 120
        ds.StudyID = str(self.studyid)
        # series instance uid unique for each series
        end = ds.SeriesInstanceUID.split('.')[-1]
        new_end = str(int(end) + self.studyid)
        ds.SeriesInstanceUID = ds.SeriesInstanceUID.replace(end, new_end)
        
        # study instance uid unique for each series
        end = ds.StudyInstanceUID.split('.')[-1]
        new_end = str(int(end) + self.studyid)
        ds.StudyInstanceUID = ds.StudyInstanceUID.replace(end, new_end)
        ds.AcquisitionNumber = self.studyid

        fname = Path(fname)
        fname.parent.mkdir(exist_ok=True, parents=True)
        # saveout slices as individual dicom files
        fnames = []
        vol = self.groundtruth if groundtruth else self.recon
        if vol.ndim == 2: vol = vol[None]
        for slice_idx, array_slice in enumerate(vol):
            ds.InstanceNumber = slice_idx + 1 # image number
            # SOP instance UID changes every slice
            end = ds.SOPInstanceUID.split('.')[-1]
            new_end = str(int(end) + slice_idx + self.studyid + self.seriesid)
            ds.SOPInstanceUID = ds.SOPInstanceUID.replace(end, new_end)
            # MediaStorageSOPInstanceUID changes every slice
            end = ds.file_meta.MediaStorageSOPInstanceUID.split('.')[-1]
            new_end = str(int(end) + slice_idx + self.studyid + self.seriesid)
            ds.file_meta.MediaStorageSOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID.replace(end, new_end)
            # slice location and image position changes every slice
            ds.SliceLocation = self.nsims//2*ds.SliceThickness + slice_idx*ds.SliceThickness
            ds.ImagePositionPatient[-1] = ds.SliceLocation
            ds.ImagePositionPatient[0] = -ds.Rows//2*ds.PixelSpacing[0]
            ds.ImagePositionPatient[1] = -ds.Columns//2*ds.PixelSpacing[1]
            ds.ImagePositionPatient[2] = ds.SliceLocation
            ds.PixelData = array_slice.copy(order='C').astype('int16') - int(ds.RescaleIntercept)
            dcm_fname = fname.parent / f'{fname.stem}_{slice_idx:03d}{fname.suffix}' if nslices > 1 else fname
            fnames.append(dcm_fname)
            pydicom.write_file(dcm_fname, ds)
        return fnames


def mirt_sim(phantom='CCT189', patient_diameter=200, reference_diameter=200, reference_fov=340,
             I0=3e5, nb=900, na=580, ds=1, sid=595, sdd=1085.6, offset_s=1.25, down=1, has_bowtie=False,
             add_noise=True, aec_on=True, nx=512, fov=340, fbp_kernel='hanning,2.05', nsims=1, relative_lesion_diameter=False):
    """
    Python wrapper for calling Michigan Image Reconstruction Toolbox (MIRT) Octave function 
    """
    if patient_diameter == reference_diameter:
        fov = reference_fov
    else:
        fov = 1.1*patient_diameter
    curdir = os.path.dirname(os.path.realpath(__file__))
    octave.cd(curdir)
    return octave.ct_sim(phantom, patient_diameter, reference_diameter,    relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims)


def run_batch_sim(image_directory: str, model=['CCT189'], diameter=[200], reference_diameter=200, framework='MIRT',
         nsims=1, nangles=580, aec_on=True, add_noise=True, full_dose=3e5,
         dose_level=[1.0], sid=595, sdd=1085.6, nb=880,
         ds=1, offset_s=1.25, fov=340, image_matrix_size=512, fbp_kernel='hanning,2.05', has_bowtie=True):
    """
    Return a list of random ingredients as strings.

    :param image_directory: Directory to save simulated outputs
    :type image_directory: str
    :param model: Optional, select phantom model to simulate current options include ['CCT189', 'CTP404']
    :type model: list[str]
    :param diameter: Optional, simulated phantom diameter in mm
    """

    image_directory = Path(os.path.abspath(image_directory))
    print(image_directory)
    phantoms = model

    dose_level = full_dose * np.array(dose_level)
    recon = 'fbp'
    reference_fov = 340
    for phantom_idx, phantom in enumerate(phantoms):
        print(f'{phantom} Simulation series {phantom_idx}/{len(phantoms)}')
        for patientid, patient_diameter in enumerate(diameter):
            patientname = f'{patient_diameter/10} cm {phantom}'
            for studyid, dose in enumerate(dose_level):
                rel_dose = 100*dose/dose_level.max()
                studyname = f'{int(rel_dose)}% dose'
                ct = CTobj(patient_diameter=patient_diameter, reference_diameter=reference_diameter, reference_fov=reference_fov,
                           I0=dose, nb=nb, na=nangles, ds=ds, sid=sid, sdd=sdd, offset_s=offset_s, down=1, has_bowtie=has_bowtie,
                           add_noise=add_noise, aec_on=aec_on, nx=image_matrix_size, fov=fov, fbp_kernel=fbp_kernel, nsims=nsims,
                           patientname=patientname, patientid=patientid, studyname=studyname, studyid=studyid, seriesname=f'{patientname} {studyname}')
                ct.run()
                fname = image_directory / phantom / f'diameter{patient_diameter}mm' / f'dose_{int(rel_dose):03d}' / f'{recon} {fbp_kernel.replace(',','').replace('.','')}' / f'{ct.patientname}.dcm'
                ct.write_to_dicom(fname)
            # add noise free
            ct.nsims=1
            ct.add_noise=False
            ct.run()
            fname = image_directory / phantom / f'diameter{patient_diameter}mm' / f'{ct.patientname}_noisefree.dcm'
            ct.write_to_dicom(fname)
            # add ground truth
            fname = image_directory / phantom / f'diameter{patient_diameter}mm' / f'{ct.patientname}_groundtruth.dcm'
            ct.write_to_dicom(fname, groundtruth=True)


def main():
    parser = argparse.ArgumentParser(description='Make Pediatric IQ Phantoms')
    parser.add_argument('config', nargs='?', default=None,
                        help="configuration toml file containing simulation parameters")
    args = parser.parse_args()

    if args.config:
        with open(args.config, mode="rb") as fp:
            config = tomli.load(fp)
    else:
        with open("configs/defaults.toml", mode="rb") as fp:
            config = tomli.load(fp)
    
    sim = dict()
    for c in config['simulation']:
        sim.update(c)
        run_batch_sim(**sim)

if __name__ == '__main__': main()