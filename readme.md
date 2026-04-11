Things to do:

- Calculate the prior EW distributions with different choices for a rest-UV filter
- Confirm the version of BEAGLE that Ryan used and compare it to mine
- Add a note in the priors table explaining what the dust-metal mass ratio is
- Do more investigation about the IGM absorption law in BEAGLE; doesn't appear in the docs
- Add information about the EW bins
- Add more details about implementing the Bayesian inference
- Clarify what BEAGLE means by "Inoue" in the priors table
- Clarify the "dependent" description for the ISM metallicity in the priors table, and the "NA" for E24, who equivocate it with the stellar metallicity?
- Add to the priors table about the adopted IMF / models, and then add to the "different parameters" discussion if necessary
- Update the discussion about $M_\text{UV}$ biases with results from the no-Lya fits
- Change the EW comparison to instead use probability-weighted percentiles
- Reach out to Lily / Zuyi about metallicities in BEAGLE

# Overview and methodology

This repository is my attempt to replicate the [O III] + H-beta EW distributions inferred by [Endsley et al. (2024)](https://doi.org/10.1093/mnras/stae1857) (hereafter E24) from $z\sim6$ F775W dropout galaxies in the JADES fields. An explanation of the repository's content follows.

At the core of the repository is the photometric catalog of E24: `JADES_z6to9LBGcatalog_Endsley2024.fits`, located in the `data` folder, which contains data products not created by the code in this repository, or which are immediately derivative thereof. That catalog includes both F775W and F090W dropout galaxies. The current interest of this repository is just the F775W dropout galaxies, so `split.py` splits the parent joint catalog into two: one with just the F775W dropout galaxies (`JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts.fits`), and another with just the F090W dropout galaxies (`JADES_z6to9LBGcatalog_Endsley2024_f090w_dropouts.fits`). `split.py` preserves the original FITS headers, apart from updating the key stating the number of galaxies in a catalog.

With the photometry of the F775W dropout galaxies in hand, the next step is to fit the photometry with BEAGLE, in order to estimate the [O III] + H-beta EWs of the galaxies. Although E24 employed 3 different SED fitting methods, this work only attempts to reproduce the BEAGLE CSFH SED fitting. The table below summarizes the priors I adopted compared to E24, which are mostly identical.

>| Parameter | This work | E24 |
>| - | - | - |
>| Cosmology | $h=0.7$, $\Omega_\text{M}=0.3$, $\Omega_\Lambda=0.7$ | $h=0.7$, $\Omega_\text{M}=0.3$, $\Omega_\Lambda=0.7$ |
>| SFH | CSFH | CSFH |
>| Redshift | $0\leq z\leq25$ (uniform) | $4\leq z\leq8$ (uniform) |
>| Age $^a$ | $6 \leq \text{log}_{10}(\text{age}) \leq 10.2$ (log-uniform) | $6 \leq \text{log}_{10}(\text{age}) \leq \text{age of the universe}$ (log-uniform) |
>| Mass | $5 \leq \text{log}_{10}(M_\star/\text{M}_\odot) \leq 12$ (log-uniform) | $5 \leq \text{log}_{10}(M_\star/\text{M}_\odot) \leq 12$ (log-uniform) |
>| $V$-band dust optical depth | $-3 \leq \tau_V \leq 0.7$ (log-uniform) | $-3 \leq \tau_V \leq 0.7$ (log-uniform) |
>| Ionization parameter | $-4\leq\text{log}_{10}U\leq-1$ (log-uniform) | $-4\leq\text{log}_{10}U\leq-1$ (log-uniform) |
>| Metallicity | $-2.2\leq\text{log}_{10}(Z/\text{Z}_\odot)\leq-0.3$ (log-uniform) | $-2.2\leq\text{log}_{10}(Z/\text{Z}_\odot)\leq-0.3$ (log-uniform) |
>| Dust law | SMC ([Pei 1992](https://doi.org/10.1086/171637)) | SMC ([Pei 1992](https://doi.org/10.1086/171637)) |
>| IGM absorption law $^b$ | Inoue | [Inoue (2014)](https://doi.org/10.1093/mnras/stu936) |
>| Dust-metal mass ratio $^c$ | $0.1\leq\xi_d\leq0.5$ (uniform) | NA |
>| Interstellar metallicity | dependent | NA |
>
>$^a$ E24 noted that they set the upper bound on the age prior as the age of the universe at the given redshift. I'm not sure if my approach also does this; BEAGLE isn't clear, but my upper prior on the age of $10^{10.2}$ yr is beyond even the current age of the universe, so if BEAGLE does any intelligent inference at all, the behavior should be identical.  
>$^b$ The BEAGLE documentation does not mention IGM absorption at all, even though a IGM absorption model is an accepted parameter in a `.param` file. For this work's fitting, I continued using the "Inoue" argument from `.param` files I inherited, which is presumably the [Inoue (2014)](https://doi.org/10.1093/mnras/stu936) model.  
>$^c$ E24 do not describe any adopted priors for the dust-metal mass ratio, $\xi_d$.
>
>**Table:** BEAGLE priors adopted by this work and E24. E24 noted that they set the upper bound on the age prior as the age of the universe at the given redshift. I'm not sure if my approach also does this; BEAGLE isn't clear, but my upper prior on the age of $10^{10.2}$ yr is beyond even the current age of the universe, so if BEAGLE does any intelligent inference at all, the behavior should be identical.

BEAGLE runs in series on whatever catalog the user tells it to fit. Even on a HPC system, this can be a problem, significantly slowing down the time to a fitted catalog, particularly for catalogs with tens or more of galaxies (278, in this case). One can circumvent this shortcoming by parallelizing the catalog and running many instances of BEAGLE at once. The `copy.py` script does this, making, for each galaxy in the F775W dropout galaxy catalog, (1) an individual FITS file of the galaxy's photometry and (2) a corresponding BEAGLE parameter file for each galaxy, based on a template parameter file, in the `beagle` folder. The script also makes a `.txt` list of the galaxy IDs. 

The `beagle` folder contains all the relevant files necessary to run BEAGLE. Within that folder, `data` contains the individual FITS files of the photometry of each galaxy from the parent catalog, `filters` contains the filter throughput curves (`filters.fits`) and the filter setup information (`*.dat`), `logs` contains output logs from the HPC system (not tracked by the repository), `params` contains the parallelized parameter files of the individual galaxies from the parent catalog, `results` contains the output products from BEAGLE, and `success` contains files tracking if a given BEAGLE fit succeeded, so that it can be refitted if necessary.

To fit a catalog with a given set of model parameters and filters, I use a `*.sh` file in the `beagle` folder. These files automatically submit SLURM jobs based on a corresponding `*.slurm` file for each of the parallelized files of the parent catalog. Upon a successful fit, the SLURM script writes a `success_*` file in the `beagle/success` folder, where the `*` stands for the SLURM array task ID. The `*.sh` file checks for existing `success_*` files and only submits SLURM jobs for those galaxies that do not have a corresponding `success_*` file.

I performed three sets of fits with the priors described above: one with Lya emission, one without Lya emission, and another with *just* the F200W photometry but with Lya emission enabled (shouldn't matter anyways). The third is necessary to probe the priors on the EWs that BEAGLE *can* produce, which I use later to prevent any inferences on the observed EW distributions from being model-driven. E24 does not specify which single filter they used to assess the BEAGLE model priors, only stating they used "a single photometric
data point in the rest-UV." At any rate, F200W is a rest-UV filter at the targeted redshifts. Although E24 is not clear, judging by their SED figures, they did not include Lya emission.

With the above sets of SED fits in hand, it is next necessary to measure the [O III] and H-beta EWs from the posterior model SEDs of each galaxy. Because E24 measured the EW distribution for several $M_\text{UV}$ bins, I first measured the $M_\text{UV}$ of the galaxies from the posterior model SEDs with the `calculate_m_uv()` function in `calculate_ew_distribution.ipynb`. For the two sets of full fits, the function calculates the posterior $M_\text{UV}$ distribution of each galaxy from each posterior model SED, based on the median rest-frame flux density between 1450 $\text{\AA}$ and 1550 $\text{\AA}$. E24 state they computed the $M_\text{UV}$ from "the continuum flux density at 1500 $\text{\AA}$ rest frame using the output redshift and SED posteriors" but do not provide more specifics. The resulting $M_\text{UV}$ posterior distributions are stored, for each of the two sets of full fits, in a `*_m_uv.h5` file in `results/m_uv`, where the `*` matches the set of fits.

The F775W dropout galaxy catalog from E24 also includes a few physical properties measured for each galaxy and their uncertainties (i.e., the 16th and 84th percentiles of the posteriors), including the $M_\text{UV}$. For posterity, I also measured the EW distributions according to the $M_\text{UV}$ bin assignments based on those E24 measurements, so that each galaxy is in the exact same $M_\text{UV}$ bin that E24 would have assigned.

Regardless of the specific method to assign a galaxy to a $M_\text{UV}$ bin, the [O III] and H-beta EW of each galaxy is measured in an identical manner, by `calculate_ew()` and `calculate_ew_m_uv_endsley2024()`, which just differ in $M_\text{UV}$ bin assignments of the saved outputs. In either case, I measured the [O III] and H-beta EW of each galaxy from the posterior model SEDs, following the standard EW equation and assuming a flat continuum based on the median flux density in a given set of continuum bands. The table below summarizes the assumed rest wavelengths of the line and continuum bands.

| Emission line | Line band ($\text{\AA}$) | Continuum band(s) ($\text{\AA}$) |
| - | - | - |
| [O III] 4959, 5007 $\text{\AA}$ | 4954 - 5011 | 4880 - 4930, 5050 - 5100 |
| H-beta | 4856 - 4866 | 4775 - 4825, 4880 - 4930 |

At this stage, both functions also measure, in the same fashion described above, the EWs of the F200W-only SED fits. These come into play later. The EW distributions from each set of posterior model SEDs are sorted into their corresponding $M_\text{UV}$ bin, based on the probability-weighted (where the probabilities come from BEAGLE) median $M_\text{UV}$ of the previously measured $M_\text{UV}$ posterior distributions. The resulting groupings of EW measurements are saved into separate files, depending on the $M_\text{UV}$ bin, in `results/ew` as `*_ews_*.h5`, where the two `*` indicate the $M_\text{UV}$ bin, method to assign the $M_\text{UV}$ bin, fit set, and if it corresponds to the F200W-only fits.

With the EW measurements of the full and F200W-only SED fits in hand, we are prepared to infer the EW distributions. E24 employed a Bayesian approach summarized in the equation below, where the index $i$ is across galaxies and $j$ is across EW bins.

$
\begin{equation}
    P(\theta) \propto \prod_i\left[\sum_j P_{i,j}(\text{EW})P_j(\text{EW}|\theta)\right]
\end{equation}
$

$P(\theta)$ is the probability that the parameter set $\theta$ describes the observations, $P_{i,j}(EW)$ is the probability galaxy $i$ has an EW in bin $j$ (i.e., the corresponding bin in the normalized posterior EW distribution), and $P_j(EW|\theta)$ is the integrated probability of the assumed model EW distribution in bin $j$. The function `calculate_ew_distribution()` implements the above equation and calculates the probabilities associated with 10,000 uniformly randomly sampled sets of parameters describing model EW distributions. Following E24, the model EW distributions are assumed to be Gaussian curves in base-10 logarithmic EW space. The uniform priors on the mean and variance are $\mu = 0-4$ and $\sigma = 0.01 - 2$.

The sampled sets of parameters and associated probabilities are stored in the folder `results/probs` in a file matching `*_probs*.h5`, where the `*` indicate the set of fits, the $M_\text{UV}$ bin, and method to determine the $M_\text{UV}$ bin assignments.

Below are the resulting inferred EW distributions from the sampled model EW distribution parameters and probabilities, split by $M_\text{UV}$ bin and the two sets of BEAGLE fits (with and without Lya). Both sets of fits are generally consistent, but those that include Lya appear more consistent, even if the specific physical properties (especially redshift) of the galaxy are more discrepant. Plotted in dashed lines are the corresponding distributions from E24 for the reported median parameters.

<p float="left" align="middle">
    <img src="figs/ew_distributions.png" width=49%/>
    <img src="figs/ew_distributions_no_lya.png" width=49%/>
    <img src="figs/ew_distributions_m_uv_endsley2024.png" width=49%>
    <img src="figs/ew_distributions_m_uv_endsley2024_no_lya.png" width=49%>
</p>

* table comparing priors *

* discussion about basic properties of my BEAGLE fits vs E24, including a comparison of those with and without Lya *

* discussion about how I measured the EWs from the fits, especially contrasting that the exact methodology of E24 is not clear *

* discussion about how I inferred the EW distributions from the fits *

* discussion about the different inferred EW distributions and how they compare to E24 *

# Why aren't the EW distributions identical?

The EW distributions inferred by E24 and my work here are not identical. In this section, I explore possible explanations for the discrepancy.

### Different BEAGLE parameter files

A low-hanging suggestion is that the parameter files that E24 used with BEAGLE are not the same as I am using, which leads to the differences in the inferred EW distributions. At least the former half of that statement is probably true; the original parameter files are gone, so it is impossible to know definitively the exact setup. But E24 do describe much of the adopted priors, summarized against my own priors in the priors table above. Some discussion of the differences in priors follows.

- **Redshift.** E24 restricted the fitted redshift of the F775W dropouts to a uniform prior of $z = 4 - 8$. Instead of that, I carried over a more expansive prior I had previously used which uniformly sampled $z = 0 - 25$. This probably explains a few galaxies with anomalously faint $M_\text{UV}$, since their solutions prefer a low redshift ($z\sim1$).

- **Age.** E24 describe setting a logarithmically uniform prior on the age between $1$ Myr and the age of the universe at the sampled redshift. It's not exactly clear if my approach also does this. I used a logarithmically uniform prior between $10^6 - 10^{10.2}$ yr, matching the lower bound on age. However, the BEAGLE documentation is unclear how BEAGLE handles ages that exceed the age of the universe at a given redshift, which $10^{10.2}$ yr will certainly be for any redshift in a standard cosmology. The BEAGLE documentation makes it clear, for example, that it will reconcile any upper bounds on the age that are not consistent with the formation redshift (which my parameter file does not specify) and observed redshift. But it doesn't go as far as to say that it will automatically amend ages inconsistent with the age of the universe. Though I assume it does.

I have also compared my parameter file to another that Ryan shared with me as an example of what the original, lost parameter files were similar to. I found that the two were broadly consistent.

#### Open questions:

- Do my BEAGLE fits ever exceed the age of the universe at the given redshifts?
- How does BEAGLE handle ages exceeding the age of the universe at a given redshift?

### Different filter sets

**Concluded impact: unimportant**

I confirmed that the filter set that BEAGLE uses (`beagle/filters/filters.dat`) is the exact same filter set as E24 states. Perhaps the filter curves could vary slightly (a different wavelength resolution, for example), but that should be completely independent from the observed differences in the inferred EW distributions.

### Different filter choices to evaluate BEAGLE's priors on EWs

**Concluded impact: uncertain**

An important step when computing the inferred EW distributions is to normalize the "observed" posterior EW distributions from BEAGLE by some prior. This prevents priors from the SED modeling choices from driving any results surmised from the inferred EW distributions. The prior should encode information about the EWs BEAGLE can and does produce when unbiased toward any specific EW. 

In practice, E24 calculated the prior EW distributions by fitting BEAGLE to each dropout galaxy, except to just a single photometric band in the rest UV at the targeted redshifts, the brightness of which should deliver no constraining information about the strength of nebular emission lines in the rest optical wavelengths. The resulting prior EW distribution then normalized the posterior EW distribution measured from the full-photometry BEAGLE fit to the galaxy. 

E24 does not mention the specific filter they chose to perform that fitting. I chose NIRCam's F200W filter, which lies at some band between $\sim2300-3400$ $\text{\AA}$ for $z = 5.5 - 6.5$ (the approximate redshift band targeted by the selections designed for the F775W dropouts). E24 may have chosen a different filter for this operation, however, which could conceivably impact the inferred EW distributions by way of the prior EW distributions. I would expect, though, that the specific choice of rest UV filter should not significantly bias the prior EW distributions. This is computationally testable (but potentially wasteful) by calculating the prior EW distributions with different choices for a rest-UV filter.

#### Open questions:

- How do different choices of the rest-UV filter impact the EW priors?

### Biases in $M_\text{UV}$ measurements

**Concluded impact: important**

One possibility is that, for some reason, the absolute magnitude $M_\text{UV}$ and EWs are correlated differently, such that not quite the \textit{same} galaxies end up in the different $M_\text{UV}$ bins, shuffling the specific posterior EW distributions in each $M_\text{UV}$ bin. This might be the case, for example, if there are any systematic differences in the rest-UV brightness of the BEAGLE fits. This seems unlikely, though, since, from comparing the photometry of my own fits with the photometry of galaxies that E24 also shows, the photometry appears nearly identical.

At any rate, `compare_m_uv.ipynb` produced the below figure, showing, for the objects of the E24 F775W dropout catalog, the $M_\text{UV}$ measurements made by E24 and my own measurements, using the BEAGLE fits to the photometry of the catalog. It seems a few of my measurements vastly underestimate the $M_\text{UV}$ compared to E24, but the two sets of measurements otherwise follow a very tight correlation, as expected. Although key physical parameters might be different, BEAGLE should definitely reproduce the observed brightness and shape of the rest-UV continuum well, at least modulo the redshift, which I suspect is what drives the minimal scatter in the correlation between the two measurements.

![image info](figs/m_uv_measurements_comparison.png)

I also compared the galaxies in the different $M_\text{UV}$ bins, according to the measurements of E24 and my own. With `bins()` in `compare_m_uv.ipynb`, I calculated the number of galaxies in each $M_\text{UV}$ bin for each set of $M_\text{UV}$ measurements, as well as the intersection of the two approaches. Interestingly, based on E24's measurements, there is one more galaxy in the bright bin, and one fewer galaxy in the very faint bin, than stated in the paper. The two approaches are very similar, though: 18 galaxies shift bins (so $<10\%$ of the sample). The table below summarizes the results.

| | E24 (paper) | E24 (catalog) | My BEAGLE CSFH fits to the E24 catalog | Common to both the E24 catalog and my BEAGLE CSFH fits to that catalog |
| :---: | :---: | :---: | :---: | :---: |
| Bright | 64 | 65 | 59 | 59 |
| Faint | 138 | 138 | 136 | 128 |
| Very faint | 76 | 75 | 83 | 73 |

Also in `bins()`, I found that nearly all of the galaxies that shift bins shift to a fainter bin, compared to E24, and tend to have a $\sim0.05-0.1$ mag fainter $M_\text{UV}$, though some are significantly fainter (multiple magnitudes). Of these objects, 6 shift from the bright to faint bin, 10 shift from the faint to very faint bin, and 2 shift from the very faint to faint bin.

With `compare_diff()` in `compare_m_uv.ipynb`, I determined the objects where the difference between my $M_\text{UV}$ measurement and that of E24 is $\geq 0.2$ mag. In total, 17 objects satisfy this condition. I then manually investigated the BEAGLE SEDs of those objects. Of the 17, 12 do not appear unusual from visual inspection, and 5 are clearly impacted by low-redshift solutions. I investigated if there was any correlation between the discrepancy in $M_\text{UV}$ and the discrepancy in $z$ between the two sets of measurements, summarized in the figure below. It shows that, as the $M_\text{UV}$ measured by E24 increases compared to what I measured, the redshift I measured also becomes larger compared to that measured by E24. That makes sense; the redshift directly impacts the inferred $M_\text{UV}$. The 4 outliers in the figure are also the 4 outliers in the previous figure (they're the only objects that have a large enough difference to be those markers, so they must be the same objects). Combined with the visual inspection of the SED fits, I think this is confirmation that the significant $M_\text{UV}$ discrepancy of these objects is attributable to low-redshift solutions dominating the posterior. However, ~4 galaxies possibly misbinned due to poor redshift priors probably cannot explain the large differences in the inferred EW distributions.

![](figs/delta_m_uv_z.png)

Next, I tried adopting the $M_\text{UV}$ measurements of E24 uncritically, so that the exact same galaxies should be in each $M_\text{UV}$ bin. After adopting that change and running the pipeline otherwise normally, I found that the posteriors of the inferred EW distributions are very similar to what E24 reported; the median of the mean's posterior is no more than $\sim30$ $\text{\AA}$ different, and the variances are basically consistent, except maybe that of the very faint $M_\text{UV}$ bin, which is a little higher. 

The bin shifting may be able to explain why my $M_\text{UV}$ measurements led to a much higher inferred mean of the EW distribution than when relying on the $M_\text{UV}$ reported by E24. We know that galaxies with brighter $M_\text{UV}$ generally have higher EWs. If the 6 galaxies that shifted down to the faint bin had $M_\text{UV}$ on the fainter tail of the bright bin, it might be plausible that this could've caused an increase in the typical EWs in the bright bin. Something similar may happen in the faint and very faint bins, but in reverse. In the faint bin, 6 galaxies from the bright bin enter and 10 galaxies shift to the very faint bin and 2 galaxies shift from the very faint bin to the faint bin. It could be that the galaxies from the bright bin have a larger EW, and the ones shed to the very faint bin have a smaller EW, bumping up the typical EWs. And similar for the very faint bin, too, from the galaxies in the faint bin entering it.

The number of common galaxies (those that stay in the same bin), compared to the "starting" size, are $\sim10-15\%$, so enough that this could have a significant impact.

<!--That higher variance may be driven by the 10 galaxies that shift from the faint to very faint $M_\text{UV}$ bin compared to E24. We know that the higher $M_\text{UV}$ galaxies generally have higher EWs, so that shift could be adding a higher-EW tail to the very faint bin, thus increasing the variance (the mean posterior also prefers $\sim20$ $\text{\AA}$ more than the same bin in E24, which is in line with this picture). And those 10 additional galaxies will add $\sim10-15\%$ to the sample size in the very faint bin, so they could have a significant impact. A similar effect may also be slightly pushing down the mean posterior of the bright bin (the difference between my ), too, since 6 galaxies shift from the bright to faint bin.-->

<!--
Very low redshift:

5 (16781_GOODSN, 28474_GOODSN, 43154_GOODSN, 63938_GOODSN, 94758_GOODSS)

Normal:

12
-->

<!--#### Open questions:-->

### Different methodologies for measuring EWs from SEDs

Measuring the EW of an emission or absorption line is a conceptually simple task, but its implementation can vary dramatically (e.g., the integration range or continuum estimation), easily producing systematic differences for the same data. E24 does not clarify how they measured the EWs of the key rest-optical nebular emission lines, meaning reproducing identical EWs is significantly more difficult.

My calculation of the EWs happens in the `calculate_ew()` command in `calculate_ew_distribution.ipynb`, which is a wrapper for my custom code to calculate the EWs from the posteriors of a set of BEAGLE fits.

I compared the [O III] + H-beta EWs I measured with those from E24 (see the figure below). I tend to measure higher EWs than E24, but especially so for objects they report as low-EW ($<10^2$ $\text{\AA}$). This could be connected to the clear "floor" also observed in the ionizing photon production efficiency $\xi_\text{ion}$ measured by BEAGLE.

<p float="left" align="middle">
    <img src="figs/compare_ew.png" width=33%/>
</p>

To investigate the last point further, I plotted the EWs measured by E24 against the corresponding BEAGLE output parameters from my own fits that also appear in the E24 catalog. The age and $\xi_\text{ion}$ are the most clearly correlated. The former definitely makes sense; it's just stating that younger galaxies have higher EWs. Importantly, it's clear from the latter that the low-EW objects, as measured by E24, also tend to be the low-$\xi_\text{ion}$ objects, which confirms that the floor in EW and in $\xi_\text{ion}$ are the same galaxies.

<p float="left" align="middle">
    <img src="figs/compare_max_stellar_age_ew_e24.png" width=33%/>
    <img src="figs/compare_xi_ion_unatt_stellar_ew_e24.png" width=33%/>
</p>

Because it looked (by eye, at least) that I measured much higher uncertainties on the EWs than E24, I also directly plotted the uncertainties we both measured against each other (the figure below). We both used the 16th and 84th percentiles of the measured EW posteriors as proxies for the uncertainty. And it does seem like there is a preference toward my measurements having larger uncertainties. I'm especially surprised that I did not measure \textit{any} EW to better than 70 $\textrm{\AA}$, whereas E24 measured some to better than 20 $\textrm{\AA}$.

<p float="left" align="middle">
    <img src="figs/compare_ew_errors.png" width=33%/>
</p>

#### Open questions

- Why do I tend to measure higher EWs? And why doesn't that seem to bear out in the inferred EW distributions (2/3 of which are lower-EW than reported by E24)?

# Why aren't the BEAGLE parameters always consistent?

When comparing key BEAGLE parameters from E24 versus those from my own fits, it's clear that the fits I made including Lya show significant discrepancies (see the figures below). Namely that my fits including Lya prefer higher redshifts (a few tenths larger), and slightly more massive and younger galaxies. In fact, this observation was the original catalyst that made me realize E24 did not appear to include Lya (by the apparent lack of any Lya emission in the figures of their SEDs), and thus to also try fitting the galaxies without any Lya emission. Though E24 doesn't explicitly mention if they included Lya in their emission line setup.

<p float="left" align="middle">
    <img src="figs/compare_redshift.png" width=33%/>
    <img src="figs/compare_M_tot.png" width=33%/>
    <img src="figs/compare_max_stellar_age.png" width=33%/>
</p>

At any rate, including Lya will cause a significant boost to the flux density observed in a corresponding filter, requiring a model fit to push to higher redshift to match the observed flux density in that filter, due to the immediate position of the Lyman break shortward of the rest Lya wavelength. I think this naturally explains why my fitting preferred slightly higher redshifts. That also likely leads to knock-on effects on the inferred UV slope, SFR, etc., which is probably what drives the slightly higher masses and younger ages inferred by the fits that include Lya. It's possible that this also has effects on the measured EWs.

That the fits excluding Lya appear to match the results of E24 very closely is suggestive that those fits are the "correct" approach, at least as far as reproducing the results of E24.

Other quantities, though, besides those mentioned above, are still discrepant after removing Lya from the line modeling setup. For posterity, for each parameter that also existed in the E24 catalog, I compared the BEAGLE parameters from my own fits. Notably, the metallicity is significantly discrepant, where my fits prefer metallicities ~1.5 dex lower than E24 (with minimal impact from removing Lya emission, at least on the bulk distribution of metallicities). The slope, however, seems consistent with a 1-to-1 relationship, which makes me question if the comparison is really apples-to-apples, and instead my own results are offset somehow. BEAGLE offers several options for the metallicity: a mass-weighted stellar metallicity, luminosity-weighted stellar metlallicity, or the ISM metallicity. It's not clear which (if any) of these corresponds to the metallicities logged in the E24 catalog. There is a compounding issue, too: my metallicities are *very* low, clustering around $10^{-3}$ Solar metallicity. This is well outside the range of even my own priors (which had a lower bound of $10^{-2.2}$ Solar metallicity), so it's not even clear why my metallicities are so low. Worth pointing out is that my BEAGLE fitting set the nebular / ISM metallicity as "dependent," so that the specific choice of BEAGLE's output metallicity type always produces an identical metallicity.

<p float="left" align="middle">
    <img src="figs/compare_Z_ISM.png" width=33%/>
</p>

Also different is the ionizing photon production efficiency, $\xi_\text{ion}$. Regardless of the specific BEAGLE output choice for measuring $\xi_\text{ion}$, the result is still the same: an abrupt "floor" in the reported measurements from BEAGLE, beyond which no lower $\xi_\text{ion}$ is measured, even if E24 reported a much lower $\xi_\text{ion}$. Including or not including Lya does have a significant impact, presumably bceause of its downstream effects on the inferred SFR, UV slope, etc.

<p float="left" align="middle">
    <img src="figs/compare_xi_ion.png" width=33%/>
    <img src="figs/compare_xi_ion_unatt.png" width=33%/>
    <img src="figs/compare_xi_ion_unatt_stellar.png" width=33%/>
</p>

Correspondingly, there is also an abrupt floor in EW, and the same galaxies tend to cohabitate both of those floors.

#### Open questions

- How does including Lya affect the measured [O III] and H-beta EWs?
- Why are my metallicities so low?
- What metallicity does the E24 catalog contain?