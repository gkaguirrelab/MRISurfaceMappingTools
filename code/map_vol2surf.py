import os 

def map_vol2surf(image_to_interpolate, image_dimension, template_to_interpolate, output_path, from_mni_to_fsaverage=True, recon_all_folder='NA'):
    
    '''
    Maps volume image to freesurfer fsaverage or a custom surface
    
    Inputs:
        - image_to_interpolate = The main moving image to interpolate to target
        surface.
        - image_dimension = Dimension of the image_to_interpolate (e.g. 3 for 
        single volume or 4 for time series)
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
    main_output_folder = os.path.join(output_path, 'vol2surf_results')
    os.system(f'mkdir {main_output_folder}')
    
    # Set the output image names
    right_hemi_output_path_gifti = os.path.join(main_output_folder, image_name + '-rh.gii')
    left_hemi_output_path_gifti = os.path.join(main_output_folder, image_name + '-lh.gii')
    right_hemi_output_path_mgz = os.path.join(main_output_folder, image_name + '-rh.mgz')
    left_hemi_output_path_mgz = os.path.join(main_output_folder, image_name + '-lh.mgz')   
    
    # If interpolating from mni to fsaverage, life is easy    
    if from_mni_to_fsaverage:
        if recon_all_folder != 'NA':
            print('Warning: You specified a recon all folder but also using the from_mni_to_fsaverage option. Assuming that you are using the MNI template and interpolating to fsaverage. Revise the flags if this is not what you want')    
        os.system(f'mri_vol2surf --src {image_to_interpolate} --out {right_hemi_output_path_gifti} --hemi rh --mni152reg')
        os.system(f'mri_vol2surf --src {image_to_interpolate} --out {left_hemi_output_path_gifti} --hemi lh --mni152reg')
        os.system(f'mri_vol2surf --src {image_to_interpolate} --out {right_hemi_output_path_mgz} --hemi rh --mni152reg')
        os.system(f'mri_vol2surf --src {image_to_interpolate} --out {left_hemi_output_path_mgz} --hemi lh --mni152reg')
        
    # Otherwise we need to do a nonlinear warp to the volume that is the base 
    # of the target surface
    if not from_mni_to_fsaverage:
        if recon_all_folder == 'NA':
            raise RuntimeError('You have not specified a recon all folder') 
            
        # Create a folder for intermediate files 
        intermediate_files = os.path.join(main_output_folder, 'intermediate_folders')
        os.system(f'mkdir {intermediate_files}')
        
        # Get some paths for non-linear registration and run it 
        target = os.path.join(recon_all_folder, 'mri', 'T1.mgz')
        output_stem_name = os.path.join(intermediate_files, 'volume2orig')
        #os.system(f'antsRegistrationSyNQuick.sh -d 3 -f {target} -m {template_to_interpolate} -o {output_stem_name} -n 6')
        warp_matrix = output_stem_name + '1Warp.nii.gz'
        linear_matrix = output_stem_name + '0GenericAffine.mat'
        final_warped_template = output_stem_name + 'Warped.nii.gz'
       
        # Apply warp to the image 
        final_warped_image = output_stem_name + '_finalInterpolatedImage.nii.gz'
        os.system(f'antsApplyTransforms -e {image_type} -i {image_to_interpolate} -r {target} -t {warp_matrix} -t {linear_matrix} -o {final_warped_image}')
                
        # Create a register.dat from the FSL identity matrix
        fsl_identity_matrix = os.path.join(os.popen('echo $FSLDIR').read().strip(), 'etc', 'flirtsch', 'ident.mat')
        registerdat_path = os.path.join(intermediate_files, 'register.dat')
        os.system(f'tkregister2 --mov {final_warped_image} --fsl {fsl_identity_matrix} --targ {final_warped_image} --noedit --reg {registerdat_path}')
        
        # Create the final surface maps 
        subject_dir = os.path.dirname(recon_all_folder)
        subject_name = os.path.basename(recon_all_folder)     
        os.system(f'mri_vol2surf --mov {final_warped_image} --ref {final_warped_image} --reg {registerdat_path} --sd {subject_dir} --srcsubject {subject_name} --hemi rh --o {right_hemi_output_path_gifti}')
        os.system(f'mri_vol2surf --mov {final_warped_image} --ref {final_warped_image} --reg {registerdat_path} --sd {subject_dir} --srcsubject {subject_name} --hemi lh --o {left_hemi_output_path_gifti}')
        os.system(f'mri_vol2surf --mov {final_warped_image} --ref {final_warped_image} --reg {registerdat_path} --sd {subject_dir} --srcsubject {subject_name} --hemi rh --o {right_hemi_output_path_mgz}')
        os.system(f'mri_vol2surf --mov {final_warped_image} --ref {final_warped_image} --reg {registerdat_path} --sd {subject_dir} --srcsubject {subject_name} --hemi lh --o {left_hemi_output_path_mgz}')       
