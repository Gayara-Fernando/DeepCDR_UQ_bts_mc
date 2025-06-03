### Uncertainty quantification in DRP models with Bootstrapping and Monte-Carlo dropout methods

This notebook contains the preprocessing, training, and inference scripts for implementing uncertainty quantification in the DeepCDR model. To execute the scripts for both models, do the following steps.

### 1. Clone this repository
```
git clone https://github.com/JDACS4C-IMPROVE/DeepCDR.git
cd DeepCDR
```

### 2. Set computational environment

Option 1: Create the conda env using the yml file.
```
conda env create -f parsl_env.yml
```

Option 2: Use the following commands to create the environment.
```
conda create --name DeepCDR_IMPROVE_env python=3.10
conda activate DeepCDR_IMPROVE_env
conda install tensorflow-gpu=2.10.0
pip install rdkit==2023.9.6
pip install deepchem==2.8.0
pip install PyYAML
```

### 3. Run `setup_improve.sh`.
```bash
source setup_improve.sh
```

This will:
1. Download cross-study analysis (CSA) benchmark data into `./csa_data/`.
2. Clone IMPROVE repo (checkout `develop`) outside the DeepCDR model repo.
3. Set up env variables: `IMPROVE_DATA_DIR` (to `./csa_data/`) and `PYTHONPATH` (adds IMPROVE repo).

