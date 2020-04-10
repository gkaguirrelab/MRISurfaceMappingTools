import os
import nibabel as nb
import numpy as np

def map_gifti2cifti(gifti_left, gifti_right, standard_mesh_atlases_folder, tr, output_path):
 
    # Create a subfolder for cifti
    main_output_folder = os.path.join(output_path, 'cifti')
    
    # Load left and right hemispheres
    gifti_left_loaded = nb.load(gifti_left)
    gifti_right_loaded = nb.load(gifti_right)
    
    # Load the dtseries template 
    dtseries_template = nb.load(os.path.join(standard_mesh_atlases_folder, 'dtseries_atlas_FSLR32k', 'cifti_Atlas.dtseries.nii'))
    header = dtseries_template.header.copy()
    filemap = dtseries_template.file_map
    
    # Load vertex atleses combine and find the vertices that don't belong (zeros)
    left_atlas = nb.load(os.path.join(standard_mesh_atlases_folder, 'dtseries_atlas_FSLR32k', 'L.atlasroi.32k_fs_LR.shape.gii'))
    right_atlas = nb.load(os.path.join(standard_mesh_atlases_folder, 'dtseries_atlas_FSLR32k', 'R.atlasroi.32k_fs_LR.shape.gii')) 
    atlas_combined = np.concatenate((left_atlas.darrays[0].data, right_atlas.darrays[0].data))
    zero_indices = np.argwhere(atlas_combined<1)
    
    # Get some length variables
    len32 = 91282
    timeseries_length = len(gifti_left_loaded.darrays)
    
    # Modify the header 
    header.matrix._mims[0].number_of_series_points = timeseries_length
    header.matrix._mims[0].series_step = tr
    
    # Loop through the time series, combine the hemispheres, remove zero values
    # using the atlases and add subcortex values to the array 
    final_array_set = np.zeros((timeseries_length, len32))
    for i in range(timeseries_length):
        combined = np.concatenate((gifti_left_loaded.darrays[i].data, gifti_right_loaded.darrays[i].data)) 
        cleaned = np.delete(combined, zero_indices)        
        length_dif = len32 - len(cleaned)
        subcortex = np.zeros(length_dif)
        final_matrix = np.concatenate((cleaned, subcortex))
        final_array_set[i,:] = final_matrix       
    newcifti = nb.Cifti2Image(final_array_set, header, file_map=filemap)
    final_dtseries = os.path.join(main_output_folder, 'fs_LR-interpolated.32k.dtseries.nii')
    nb.save(newcifti, final_dtseries)    
    
    return(final_dtseries)
