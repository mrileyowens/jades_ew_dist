# A file to separate the Endsley et al. (2024) photometric dropout catalog into two separate catalogs, based on which filter the break is in

import os

import numpy as np

from astropy.io import fits
from astropy.table import Table

# Set common directories
home = os.getcwd()
data = f'{home}/data'

# The file path to the combined catalog
catalog = f'{data}/JADES_z6to9LBGcatalog_Endsley2024.fits'

# Open the F775W and F090W dropout catalog from Endsley et al. (2024)
with fits.open(catalog) as hdul:

    # Format the catalog's data as a table
    t = Table(hdul[1].data)

    # For each dropout filter
    for filter in ['F775W', 'F090W']:

        # Make a mask for the dropout filter in the table
        mask = t['dropoutType'] == filter

        # Mask the table to just select the dropout galaxies in the given filter
        t_new = t[mask]

        # Update the size of the second axis in the header
        header = hdul[1].header
        header['NAXIS2'] = np.sum(mask)

        # Create a new HDU from the masked table and replace the existing HDU
        new_hdu = fits.BinTableHDU(data=t_new.as_array(), header=header)
        hdul[1] = new_hdu

        # Save the pared down catalog
        hdul.writeto(f'{catalog.split('.')[0]}_{filter.lower()}_dropouts.fits', overwrite=True)