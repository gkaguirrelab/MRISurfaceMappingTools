import os

def fsNativeScalar_to_FSLRScalar(left_hemi_scalar, right_hemi_scalar, subject_freesurfer_folder, subject_name, standard_mesh_atlases, workdir, left_output_scalar, right_output_scalar, interp='ADAP_BARY_AREA'):

    ########## LEFT HEMI
    # Surface prep left hemi
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'lh.white')
    fs_pial = os.path.join(subject_freesurfer_folder, 'surf', 'lh.pial')
    fs_sphere_reg = os.path.join(subject_freesurfer_folder, 'surf', 'lh.sphere.reg')
    new_sphere = os.path.join(standard_mesh_atlases, 'resample_fsaverage', 'fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii')
    midthickness_current = os.path.join(workdir, 'lh.midthickness.surf.gii')
    midthickness_new = os.path.join(workdir, 'subject.lh.midthickness.32k_fs_LR.surf.gii')
    current_gifti_sphere = os.path.join(workdir, 'lh.sphere.reg.surf.gii')  
    os.system(f'wb_shortcuts -freesurfer-resample-prep {fs_white} {fs_pial} {fs_sphere_reg} {new_sphere} {midthickness_current} {midthickness_new} {current_gifti_sphere}')

    # Now map the maps to gifti label format
    # Left hemi first
    scalar_in = os.path.join(workdir, 'temp.dscalar.gii')
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'lh.white')
    os.system(f'mris_convert -f {left_hemi_scalar} {fs_white} {scalar_in}')
    if interp == 'BARYCENTRIC':
        os.system(f'wb_command -metric-resample {scalar_in} {current_gifti_sphere} {new_sphere} BARYCENTRIC {left_output_scalar} -area-surfs {midthickness_current} {midthickness_new} -largest')
    elif interp == 'ADAP_BARY_AREA':
        os.system(f'wb_command -metric-resample {scalar_in} {current_gifti_sphere} {new_sphere} ADAP_BARY_AREA {left_output_scalar} -area-surfs {midthickness_current} {midthickness_new}')
    else:
        raise ValueError("Interpolation method is unknown. Use ADAP_BARY_AREA or BARYCENTRIC")

    ########## RIGHT HEMI
    # Surface prep right hemi
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'rh.white')
    fs_pial = os.path.join(subject_freesurfer_folder, 'surf', 'rh.pial')
    fs_sphere_reg = os.path.join(subject_freesurfer_folder, 'surf', 'rh.sphere.reg')
    new_sphere = os.path.join(standard_mesh_atlases, 'resample_fsaverage', 'fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii')
    midthickness_current = os.path.join(workdir, 'rh.midthickness.surf.gii')
    midthickness_new = os.path.join(workdir, 'subject.rh.midthickness.32k_fs_LR.surf.gii')
    current_gifti_sphere = os.path.join(workdir, 'rh.sphere.reg.surf.gii')
    os.system(f'wb_shortcuts -freesurfer-resample-prep {fs_white} {fs_pial} {fs_sphere_reg} {new_sphere} {midthickness_current} {midthickness_new} {current_gifti_sphere}')

    # Now map the maps to gifti label format
    # Left hemi first
    scalar_in = os.path.join(workdir, 'temp.dscalar.gii')
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'rh.white')
    os.system(f'mris_convert -f {right_hemi_scalar} {fs_white} {scalar_in}')
    if interp == 'BARYCENTRIC':
        os.system(f'wb_command -metric-resample {scalar_in} {current_gifti_sphere} {new_sphere} BARYCENTRIC {right_output_scalar} -area-surfs {midthickness_current} {midthickness_new} -largest')
    if interp == 'ADAP_BARY_AREA':
        os.system(f'wb_command -metric-resample {scalar_in} {current_gifti_sphere} {new_sphere} ADAP_BARY_AREA {left_output_scalar} -area-surfs {midthickness_current} {midthickness_new}')
    else:
        raise ValueError("Interpolation method is unknown. Use ADAP_BARY_AREA or BARYCENTRIC")