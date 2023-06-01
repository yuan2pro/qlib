# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import unittest
import shutil
import difflib
from qlib.finco.tpl import get_tpl_path
import ruamel.yaml as yaml

from qlib.data.dataset.handler import DataHandlerLP
from qlib.utils import init_instance_by_config
from qlib.tests import TestAutoData

from pathlib import Path
from qlib.finco.tpl import get_tpl_path
from qlib.finco.task import YamlEditTask

DIRNAME = Path(__file__).absolute().resolve().parent


class FincoTpl(TestAutoData):
    def test_tpl_consistence(self):
        """Motivation: make sure the configuable template is consistent with the default config"""
        tpl_p = get_tpl_path()
        with (tpl_p / "sl" / "workflow_config.yaml").open("rb") as fp:
            config = yaml.safe_load(fp)
        # init_data_handler
        hd: DataHandlerLP = init_instance_by_config(config["task"]["dataset"]["kwargs"]["handler"])
        # NOTE: The config in workflow_config.yaml is generated by the following code:
        # dump in yaml format to file without auto linebreak
        # print(yaml.dump(hd.data_loader.fields, width=10000, stream=open("_tmp", "w")))

        with (tpl_p / "sl-cfg" / "workflow_config.yaml").open("rb") as fp:
            config = yaml.safe_load(fp)
        hd_ds: DataHandlerLP = init_instance_by_config(config["task"]["dataset"]["kwargs"]["handler"])
        self.assertEqual(hd_ds.data_loader.fields, hd.data_loader.fields)

        check = hd_ds.fetch().fillna(0.0) == hd.fetch().fillna(0.0)
        self.assertTrue(check.all().all())

    def test_update_yaml(self):
        p = get_tpl_path() / "sl" / "workflow_config.yaml"
        p_new = DIRNAME / "_test_config.yaml"
        shutil.copy(p, p_new)
        updated_content = """
class: LGBModelTest
module_path: qlib.contrib.model.gbdt
kwargs:
    loss: mse
    colsample_bytree: 1.8879
    learning_rate: 0.3
    subsample: 0.8790
    lambda_l1: 205.7000
    lambda_l2: 580.9769
    max_depth: 9
    num_leaves: 211
    num_threads: 21
"""
        t = YamlEditTask(p_new, "task.model", updated_content)
        t.execute()
        # NOTE: the formmat is changed by ruamel.yaml, so it can't be compared by text directly..
        # print the diff between p and p_new with difflib
        # with p.open("r") as fp:
        #     content = fp.read()
        # with p_new.open("r") as fp:
        #     content_new = fp.read()
        # for line in difflib.unified_diff(content, content_new, fromfile="original", tofile="new", lineterm=""):
        #     print(line)


if __name__ == "__main__":
    unittest.main()
