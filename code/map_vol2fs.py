import os 

def map_vol2fs(volume_to_interpolate, subject_name, native_output_path, fsaverage_output_path, surf_temp='fsaverage', interp='trilinear', freesurfer_environment_path=''):
    
    '''
    This function maps human volumetric time-series or R2 maps to 
    subject's native space and to any template provided by Freesurfer   
    (eg. fsaverage, fsaverage_sym). Make sure that you set your Freesurfer
    subjects directory and run recon-all on the subject prior to running this 
    script.
    
    Required software:
        - Python 3 (Might work alright with python 2 as well, but not tested)
        - Freesurfer
    
    Required Pyton packages:
        None. 
    
    Inputs:
        - volume_to_interpolate = This is your nifti input volumetric time 
          series or R2 map image. Should have the .nii or .nii.gz extention.
        - subject_name = Name of the subject. This must match the name of the
          subject's recon-all folder you have in your $SUBJECTS_DIR.
        - native_output_path = A location to save the native surface maps
        - fsaverage_output_path = A location to save the template registered
          maps.
        - surf_temp = Template name you want to map to. Can be anything FS
          provides. Check the subjects directory in Freesurfer folder for the
          options. Optional (default: fsaverage).
        - freesurfer_environment_path = Path to the bin folder in your 
          Freesurfer directory. This can be left empty if you already set path 
          to your Freesurfer folder and can call Freesurfer functions the your 
          terminal. 
    Output:
        Outputs 4 images. lh/rh.native.<original_image_name> and
        lh/rh.<template_name>.<original_image_name>. The function also returns
        paths to the newly created surface maps if requested.
    '''
    
    # Strip the .nii.gz get the image name
    fmri_name = os.path.split(volume_to_interpolate)[1]
    if volume_to_interpolate[-3:] == '.gz':
        fmri_name = fmri_name[:-7]
    elif volume_to_interpolate[-3:] == 'nii':
        fmri_name = fmri_name[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention')

    # Register map to subject's native surface
    native_left = os.path.join(native_output_path, 'lh.native.' + fmri_name + '.mgz')
    native_right = os.path.join(native_output_path, 'rh.native.' + fmri_name + '.mgz')
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --interp %s --hemi lh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                          volume_to_interpolate, subject_name, interp, native_left))
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --interp %s --hemi rh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                          volume_to_interpolate, subject_name, interp, native_right))
    
    # Register map to specified Freesurfer template
    fsaverage_left = os.path.join(fsaverage_output_path, 'lh.%s.' % surf_temp + fmri_name + '.mgz')
    fsaverage_right = os.path.join(fsaverage_output_path, 'rh.%s.'  % surf_temp + fmri_name + '.mgz')
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --interp %s --trgsubject %s --hemi lh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                                          volume_to_interpolate, subject_name, interp, surf_temp,
                                                                                                          fsaverage_left))
    os.system('%s --mov %s --regheader %s --projfrac 0.5 --interp %s --trgsubject %s --hemi rh --o %s' % (os.path.join(freesurfer_environment_path, 'mri_vol2surf'),
                                                                                                          volume_to_interpolate, subject_name, interp, surf_temp,
                                                                                                          fsaverage_right))
    
    return (native_left, native_right, fsaverage_left, fsaverage_right)