import os 
import nibabel as nb

def map_vol2fs(image_to_interpolate, template_to_interpolate, output_path, freesurfer_subjects_dir, recon_all_folder, input_is_MNI=True, custom_recon_all=False):
    
    '''
    Maps volume image to freesurfer fsaverage or a custom surface
    
    Inputs:
        - image_to_interpolate = The main moving image to interpolate to target
        surface.
        - template_to_interpolate = High-res template that is in the same 
        space with the image_to_interpolate. It is not required if you are not
        mapping R2 maps, but strongly recommended. 'NA' can be passed instead 
        if it will not be used.
        - output_path = Path to output files
        - from_mni_to_fsaverage = If image_to_interpolate is in MNI152 space
        and you want to map to fsaverage space, set this to true. Extremely 
        speeds up the process.
        - recon_all_folder = Set this to a freesurfer recon-all folder. This
        is the target of the surface mapping. If you want to map to fsaverage
        set this to freesurfer-dir/subjects/fsaverage?
        - freesurfer subject dir - The folder containing all the freesurfer subjects
    
    Outputs:
        The main output folder contains the final left/right surface images and
        a folder for intermediate files. These intermediate files are:
            
        - register.dat = Identity registeration file used for surface mapping
        - <scan_name>0GenericAffine.mat = Linear matrix between the template and 
        the surface
        - <scan_name>1Warp.nii.gz = Warp field of template and surface registration
        - <scan_name>1InverseWarp.nii.gz = Inverse of the warp mentioned above
        - <scan_name>Warped.nii.gz = Product after applying the generic and warp
        field to the template image
        - <scan_name>InverseWarped.nii.gz = Product after applying the inverse
        of the warp field to the template image        
        - <scan_name>finalInterpolatedImage.nii.gz = Final image that is 
        in the space of the volumetric image which is the base for the provided
        surface target      
    '''
    
    # If template is not passed, use the main image for the operations
    if template_to_interpolate == 'NA':
        template_to_interpolate = image_to_interpolate
    loaded_image = nb.load(image_to_interpolate)
    image_dimension = len(loaded_image.shape)
    
    # Strip the whole path and extention and get the image name
    base = os.path.basename(template_to_interpolate)
    if 'nii' in base:
        image_name = os.path.splitext(base)[0][:-4]
    else:
        image_name = os.path.splitext(base)[0]     
    
    # Convert dimension to ANTs value
    if image_dimension == 3:
        image_type = '0' # scalar
    if image_dimension == 4:
        image_type = '3' # time-series
       
    # Create the main output folder at the specified path
    main_output_folder = os.path.join(output_path, 'fs-surf')
    os.system('mkdir %s' % main_output_folder)
    
    # Set the output image names
    right_hemi_output_path_gifti = os.path.join(main_output_folder, image_name + '-rh.gii')
    left_hemi_output_path_gifti = os.path.join(main_output_folder, image_name + '-lh.gii')
    right_hemi_output_path_mgz = os.path.join(main_output_folder, image_name + '-rh.mgz')
    left_hemi_output_path_mgz = os.path.join(main_output_folder, image_name + '-lh.mgz')   
    
    # If interpolating from mni to fsaverage, life is easy    
    if input_is_MNI and custom_recon_all==False:
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --src %s --out %s --hemi rh --mni152reg' % (freesurfer_subjects_dir, image_to_interpolate, right_hemi_output_path_gifti))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --src %s --out %s --hemi lh --mni152reg' % (freesurfer_subjects_dir, image_to_interpolate, left_hemi_output_path_gifti))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --src %s --out %s --hemi rh --mni152reg' % (freesurfer_subjects_dir, image_to_interpolate, right_hemi_output_path_mgz))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --src %s --out %s --hemi lh --mni152reg' % (freesurfer_subjects_dir, image_to_interpolate, left_hemi_output_path_mgz))
        
    # Otherwise we need to do a nonlinear warp to the volume that is the base 
    # of the target surface
    if custom_recon_all==True:
 
        # Create a folder for intermediate files 
        intermediate_files = os.path.join(output_path, 'intermediate_folders')
        os.system('mkdir %s' % intermediate_files)
        
        # Get some paths for non-linear registration and run it 
        target = os.path.join(recon_all_folder, 'mri', 'T1.mgz')
        output_stem_name = os.path.join(intermediate_files, 'volume2orig')
        os.system('export ANTSPATH=/usr/lib/ants/;export PATH=${ANTSPATH}:$PATH;/usr/lib/ants/antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s -n 6' % (target, template_to_interpolate, output_stem_name))
        warp_matrix = output_stem_name + '1Warp.nii.gz'
        linear_matrix = output_stem_name + '0GenericAffine.mat'
       
        # Apply warp to the image 
        final_warped_image = output_stem_name + '_finalInterpolatedImage.nii.gz'
        os.system('export ANTSPATH=/usr/lib/ants/;export PATH=${ANTSPATH}:$PATH;/usr/lib/ants/antsApplyTransforms -e %s -i %s -r %s -t %s -t %s -o %s' % (image_type, image_to_interpolate,
                                                                                target, warp_matrix, linear_matrix,
                                                                                final_warped_image))
                
        # Create a register.dat from the FSL identity matrix
        fsl_identity_matrix = os.path.join(os.popen('echo $FSLDIR').read().strip(), 'etc', 'flirtsch', 'ident.mat')
        registerdat_path = os.path.join(intermediate_files, 'register.dat')
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/tkregister2 --mov %s --fsl %s --targ %s --noedit --reg %s' % (freesurfer_subjects_dir, final_warped_image, fsl_identity_matrix,
                                                                                                                                                                                                                                 final_warped_image, registerdat_path))
        
        # Create the final surface maps 
        subject_dir = os.path.dirname(recon_all_folder)
        subject_name = os.path.basename(recon_all_folder)     
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --mov %s --ref %s --reg %s --sd %s --srcsubject %s --hemi rh --o %s' % (freesurfer_subjects_dir, final_warped_image, final_warped_image, 
                                                                                                                                                                                                                                                        registerdat_path, subject_dir,
                                                                                                                                                                                                                                                        subject_name, right_hemi_output_path_gifti))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --mov %s --ref %s --reg %s --sd %s --srcsubject %s --hemi lh --o %s' % (freesurfer_subjects_dir, final_warped_image, final_warped_image,
                                                                                                                                                                                                                                                        registerdat_path, subject_dir,
                                                                                                                                                                                                                                                        subject_name, left_hemi_output_path_gifti))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --mov %s --ref %s --reg %s --sd %s --srcsubject %s --hemi rh --o %s' % (freesurfer_subjects_dir, final_warped_image, final_warped_image, 
                                                                                                                                                                                                                                                        registerdat_path, subject_dir,
                                                                                                                                                                                                                                                        subject_name, right_hemi_output_path_mgz))
        os.system('export FREESURFER_HOME=/freesurfer;/bin/bash -c \'source $FREESURFER_HOME/FreeSurferEnv.sh &>/dev/null\';export SUBJECTS_DIR=%s;/freesurfer/bin/mri_vol2surf --mov %s --ref %s --reg %s --sd %s --srcsubject %s --hemi lh --o %s' % (freesurfer_subjects_dir, final_warped_image, final_warped_image,
                                                                                                                                                                                                                                                        registerdat_path, subject_dir,
                                                                                                                                                                                                                                                        subject_name, left_hemi_output_path_mgz))
   
    return (left_hemi_output_path_gifti, right_hemi_output_path_gifti, left_hemi_output_path_mgz, right_hemi_output_path_mgz)
