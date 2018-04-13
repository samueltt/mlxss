# -*- coding:utf-8 -*-
import os
import pickle
from six.moves import urllib

import tflearn
from tflearn.data_utils import *
import traceback


class XSS_ATTACK(object):
    def __init__(self):
        self.model = None
        self.model_path = "xss_model.tfl"
        self.X = None
        self.Y = None
    
    def gen_model(self):
        char_idx_file = 'char_idx_xss.pkl'
        maxlen = 25
        char_idx = None
        xss_data_file="xss-2000.txt"
        model = None
        try:
            self.X, self.Y, char_idx = \
                textfile_to_semi_redundant_sequences(xss_data_file, seq_maxlen=maxlen, redun_step=3,
                                                     pre_defined_char_idx=char_idx)
            
            
            #pickle.dump(char_idx, open(char_idx_file, 'wb'))
            
            g = tflearn.input_data([None, maxlen, len(char_idx)])
            g = tflearn.lstm(g, 32, return_seq=True)
            g = tflearn.dropout(g, 0.1)
            g = tflearn.lstm(g, 32, return_seq=True)
            g = tflearn.dropout(g, 0.1)
            g = tflearn.lstm(g, 32)
            g = tflearn.dropout(g, 0.1)
            g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
            g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                                   learning_rate=0.001)
            
            model = tflearn.SequenceGenerator(g, dictionary=char_idx,
                                          seq_maxlen=maxlen,
                                          clip_gradients=5.0,
                                          checkpoint_path='model_scanner_poc')
        except:
            traceback.print_exc()
        finally:
            return model
    
    def set_model(self):
        try:
            self.model = self.gen_model()
            # train model and save
            self.model.fit(self.X, self.Y, validation_set=0.1, batch_size=128,
                      n_epoch=2, run_id='scanner-poc')
            self.model.save(model_file=self.model_path)
        except:
            traceback.print_exc()
        
    def get_model(self):
        model_x = None
        try:
            model_x = self.gen_model()
            model_x.load(self.model_path)
        except:
            traceback.print_exc()
        finally:
            return model_x
    
    def general_payload(self, model=None):
        payload = ""
        try:
            payload = model.generate(32, temperature=1.0, seq_seed=">alert(1)<")
        except:
            pass
        finally:
            return payload

if __name__ == "__main__":
    x = XSS_ATTACK()
    print "train and set model"
    x.set_model()
    print "reload and use model"
    import time
    time.sleep(5)
    print "sleep 5 seconds"
    x.get_model()