import os 
import nibabel as nb

def map_fs2gifti(fs_map_left, fs_map_right, recon_all_folder, standard_mesh_atlases_folder, temporary_intermediate, output_path, source_space='native', resolution='32k', workbench_path='', freesurfer_environment_path=''):
    
    '''
    This function maps time-series surface images that are in fsaverage or
    native space to the FSLR gifti space. Output gifti maps can be viewed by 
    overlaying them with the FSLR left and right surface meshes on wb_view.
    
    Required software:
        - Python 3 (Might work alright with python 2 as well, but not tested)
        - Connectome Workbench
        - Freesurfer
        
    Required Python packages:
        - nibabel 
          (can be installed by calling "pip install nibabel" from a terminal 
          window without the quotation marks)
    
    Inputs:
        - fs_map_left = Left hemi native or fsaverage surface maps.
        - fs_map_right = Right hemi native or fsaverage surface maps.
        - standard_mesh_atlases_folder = Path to the folder containing fs/FSLR
          calculations. A zipped version can be found in the utilities directory.
          This script doesn't do unzipping, so unzip before using it as an input
        - temporary_intermediate = A folder to save all the intermediate files.
        - output_path = A folder to save the outputs.
        - source_space = Specify whether your input images are in the native or
          fsaverage space. Default: native.
        - resolution = Output cifti resolution. Default: 32k.
        - workbench_path = Path to workbench folder. Can be left empty if you
          already set path to it can call it from your terminal.
        - freesurfer_environment_path = Path to freesurfer folder. Can be left
          empty if you already set path to it and can call it from terminal.
          
    Outputs:
        Left and right hemispere gifti FSLR images. Also, returns path to the
        new images if requested
    '''
    
    # Strip the gii get the image name
    if fs_map_left[-3:] == 'mgz':
        left_name = os.path.split(fs_map_left)[1]
        left_name = left_name[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention')
        
    # Strip the gii get the image name
    if fs_map_right[-3:] == 'mgz':
        right_name = os.path.split(fs_map_right)[1]
        right_name = right_name[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention')
        
    fs_gifti_left = os.path.join(temporary_intermediate, left_name + '_converted' + '.gii')
    fs_gifti_right = os.path.join(temporary_intermediate, right_name + '_converted' + '.gii')
    os.system('%s %s %s' % (os.path.join(freesurfer_environment_path, 'mri_convert'),
                            fs_map_left, os.path.join(temporary_intermediate, fs_gifti_left)))
    os.system('%s %s %s' % (os.path.join(freesurfer_environment_path, 'mri_convert'),
                            fs_map_right, os.path.join(temporary_intermediate, fs_gifti_right)))    
    
    if source_space == 'fsaverage':
        
        # Set paths to the files required for the operations 
        current_sphere_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                            'fsaverage_std_sphere.L.164k_fsavg_L.surf.gii')
        current_sphere_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                            'fsaverage_std_sphere.R.164k_fsavg_R.surf.gii')    
        new_sphere_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                            'fs_LR-deformed_to-fsaverage.L.sphere.%s_fs_LR.surf.gii' % resolution) 
        new_sphere_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                            'fs_LR-deformed_to-fsaverage.R.sphere.%s_fs_LR.surf.gii' % resolution)     
        metric_out_left = os.path.join(output_path, 'fs_LR-interpolated.L.%s_%s.func.gii' % (resolution, left_name)) 
        metric_out_right = os.path.join(output_path, 'fs_LR-interpolated.R.%s_%s.func.gii' % (resolution, right_name))    
        current_area_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                             'fsaverage.L.midthickness_va_avg.164k_fsavg_L.shape.gii') 
        current_area_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                             'fsaverage.R.midthickness_va_avg.164k_fsavg_R.shape.gii')     
        new_area_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                             'fs_LR.L.midthickness_va_avg.%s_fs_LR.shape.gii' % resolution)    
        new_area_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                             'fs_LR.R.midthickness_va_avg.%s_fs_LR.shape.gii' % resolution)     
       
        # Assemble the run commands and call  
        wb_run_left_string = '%s;%s -metric-resample %s %s %s ADAP_BARY_AREA %s -area-metrics %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_command'), fs_gifti_left, current_sphere_left, new_sphere_left, metric_out_left, current_area_left, new_area_left)
        wb_run_right_string = '%s;%s -metric-resample %s %s %s ADAP_BARY_AREA %s -area-metrics %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_command'), fs_gifti_right, current_sphere_right, new_sphere_right, metric_out_right, current_area_right, new_area_right)
        
        os.system(wb_run_left_string)
        os.system(wb_run_right_string)
        
    elif source_space == 'native':
        
        # Make temp maps        
        left_fs_white = os.path.join(recon_all_folder, 'surf', 'lh.white')
        left_fs_pial = os.path.join(recon_all_folder, 'surf', 'lh.pial') 
        left_fs_sphere = os.path.join(recon_all_folder, 'surf', 'lh.sphere.reg') 
        left_new_sphere = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage', 'fs_LR-deformed_to-fsaverage.L.sphere.%s_fs_LR.surf.gii' % resolution)
        left_midthickness_current_out = os.path.join(temporary_intermediate, 'lh.midthickness.surf.gii')
        left_midthickness_new_out = os.path.join(temporary_intermediate, 'sub.lh.midthickness.%s_fs_LR.surf.gii' % resolution)
        left_gifti_sphere = os.path.join(temporary_intermediate, 'lh.sphere.reg.surf.gii')
        
        right_fs_white = os.path.join(recon_all_folder, 'surf', 'rh.white')
        right_fs_pial = os.path.join(recon_all_folder, 'surf', 'rh.pial')
        right_fs_sphere = os.path.join(recon_all_folder, 'surf', 'rh.sphere.reg') 
        right_new_sphere = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage', 'fs_LR-deformed_to-fsaverage.R.sphere.%s_fs_LR.surf.gii' % resolution)
        right_midthickness_current_out = os.path.join(temporary_intermediate, 'rh.midthickness.surf.gii')
        right_midthickness_new_out = os.path.join(temporary_intermediate, 'sub.rh.midthickness.%s_fs_LR.surf.gii' % resolution)
        right_gifti_sphere = os.path.join(temporary_intermediate, 'rh.sphere.reg.surf.gii')
    
        make_surfaces_left = '%s;export PATH="/freesurfer/bin:$PATH";export PATH="/anaconda3/bin:$PATH";FSLDIR=/fsl;. ${FSLDIR}/etc/fslconf/fsl.sh;PATH=${FSLDIR}/bin:${PATH};export FSLDIR PATH;%s -freesurfer-resample-prep %s %s %s %s %s %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_shortcuts'),
                                                                                                                                                                                                                                                       left_fs_white, left_fs_pial,
                                                                                                                                                                                                                                                       left_fs_sphere, left_new_sphere,
                                                                                                                                                                                                                                                       left_midthickness_current_out,
                                                                                                                                                                                                                                                       left_midthickness_new_out,
                                                                                                                                                                                                                                                       left_gifti_sphere)
        make_surfaces_right = '%s;export PATH="/freesurfer/bin:$PATH";export PATH="/anaconda3/bin:$PATH";FSLDIR=/fsl;. ${FSLDIR}/etc/fslconf/fsl.sh;PATH=${FSLDIR}/bin:${PATH};export FSLDIR PATH;%s -freesurfer-resample-prep %s %s %s %s %s %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_shortcuts'),
                                                                                                                                                                                                                                                        right_fs_white, right_fs_pial,
                                                                                                                                                                                                                                                        right_fs_sphere, right_new_sphere,
                                                                                                                                                                                                                                                        right_midthickness_current_out,
                                                                                                                                                                                                                                                        right_midthickness_new_out,
                                                                                                                                                                                                                                                        right_gifti_sphere) 
        os.system(make_surfaces_left)
        os.system(make_surfaces_right)
        
        # Make gifti maps
        fs_gifti_left
        left_gifti_sphere
        left_new_sphere
        metric_out_left = os.path.join(output_path, 'fs_LR.L.%s_%s.func.gii' % (resolution, left_name))
        left_midthickness_current_out
        left_midthickness_new_out
        
        fs_gifti_right
        right_gifti_sphere
        right_new_sphere
        metric_out_right = os.path.join(output_path, 'fs_LR.R.%s_%s.func.gii' % (resolution, right_name)) 
        right_midthickness_current_out
        right_midthickness_new_out
        
        map_surfaces_left = '%s;%s -metric-resample %s %s %s ADAP_BARY_AREA %s -area-surfs %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_command'),
                                                                                                     fs_gifti_left, left_gifti_sphere,
                                                                                                     left_new_sphere, metric_out_left,
                                                                                                     left_midthickness_current_out,
                                                                                                     left_midthickness_new_out)
        map_surfaces_right = '%s;%s -metric-resample %s %s %s ADAP_BARY_AREA %s -area-surfs %s %s' % (freesurfer_environment_path, os.path.join(workbench_path, 'wb_command'),
                                                                                                      fs_gifti_right, right_gifti_sphere,
                                                                                                      right_new_sphere, metric_out_right,
                                                                                                      right_midthickness_current_out,
                                                                                                      right_midthickness_new_out)        
        os.system(map_surfaces_left)
        os.system(map_surfaces_right)
 
    # Load the files and modify metadata for easy wb_view loading
    metric_out_left_loaded = nb.load(metric_out_left)
    metric_out_right_loaded = nb.load(metric_out_right)
    
    metric_out_left_loaded.meta.data.pop(0)
    metric_out_right_loaded.meta.data.pop(0)
    metric_out_left_loaded.meta.data.insert(0, nb.gifti.GiftiNVPairs('AnatomicalStructurePrimary', 'CortexLeft'))
    metric_out_right_loaded.meta.data.insert(0, nb.gifti.GiftiNVPairs('AnatomicalStructurePrimary', 'CortexRight'))

    # Save the final folders
    nb.save(metric_out_left_loaded, metric_out_left)
    nb.save(metric_out_right_loaded, metric_out_right)       
   
    return(metric_out_left, metric_out_right)
