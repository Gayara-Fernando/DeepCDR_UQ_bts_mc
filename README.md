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

### Uncertainty quantification with Bootstrap Confidence Intervals

For creating the confidence intervals (CIs) for uncertainty quantification, we use the method suggested by Heskes (1997 - https://proceedings.neurips.cc/paper_files/paper/1996/file/7940ab47468396569a906f75ff3f20ef-Paper.pdf). For a more straightforward explanation, refer to section II of the paper "Constructing Optimal Prediction Intervals by Using Neural Networks and Bootstrap Method" https://ieeexplore.ieee.org/document/6895153 by Khosravi et al. (2014). Two aspects of prediction intervals (PIs) make them highly informative and valuable for analysis and decision-making. First, wider PIs indicate less reliable predicted values, meaning they should be used with caution. This suggests a high degree of uncertainty in the data, which cannot be entirely removed from the prediction process. Second, PIs are associated with a confidence level, which provides an indication of their accuracy. The scripts (mainly inference) follow the steps in Section II of the above-mentioned Khosvari et al. (2014) work in computing the prediction intervals and thereby the two aspects, the confidence interval width and coverage. To implement the PIs, run the following three scripts.

#### 1. Preprocessing script
```
python deepcdr_preprocess_improve.py --input_dir ./csa_data/raw_data --output_dir exp_result
```
Preprocesses the CSA data and creates train, validation (val), and test datasets.

This command generates the following folder:

* five model input data files: `cancer_dna_methy_model`, `cancer_gen_expr_model`, `cancer_gen_mut_model`, `drug_features.pickle`, `norm_adj_mat.pickle`
* three tabular data files, each containing the drug response values (i.e. AUC) and corresponding metadata: `train_y_data.csv`, `val_y_data.csv`, `test_y_data.csv`

```
exp_result
 ├── param_log_file.txt
 ├── cancer_dna_methy_model
 ├── cancer_gen_expr_model
 ├── cancer_gen_mut_model
 ├── test_y_data.csv
 ├── train_y_data.csv
 ├── val_y_data.csv
 ├── drug_features.pickle
 └── norm_adj_mat.pickle
```

#### 2. Training script

Since bootstraps involve sampling with replacement, a new generator function was written to implement this in the DeepCDR model. This new generator is in the Python script "New_data_generator_with_tf.py". There are 10 bootstrap samples (therefore 10 models) trained in the train script, and the prediction intervals are computed using the predictions from all these 10 models. This number can be changed by changing the value of parameter B in the script "deepcdr_train_bootstrap_improve_with_new_generator.py" (line 212). To execute the train script, run the following.

```
python deepcdr_train_bootstrap_improve_with_new_generator.py --input_dir exp_result
```

This generates the following content in a folder named "bootsrtrap_results_all".

```
bootstrap_results_all
 ├── bootstrap_1
      └── DeepCDR_model
      └── val_scores.json
      └── val_y_data_predicted.csv
 ├── bootstrap_2
      └── DeepCDR_model
      └── val_scores.json
      └── val_y_data_predicted.csv
 
.

.

.
 
 ├── bootstrap_10
      └── DeepCDR_model
      └── val_scores.json
      └── val_y_data_predicted.csv
```
Note that each bootstrap model is stored inside the DeepCDR_model folder.

#### 3. Inference script

To get the performance metrics for the averaged predictions, and the coverages and the widths of the prediction intervals, run the following command.

```
python deepcdr_infer_bootstrap_improve_with_new_generator.py --input_data_dir exp_result --input_model_dir bootstrap_results_all --output_dir bootstrap_inference --calc_infer_score true
```

This contentent from this are the two folders bootstrap_inference and NNe_model, as follows.

```
bootstrap_inference

    └── param_log_file.txt
    └── test_scores.json
    └── CI_information_bootstraps.json
    └── test_y_data_predicted.csv

NNe_model
```
The widths and the coverages of the prediction intervals will get stored in the json file "CI_information_bootstraps.json".

### Uncertainty quantification with Dropout-induced Confidence Intervals with Monte-Carlo Dropout.

MC-dropout introduced as an approximation to Bayesian neural networks by Gal et al. (2015) (https://arxiv.org/abs/1506.02142) was used for this implementation. The dorpouts are activated during inference phase (for some layers connected to the prediction head). To implement this work, run the following on the command line.
#### 1. Preprocessing script
```
python deepcdr_preprocess_improve.py --input_dir ./csa_data/raw_data --output_dir mc_dropout_exp_results
```
Preprocesses the CSA data and creates train, validation (val), and test datasets.

This command generates the following folder:

* five model input data files: `cancer_dna_methy_model`, `cancer_gen_expr_model`, `cancer_gen_mut_model`, `drug_features.pickle`, `norm_adj_mat.pickle`
* three tabular data files, each containing the drug response values (i.e. AUC) and corresponding metadata: `train_y_data.csv`, `val_y_data.csv`, `test_y_data.csv`

```
mc_dropout_exp_results
 ├── param_log_file.txt
 ├── cancer_dna_methy_model
 ├── cancer_gen_expr_model
 ├── cancer_gen_mut_model
 ├── test_y_data.csv
 ├── train_y_data.csv
 ├── val_y_data.csv
 ├── drug_features.pickle
 └── norm_adj_mat.pickle
```
Notice there is no change in the preprocess script. Only the location of the output directory was changed.

#### 2. Training script

This work currently uses 25 predictions per test sample, but this number can be changed by adjusting the range in line 189 to the number of predictions we need in the script "deepcdr_infer_mcdropout_improve.py".

To execute the train script, run the following.

```
python deepcdr_train_mcdropout_improve.py --input_dir mc_dropout_exp_results --output_dir mc_dropout_exp_results
```
Generates:
* trained model: `DeepCDR_model`
* predictions on val data (tabular data): `val_y_data_predicted.csv`
* prediction performance scores on val data: `val_scores.json`
```
mc_dropout_exp_results
 ├── param_log_file.txt
 ├── cancer_dna_methy_model
 ├── cancer_gen_expr_model
 ├── cancer_gen_mut_model
 ├── test_y_data.csv
 ├── train_y_data.csv
 ├── val_y_data.csv
 ├── drug_features.pickle
 ├── norm_adj_mat.pickle
 ├── DeepCDR_model
 ├── val_scores.json
 └── val_y_data_predicted.csv
```


#### 3. Inference script

To get the performance metrics for the averaged predictions, and the coverages and the widths of the prediction intervals, run the following command.

```
python deepcdr_infer_mcdropout_improve.py --input_data_dir mc_dropout_exp_results --input_model_dir mc_dropout_exp_results --output_dir mc_dropout_exp_results --calc_infer_score true
```

Generates:
* Averaged predictions on test data (tabular data): `test_y_data_predicted.csv`
* prediction performance scores on test data: `test_scores.json`
* CI information from the MC-dropout method
```
mc_dropout_exp_results
 ├── param_log_file.txt
 ├── cancer_dna_methy_model
 ├── cancer_gen_expr_model
 ├── cancer_gen_mut_model
 ├── test_y_data.csv
 ├── train_y_data.csv
 ├── val_y_data.csv
 ├── drug_features.pickle
 ├── norm_adj_mat.pickle
 ├── DeepCDR_model
 ├── val_scores.json
 ├── val_y_data_predicted.csv
 ├── test_scores.json
 ├──mc_dropout_exp_results.json
 └── test_y_data_predicted.csv




