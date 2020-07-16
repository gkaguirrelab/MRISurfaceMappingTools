# MRISurfaceMappingTools
Python repo that contains code for mapping volumetric images to surface. This repo also contains the folders for vol2surf gear.

# Software Requirements
- Python3 (Python2 should also work but not tested)
- FSL 
- Freesurfer
- Connectome workbench

# Python package requirements
- nibabel
- ciftify

# Function overview
- map_vol2fs.py - Maps volumetric time-series or R2 images to native or template Freesurfer surfaces.
- map_fs2gifti.py - Maps Freesurfer time-series or R2 surfaces to different resolution FSLR gifti surfaces.
- map_vol2cifti.py - Maps volumetric time-series or R2 images to HCP-FSLR CIFTI surface.
- vol2surf_wrapper.py - Takes volumetric images and runs all three functions specified above to create gifti, freesurfer, and cifti images.
