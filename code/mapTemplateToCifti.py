import os
from map_vol2fs import map_vol2fs

def mapTemplateToCifti(volume_to_interpolate, subject_name, workdir, freesurfer_environment_path=''):
    
    # make folders for native and fsaverage mgz
    fsaverage_output_path = os.path.join(workdir, 'fsaverage')
    native_output_path = os.path.join(workdir, 'native')
    if not os.path.exists(fsaverage_output_path):
        os.system('mkdir {}'.format(fsaverage_output_path))
    if not os.path.exists(native_output_path):
        os.system('mkdir {}'.format(native_output_path))
        
    map_vol2fs(volume_to_interpolate, subject_name, native_output_path, fsaverage_output_path, surf_temp='fsaverage', interp='nearest', freesurfer_environment_path='')