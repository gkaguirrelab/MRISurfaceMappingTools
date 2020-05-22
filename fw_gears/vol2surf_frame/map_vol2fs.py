import os 

def map_vol2fs(volume_to_interpolate, fs_subject_dir, subject_name, freesurfer_environment_path, native_output_path, fsaverage_output_path, surf_temp='fsaverage'):
    
    # Strip the .nii.gz get the image name
    fmri_name = os.path.split(volume_to_interpolate)[1]
    if volume_to_interpolate[-3:] == '.gz':
        fmri_name = fmri_name[:-7]
    elif volume_to_interpolate[-3:] == 'nii':
        fmri_name = fmri_name[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention')

    # Register map to the native surface
    native_left = os.path.join(native_output_path, 'lh.native.' + fmri_name + '.mgz')
    native_right = os.path.join(native_output_path, 'rh.native.' + fmri_name + '.mgz')
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --hemi lh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                              volume_to_interpolate, subject_name, native_left))
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --hemi rh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                              volume_to_interpolate, subject_name, native_right))
    
    # Register map to fsaverage
    fsaverage_left = os.path.join(fsaverage_output_path, 'lh.fsaverage.' + fmri_name + '.mgz')
    fsaverage_right = os.path.join(fsaverage_output_path, 'rh.fsaverage.' + fmri_name + '.mgz')
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --trgsubject %s --hemi lh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                              volume_to_interpolate, subject_name, surf_temp,
                                                                                              fsaverage_left))
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --trgsubject %s --hemi rh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                              volume_to_interpolate, subject_name, surf_temp,
                                                                                              fsaverage_right))
    
    return (native_left, native_right, fsaverage_left, fsaverage_right)