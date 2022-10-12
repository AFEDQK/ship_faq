# -*- coding: utf-8 -*- #
# @Time : 2022/10/5 14:46


# 模型配置
import os

from bert4keras.tokenizers import load_vocab, Tokenizer

from utils.model_utils import get_encoder

model_d_path = "chinese_simbert_L-4_H-312_A-12"
config_path = os.path.join(model_d_path, "bert_config.json")
checkpoint_path = os.path.join(model_d_path, "bert_model.ckpt")
dict_path = os.path.join(model_d_path, "vocab.txt")
MODEL_SAVE_PATH = "models/best_model_928.weights"
maxlen = 64


class SimcseModel(object):
    def __init__(self):
        self.tokenizer = self.tokenize()
        self.model = self.create_model()

    def tokenize(self):
        # 加载并精简词表，建立分词器
        token_dict, keep_tokens = load_vocab(
            dict_path=dict_path,
            simplified=True,
            startswith=["[PAD]", "[UNK]", "[CLS]", "[SEP]"],
        )
        tokenizer = Tokenizer(token_dict, do_lower_case=True, pre_tokenize=None)
        return tokenizer

    def create_model(self):
        model = get_encoder(
            config_path,
            checkpoint_path,
            pooling="cls",
            dropout_rate=0.3
        )

        model.load_weights(MODEL_SAVE_PATH, by_name=True)
        model.summary()
        return model
