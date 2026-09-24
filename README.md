# Early Evolution of the Prokaryotic Transcription Factor Repertoire

Analysis code for:

> Singh IR, Dubey A, Seshasayee ASN. **Early Evolution of the Prokaryotic Transcription Factor Repertoire.** *Genome Biology and Evolution* 2026; 18(6): evag141. [doi:10.1093/gbe/evag141](https://doi.org/10.1093/gbe/evag141) | [bioRxiv preprint](https://doi.org/10.64898/2026.04.08.717362)

Supplementary datasets: [Figshare (10.6084/m9.figshare.31941684)](https://doi.org/10.6084/m9.figshare.31941684)

## What this project asks

Transcription factors (TFs) are not part of any minimal gene set for cellular life, so when did they evolve, and how has their repertoire changed? We traced the history of about 500,000 TFs, grouped into about 1,700 orthologous groups (OGs) across about 3,000 bacterial and archaeal genomes, on several prokaryotic species trees.

## Key findings

- The most ancestral prokaryotes (LUCA, LACA, LBCA) most likely encoded multiple TFs. We identified **39 ancestral TF-OGs**, including DnaA, LexA, Rex and DtxR.
- Ancestral TF counts and superfamily diversity (normalised Shannon entropy) match expectations from extant genomes, which suggests TF sequence families diversified **before LUCA**.
- TF-OGs in bacteria emerged early and smoothly along the phylogeny. In eukaryotes they emerged in bursts at multicellular lineages.
- Later TF gains in prokaryotes mostly reflect recycling of families discovered elsewhere in the tree, consistent with horizontal gene transfer.

## Pipeline overview

| Step | What it does | Tools and settings |
|---|---|---|
| 1. Genomes | 2,945 species-non-redundant complete genomes from NCBI GenBank (2,876 bacteria, 69 archaea); reference and representative genomes prioritised | NCBI GenBank |
| 2. DNA-binding domains | Scan proteomes against HTH and zinc beta-ribbon (ZnBR) family HMMs | SUPERFAMILY v1.75 profiles; `hmmscan` (HMMER), E-value 1e-3; extra bitscore cutoff of 9.96 for ZnBR |
| 3. Orthologous groups | Assign DNA-binding proteins to OGs | eggNOG v5 profiles, E-value 1e-3 |
| 4. TF identification | Separate TFs from other DNA-binding proteins with 206 TF-associated Pfam profiles; an OG counts as a TF-OG if more than two-thirds of its proteins are TFs | HMMER, `--cut-tc` trusted cutoffs |
| 5. Species trees | 16S rRNA tree, concatenated ribosomal-protein tree, and pruned GTDB bacterial and archaeal trees | MUSCLE v5, trimAl (`gappyout`), IQ-TREE 2, ModelFinder; midpoint and MAD rooting |
| 6. Ancestral state reconstruction | Presence/absence of each OG at every node; presence called at probability > 0.75 | R `ape::ace`, equal-rates vs all-rates-different model chosen by log-likelihood |
| 7. Repertoire dynamics | Path-level discovery and progenitor nodes, innovation ratio, CDFs of OG gains along the tree | Python / R (TODO: name scripts) |
| 8. Diversity and scaling | Node-level normalised Shannon entropy; power-law scaling of TFs with proteome size, with residuals for internal nodes | Python / R (TODO: name scripts) |
| 9. Controls | 100 simulations of OG presence/absence using per-OG transition matrices; about 20,000 random eggNOG OGs as a proteome-size proxy | In-house R script |

## Repository structure

<!-- TODO: replace with your actual layout, for example: -->

```
.
├── scripts/          # TODO: analysis scripts, in the order they are run
├── data/             # TODO: small input files; large files are on Figshare
├── results/          # TODO: output tables and figures
└── README.md
```

## Requirements

- Python 3 (TODO: list packages, for example pandas, numpy, matplotlib, scipy, biopython)
- R with `ape` (TODO: list other R packages)
- HMMER 3, MUSCLE v5, trimAl, IQ-TREE 2
- Reference data: SUPERFAMILY v1.75 HMMs, eggNOG v5, Pfam, GTDB (see paper for versions)

## How to reproduce

1. Download the supplementary datasets from [Figshare](https://doi.org/10.6084/m9.figshare.31941684) into `data/`.
2. TODO: give the order in which to run the scripts, with example commands.
3. TODO: state the expected outputs and which paper figures they correspond to.

## Data and code availability

Supplementary datasets are on Figshare (link above). This repository contains the analysis code.

## Citation

```bibtex
@article{singh2026early,
  title   = {Early Evolution of the Prokaryotic Transcription Factor Repertoire},
  author  = {Singh, Inder Raj and Dubey, Akshara and Seshasayee, Aswin Sai Narain},
  journal = {Genome Biology and Evolution},
  volume  = {18},
  number  = {6},
  pages   = {evag141},
  year    = {2026},
  doi     = {10.1093/gbe/evag141}
}
```

## Contact

Inder Raj Singh | National Centre for Biological Sciences, TIFR, Bengaluru | inderrajasr@gmail.com

