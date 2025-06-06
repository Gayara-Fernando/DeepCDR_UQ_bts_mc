import tensorflow as tf
from tensorflow.keras import backend as K
import pickle
import numpy as np
import pandas as pd
import os
import json
import sys
import warnings
from pathlib import Path
from pprint import pformat
from typing import Dict, Union
from New_data_generator_with_tf import DataGenerator, batch_predict

# [Req] IMPROVE imports
from improvelib.applications.drug_response_prediction.config import DRPInferConfig
from improvelib.utils import str2bool
import improvelib.utils as frm

# Model-specific imports
from model_params_def import infer_params # [Req]

# # device ID
# os.environ["CUDA_VISIBLE_DEVICES"] = "7"

filepath = Path(__file__).resolve().parent # [Req]

# [Req]
def run(params):
    """ Execute specified model training.

    :params: Dict params: A dictionary of CANDLE/IMPROVE keywords and parsed values.

    :return: List of floats evaluating model predictions according to
             specified metrics_list.
    :rtype: float list
    """
    # import pdb; pdb.set_trace()

    # ------------------------------------------------------
    # [Req] Create data names for test set
    # ------------------------------------------------------
    test_data_fname = frm.build_ml_data_file_name(data_format=params["data_format"], stage="test")

    # import the preprocessed data
    # specify the directory where preprocessed data is stored
    data_dir = params['input_data_dir']

    # load models for preprocessed data
    cancer_gen_expr_model = tf.keras.models.load_model(os.path.join(data_dir,"cancer_gen_expr_model"))
    cancer_gen_mut_model = tf.keras.models.load_model(os.path.join(data_dir, "cancer_gen_mut_model"))
    cancer_dna_methy_model = tf.keras.models.load_model(os.path.join(data_dir, "cancer_dna_methy_model"))

    cancer_gen_expr_model.trainable = False
    cancer_gen_mut_model.trainable = False
    cancer_dna_methy_model.trainable = False

    with open(os.path.join(data_dir, "drug_features.pickle"),"rb") as f:
        dict_features = pickle.load(f)

    with open(os.path.join(data_dir, "norm_adj_mat.pickle"),"rb") as f:
        dict_adj_mat = pickle.load(f)

    test_keep = pd.read_csv(os.path.join(data_dir, "test_y_data.csv"))
    test_keep.columns = ["Cell_Line", "Drug_ID", "AUC"]

    test_gcn_feats = []
    test_adj_list = []
    for drug_id in test_keep["Drug_ID"].values:
        test_gcn_feats.append(dict_features[drug_id])
        test_adj_list.append(dict_adj_mat[drug_id])

    test_gcn_feats = np.array(test_gcn_feats).astype("float32")
    test_adj_list = np.array(test_adj_list).astype("float32")

    # load the model
    modelpath = frm.build_model_path(model_file_name=params["model_file_name"], model_file_format=params["model_file_format"], model_dir=params["input_model_dir"]) # [Req]
    model_path = os.path.join(modelpath, "DeepCDR_model")
    check = tf.keras.models.load_model(model_path)

    # # get the predictions on the test set
    generator_batch_size = params['infer_batch']
 
    preds_test, target_test = batch_predict(check, DataGenerator(test_gcn_feats, test_adj_list, test_keep["Cell_Line"].values.reshape(-1,1), test_keep["Cell_Line"].values.reshape(-1,1), test_keep["Cell_Line"].values.reshape(-1,1), test_keep["AUC"].values.reshape(-1,1), generator_batch_size, shuffle = False))

    # ------------------------------------------------------
    # [Req] Save raw predictions in dataframe
    # ------------------------------------------------------
    frm.store_predictions_df(
        y_true=target_test, 
        y_pred=preds_test, 
        stage="test",
        y_col_name=params["y_col_name"],
        output_dir=params["output_dir"],
        input_dir=params["input_data_dir"]
    )

    # ------------------------------------------------------
    # [Req] Compute performance scores
    # ------------------------------------------------------
    if params["calc_infer_scores"]:
        test_scores = frm.compute_performance_scores(
            y_true=target_test, 
            y_pred=preds_test, 
            stage="test",
            metric_type=params["metric_type"],
            output_dir=params["output_dir"]
        )


# [Req]
def main(args):
    # [Req]
    additional_definitions = infer_params
    cfg = DRPInferConfig()
    params = cfg.initialize_parameters(
        pathToModelDir=filepath,
        default_config="deepcdr_params.txt",
        additional_definitions=additional_definitions
    )
    status = run(params)
    print("\nFinished model inference.")


# [Req]
if __name__ == "__main__":
    main(sys.argv[1:])
