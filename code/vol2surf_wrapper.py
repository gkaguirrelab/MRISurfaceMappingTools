import os
from map_vol2fs import map_vol2fs
from map_fs2gifti import map_fs2gifti
from map_vol2cifti import map_vol2cifti

'''
This is a script to run vol2surf function. Outputs surface files in cifti and
gifti FSLR_32k, and MGZ files in native FS and template space.
'''

############################ Set paths here ##################################

# Path to the input image. Specify path in square paranthesis. You can specify
# multiple paths by separating them with commas. However, the images should
# belong to the same subject as we only specify one recon-all folder.
input_volume = ['']

# Path to a location where the outputs will be saved. The wrapper creates 
# folders for each input image in this path
output_path = '/home/ozzy/Desktop/vol2surf_results'

# Path to a folder where the intermediate files will be saved. The script 
# creates folders for each input image 
intermediate_folder = '/tmp/temporary_vol2suf_folders'

# Freesurfer subjects directory and subject folder name in that directory 
freesurfer_license_file = '/home/ozzy/freesurfer/license.txt'
freesurfer_subject_dir = '/home/ozzy/freesurfer/subjects'
subject_name = 'gka03'

# Standard_mesh_atlases folder. Can be found in the utilities folder of the repo
standard_mesh_atlases_folder = '/home/ozzy/Documents/MATLAB/projects/MRISurfaceMappingTools/code/utilities/standard_mesh_atlases.zip'

# Configurations
output_freesurfer_template = 'fsaverage'
output_cifti_resolution = '32k'

# If you don't already have the HCP style directory set this to True. The script
# will generate it. Otherwise, point this flag to the path where the HCP dir is
# located
run_ciftify_recon_all = True 

# Set paths to software we need if you already didn't set environment paths 
# to them before. If you can call Freesurfer, workbench and FSL from your
# terminal, leave these empty 
freesurfer_environment_path = '' 
fsl_environment_path = ''
workbench_path = ''

##############################################################################
# Process the images 
recon_all_folder = os.path.join(freesurfer_subject_dir, subject_name)

for image in input_volume:
    # Get the fmri-name
    # Strip the .nii.gz get the image name
    image_name_with_extension = os.path.split(image)[1]
    if input_volume[-3:] == '.gz':
        image_name = image_name_with_extension[:-7]
    elif input_volume[-3:] == 'nii':
        image_name = image_name_with_extension[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention') 
    
    # Create specific folders in the main output folder 
    subject_specific_output_folder = os.path.join(output_path, image_name)
    subject_specific_intermediate_folder = os.path.join(intermediate_folder, image_name)
    freesurfer_results_folder = os.path.join(subject_specific_output_folder, 'freesurfer')
    freesurfer_native_output_path = os.path.join(freesurfer_results_folder, 'native')
    freesurfer_standard_output_path = os.path.join(freesurfer_results_folder, 'standard')
    gifti_results_folder = os.path.join(subject_specific_output_folder, 'giftiFSLR')
    cifti_results_folder = os.path.join(subject_specific_output_folder, 'ciftiFSLR')
    os.system('mkdir %s %s %s %s %s %s %s' % (subject_specific_output_folder, subject_specific_intermediate_folder, 
                                              freesurfer_results_folder, freesurfer_native_output_path, 
                                              freesurfer_standard_output_path, 
                                              gifti_results_folder, cifti_results_folder))
    
    native_left, native_right, fsaverage_left, fsaverage_right = map_vol2fs(image, subject_name, freesurfer_native_output_path, freesurfer_standard_output_path, output_freesurfer_template=output_freesurfer_template, freesurfer_environment_path=freesurfer_environment_path)
    map_fs2gifti(native_left, native_right, recon_all_folder, standard_mesh_atlases_folder, subject_specific_intermediate_folder, gifti_results_folder, source_space='native', resolution=output_cifti_resolution, workbench_path=workbench_path, freesurfer_environment_path=freesurfer_environment_path)
    if output_freesurfer_template == 'fsaverage':
        map_fs2gifti(fsaverage_left, fsaverage_right, recon_all_folder, standard_mesh_atlases_folder, subject_specific_intermediate_folder, gifti_results_folder, source_space='fsaverage', resolution=output_cifti_resolution, workbench_path=workbench_path, freesurfer_environment_path=freesurfer_environment_path)
    ciftify_work_dir = map_vol2cifti(image, freesurfer_subject_dir, subject_name, subject_specific_intermediate_folder, cifti_results_folder, freesurfer_license_file, freesurfer_environment_path=freesurfer_environment_path, fsl_environment_path=fsl_environment_path, run_ciftify_recon_all=run_ciftify_recon_all)
    
    # Set path to the ciftify directory so we don't run ciftify recon-all for each image.
    run_ciftify_recon_all = ciftify_work_dir
