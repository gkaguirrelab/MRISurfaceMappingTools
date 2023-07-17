import os

def fsNativeLabel_to_FSLRLabel(left_hemi_label, right_hemi_label, subject_freesurfer_folder, subject_name, standard_mesh_atlases, workdir, left_output_label, right_output_label):

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
    label_in = os.path.join(workdir, 'temp.label.gii')
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'lh.white')
    os.system(f'mris_convert --label {left_hemi_label} {subject_name} {fs_white} {label_in}')
    os.system(f'wb_command -label-resample {label_in} {current_gifti_sphere} {new_sphere} ADAP_BARY_AREA {left_output_label} -area-surfs {midthickness_current} {midthickness_new}')


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
    label_in = os.path.join(workdir, 'temp.label.gii')
    fs_white = os.path.join(subject_freesurfer_folder, 'surf', 'rh.white')
    os.system(f'mris_convert --label {right_hemi_label} {subject_name} {fs_white} {label_in}')
    os.system(f'wb_command -label-resample {label_in} {current_gifti_sphere} {new_sphere} ADAP_BARY_AREA {right_output_label} -area-surfs {midthickness_current} {midthickness_new}')