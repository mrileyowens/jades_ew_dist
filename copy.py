# Authors: Lily Whitler, M. Riley Owens (GitHub: mrileyowens)

# This is a helper file for preparing parallel computations on HPC systems with BEAGLE. This file is best used by executing it locally, and then uploading the outputs to the HPC environment and unzipping them.

import os
import glob
import argparse
import shutil
import zipfile

import numpy as np

from astropy.io import fits
from astropy.table import Table

# Create a command line parser
parser = argparse.ArgumentParser()
parser.add_argument('--base_dir', '-d', type=str, default='.',
                    help='The base directory for the parallelized photometry')
parser.add_argument('--catalog_file', '-catalog', type=str, 
                    help='The name of the catalog with all the object IDs')
parser.add_argument('--id_column', '-id', type=str, default='ID', 
                    help='The name of the ID column in the catalog')
parser.add_argument('--id_dir', '-id_dir', type=str, default='.', 
                    help='The base directory to save the list of object IDs')
parser.add_argument('--template_files', '-templates', '-template', nargs='*',
                    help='The names of the template files to copy')
parser.add_argument('--template_dir', '-template_dir', type=str, default='.', 
                    help='The base directory to save the per-object template files')
args = parser.parse_args()

# Get the object IDs in the catalog
ids = fits.open(args.catalog_file)[1].data[args.id_column]

# Save the object IDs to a .txt file, which will be used in the parallelization
np.savetxt(f'{args.id_dir}/{os.path.basename(args.catalog_file).split('.')[0]}_ids.txt', ids, fmt='%s')

# For each object ID
for id in ids:

    # Open the photometric catalog
    with fits.open(args.catalog_file) as hdul:

        # Make a new table from the catalog's data
        t = Table(hdul[1].data)

        # Mask the table so that only the given object remains
        mask = t[f'{args.id_column}'] == id
        t_id = t[mask]

        # Edit the NAXIS2 keycard to reflect that the saved file will have just 1 object
        header = hdul[1].header
        header['NAXIS2'] = 1

        # Create a new HDU from the masked table and the original table's header
        new_hdu = fits.BinTableHDU(data=t_id.as_array(), header=header)
        hdul[1] = new_hdu

        # Write the object to a dedicated FITS file
        hdul.writeto(f'{args.base_dir}/{os.path.basename(args.catalog_file).split('.')[0]}_{id}.fits', overwrite=True)

    # For each template file
    for template in args.template_files:

        # Get the name of the input and output template file
        template_name = template
        outfile_name = f'{args.template_dir}/{os.path.basename(template).replace('template', id)}'
        
        # Make a dictionary of the string to replace in the template file with the replacement as a key
        replacements = {'ID': str(id)}

        # Open the template and output files
        with open(template_name) as infile, open(outfile_name, 'w') as outfile:
            
            # For each line in the input template file
            for line in infile:

                # For each string to replace with its replacement
                for src, target in replacements.items():

                    # Replace the target string with the replacement string in that line
                    line = line.replace(src, target)

                # Write the line to the output file
                outfile.write(line)