# This config has been generated by the pocket_coffea CLI 0.9.4.
from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.lib.cut_definition import Cut
from pocket_coffea.lib.cut_functions import get_nObj_min, get_HLTsel, get_nPVgood, goldenJson, eventFlags
from pocket_coffea.parameters.cuts import passthrough
from pocket_coffea.parameters.histograms import *

import workflow
from workflow import BasicProcessor

# Register custom modules in cloudpickle to propagate them to dask workers
import cloudpickle
import custom_cut_functions
cloudpickle.register_pickle_by_value(workflow)
cloudpickle.register_pickle_by_value(custom_cut_functions)

from custom_cut_functions import *
import os
localdir = os.path.dirname(os.path.abspath(__file__))

# Creating weights configuration
from pocket_coffea.lib.weights.common import common_weights

# Loading default parameters
from pocket_coffea.parameters import defaults
default_parameters = defaults.get_default_parameters()
defaults.register_configuration_dir("config_dir", localdir+"/params")

parameters = defaults.merge_parameters_from_files(default_parameters,
                                                    f"{localdir}/params/object_preselection.yaml",
                                                    f"{localdir}/params/triggers.yaml",
                                                   update=True)

#Creating custom weight
from pocket_coffea.lib.weights.weights import WeightLambda
import numpy as np

my_custom_weight_data = WeightLambda.wrap_func(
    name="my_custom_weight_on_data",
    function=lambda params, metadata, events, size, shape_variations:
         np.ones(size)*2.,
    has_variations=False,
    isMC_only=False
    )



cfg = Configurator(
    parameters = parameters,
    datasets = {
        "jsons": ['datasets/datasets_redirector.json'],
        "filter" : {
            "samples": ['TTTo2L2Nu', "DATA_SingleMuon"],
            "samples_exclude" : [],
            "year": ['2018']
        }
    },

    workflow = BasicProcessor,

    skim = [get_nPVgood(1), eventFlags, goldenJson], 

    preselections = [passthrough],
    categories = {
        "2jets_A": [get_nObj_min(2, coll="JetGood")],
        "2jets_B": [get_nObj_min(2, coll="JetGood")],
    },

    weights = {
        "common": {
            "inclusive": ["genWeight","lumi","XS","pileup",
                          "sf_ele_id","sf_ele_reco",
                          "sf_mu_id","sf_mu_iso",
                          ],
            "bycategory": {
                          },
       },
        "bysample": {
            "TTTo2L2Nu": {
                "bycategory": {
                }
            },
            "DATA_SingleMuon": {
                "bycategory": {
                    "2jets_B": ["my_custom_weight_on_data"],
                }
            }
            
        }
    },
    # Passing a list of WeightWrapper objects
    weights_classes = common_weights + [my_custom_weight_data],

    variations = {
        "weights": {
            "common": {
                "inclusive": [ "pileup",
                               "sf_ele_id", "sf_ele_reco",
                               "sf_mu_id", "sf_mu_iso",
                               ],
                "bycategory" : {
                }
            },
            "bysample": {
                "TTTo2L2Nu": {
                    "bycategory": {
                    }
                },
            }
        },
    },

    variables = {
        **count_hist("JetGood"),
    },

    columns = {

    },
)
