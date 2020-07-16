import os

def map_vol2cifti(input_volume, freesurfer_subject_dir, subject_name, intermediate_folder, output_folder, freesurfer_license_file, freesurfer_environment_path='', fsl_environment_path='', run_ciftify_recon_all = True):

    '''
    This function uses ciftify package for python to create a HCP like directory
    from recon-all folder. Then, it uses this directory to map volumetric 
    nifti images to CIFTI FSLR 32k surface.
    
    Required software:
        - Python 3 (Might work alright with python 2 as well, but not tested)
        - Freesurfer
        - FSL
    
    Required python packages:
        - ciftify
        (can be installed by calling "pip install ciftify" from a terminal 
         without the quotation marks.)
    
    Inputs:
        - input_volume = Input volume folder
        - freesurfer_subject_dir = Path to freesurfer subjects folder 
        - subject_name = Name of the subject. Should match the recon-all folder
          for that subject in your Freesurfer subject's folder.
        - intermediate_folder = Path to a folder where the intermediate files
          will be saved.
        - output_folder = Path to a folder where the outputs will be saved
        - freesurfer_license_file = License .txt file for Freesurfer.
        - freesurfer_environment_path = Path to Freesurfer bin folder. Don't
          need to set this if you alrady set path to Freesurfer and call it 
          from your terminal.
        - fsl_environment_path = Path to main FSL direcotry (not the bin). Used
          to find the standard atlases in the directory.
        - run_ciftify_recon_all = Set this to True if you are running this 
          script for the first time for your subject. This creates the HCP like
          directory. If you already ciftified an image for the same subject 
          before and created the HCP like directory, point this flag to your
          ciftify work directory path (e.g Users/Desktop/myCiftifySubjects)
    Outputs:
        Output is a cifti file and diagnostic images.
    '''

    # Get the fmri-name
    # Strip the .nii.gz get the image name
    fmri_name = os.path.split(input_volume)[1]
    if input_volume[-3:] == '.gz':
        task_name = fmri_name[:-7]
    elif input_volume[-3:] == 'nii':
        task_name = fmri_name[:-4]
    else:
        raise RuntimeError('This is not a compatible mri image extention')    

    if run_ciftify_recon_all == True:
        # Run ciftify recon-all
        ciftify_work_dir = '%s/hcp_workdir/' % intermediate_folder
        os.system('mkdir %s' % ciftify_work_dir)
        ciftify_recon_run = 'export PATH="%s:$PATH";FSLDIR=%s;. ${FSLDIR}/etc/fslconf/fsl.sh;PATH=${FSLDIR}/bin:${PATH};export FSLDIR PATH;ciftify_recon_all --ciftify-work-dir %s --fs-subjects-dir %s --surf-reg FS --fs-license %s --n_cpus 2 --verbose %s' % (freesurfer_environment_path, 
                                                                                                                                                                                                                                                                  fsl_environment_path, ciftify_work_dir, 
                                                                                                                                                                                                                                                                  freesurfer_subject_dir, freesurfer_license_file,
                                                                                                                                                                                                                                                                  subject_name)
        os.system(ciftify_recon_run)
    else:
        ciftify_work_dir = run_ciftify_recon_all

    # Run ciftify and map to cifti FSLR
    ciftify_dtseries_run = 'export PATH="%s:$PATH";FSLDIR=%s;. ${FSLDIR}/etc/fslconf/fsl.sh;PATH=${FSLDIR}/bin:${PATH};export FSLDIR PATH;ciftify_subject_fmri --surf-reg FS --ciftify-work-dir %s %s %s %s -v' % (freesurfer_environment_path, fsl_environment_path, ciftify_work_dir, input_volume, subject_name, task_name)
    os.system(ciftify_dtseries_run)
    os.system('cp %s %s/' % (os.path.join(ciftify_work_dir, subject_name, 'MNINonLinear', 'Results', task_name, '%s_Atlas_s0.dtseries.nii' % task_name), output_folder))
    ciftify_visualization_command = 'export PATH="%s:$PATH";FSLDIR=%s;. ${FSLDIR}/etc/fslconf/fsl.sh;PATH=${FSLDIR}/bin:${PATH};export FSLDIR PATH;cifti_vis_fmri subject --ciftify-work-dir %s %s %s' % (freesurfer_environment_path, fsl_environment_path, ciftify_work_dir, task_name, subject_name)
    os.system(ciftify_visualization_command)
    
    return (ciftify_work_dir)