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
                    help='The base directory for the SED models')
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
        template_name = template #os.path.join(args.base_dir, 'param_files', template)
        outfile_name = f'{args.template_dir}/{os.path.basename(template).replace('template', id)}' #os.path.join(args.base_dir, 'param_files',
        #                            template.replace('template', objid))
        replacements = {'ID': str(id)}

        with open(template_name) as infile, open(outfile_name, 'w') as outfile:
            
            # For each line in the input template file
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)

'''
files = glob.glob(f'{args.base_dir}/{os.path.basename(args.catalog_file).split('.')[0]}_*.fits')

with zipfile.ZipFile(f'{os.path.basename(args.catalog_file).split('.')[0]}_individual.zip', mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

    for file in files:

        # Check if it's a file (glob can return directories if pattern matches)
        if os.path.isfile(file):

            # Optional: use os.path.relpath to store relative paths in the archive
            # instead of absolute paths
            relative_path = os.path.relpath(file, args.base_dir)
            zf.write(file, relative_path)

            # Delete the file
            os.remove(file)

for template in args.template_files:

    files = glob.glob(f'{args.base_dir}/[!template]*{template[8:]}')

    with zipfile.ZipFile(f'{args.base_dir}/{os.path.basename(template).split('.')[0]}_individual.zip', mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

        for file in files:

            # Check if it's a file (glob can return directories if pattern matches)
            if os.path.isfile(file):

                # Optional: use os.path.relpath to store relative paths in the archive
                # instead of absolute paths
                relative_path = os.path.relpath(file, args.base_dir)
                zf.write(file, relative_path)

                # Delete the file
                os.remove(file)
'''