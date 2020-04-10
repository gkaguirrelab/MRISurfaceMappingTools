import os 
import nibabel as nb

def map_fs2gifti(fs_gifti_left, fs_gifti_right, standard_mesh_atlases_folder, output_path, resolution='32k'):
    
    '''
    Maps gifti converted fsaverage surface to FS_LR gifti
    
    Inputs:
        - fs_gifti_left = fsaverage left hemisphere. Needs to be gifti. 
        interpolate_vol2surf outputs gifti fsaverage images that can be used 
        here.
        - fs_gifti_right = fsaverage right hemishpehere. Needs to be gifti
        - standard_mesh_atlases_folder = Path to the folder containing fs/FSLR
        calculations
        - output_path = Location to save the outputs
        - resolution = cifti resolution. Default 32k
    '''
    
    # Set paths to the files required for the operations 
    current_sphere_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                        'fsaverage_std_sphere.L.164k_fsavg_L.surf.gii')
    current_sphere_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                        'fsaverage_std_sphere.R.164k_fsavg_R.surf.gii')    
    new_sphere_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                        f'fs_LR-deformed_to-fsaverage.L.sphere.{resolution}_fs_LR.surf.gii') 
    new_sphere_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                        f'fs_LR-deformed_to-fsaverage.R.sphere.{resolution}_fs_LR.surf.gii')     
    metric_out_left = os.path.join(output_path, f'fs_LR-interpolated.L.{resolution}.func.gii') 
    metric_out_right = os.path.join(output_path, f'fs_LR-interpolated.R.{resolution}.func.gii')    
    current_area_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                         f'fsaverage.L.midthickness_va_avg.164k_fsavg_L.shape.gii') 
    current_area_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                         f'fsaverage.R.midthickness_va_avg.164k_fsavg_R.shape.gii')     
    new_area_left = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                         f'fs_LR.L.midthickness_va_avg.{resolution}_fs_LR.shape.gii')    
    new_area_right = os.path.join(standard_mesh_atlases_folder, 'resample_fsaverage',
                                         f'fs_LR.R.midthickness_va_avg.{resolution}_fs_LR.shape.gii')     
   
    # Assemble the run commands and call  
    wb_run_left_string = f'wb_command -metric-resample {fs_gifti_left} {current_sphere_left} {new_sphere_left} ADAP_BARY_AREA {metric_out_left} -area-metrics {current_area_left} {new_area_left}'
    wb_run_right_string = f'wb_command -metric-resample {fs_gifti_right} {current_sphere_right} {new_sphere_right} ADAP_BARY_AREA {metric_out_right} -area-metrics {current_area_right} {new_area_right}'   
    
    os.system(wb_run_left_string)
    os.system(wb_run_right_string)
    
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
