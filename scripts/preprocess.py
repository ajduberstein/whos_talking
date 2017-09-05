from __future__ import print_function

from random import shuffle
import glob

from python_speech_features import (
    mfcc,
    logfbank
)
import scipy.io.wavfile as wav

import numpy as np

DATA_DIR = '../categorized_data/'
NUM_CEP = 26


# Preprocessing
def get_feat(fpath, feat_type):
    (rate, sig) = wav.read(fpath)
    func = mfcc if 'mfcc' else logfbank
    mfcc_feat = func(sig, rate, numcep=NUM_CEP)
    #    d_mfcc_feat = delta(mfcc_feat, 2)
    return mfcc_feat


# How many male and female voices are there?
wavs = [f for f in glob.glob(DATA_DIR + '*')]
print('Female voices count  : %d' % len([w for w in wavs if '/F_' in w]))
print('Male voice count     : %d' % len([w for w in wavs if '/M_' in w]))

SAMPLE_NUM = 15500

# Randomize
shuffle(wavs)

# Make roughly half F and half F
vox = [w for w in wavs if '/F_' in w][:SAMPLE_NUM]
vox.extend([w for w in wavs if '/M_' in w][:SAMPLE_NUM])
shuffle(vox)

print('Generating features...')
XY = np.array([(get_feat(v, 'mfcc'), 'M' if '/M' in v else 'F', vox) for v in vox])

print('Enforce a 300 frame minimum...')

# Require at least 300 obs
print('%d observations longer than 300 frames' % len([x[0].shape[0] for x in XY if x[0].shape[0] >= 300]))


reb = 1.0*len([x[1] for x in XY if x[0].shape[0] >= 300 and x[1] == 'F']) / \
    len([x[1] for x in XY if x[0].shape[0] >= 300])

print('Balance: %s pct female' % str(reb*100))

X, Y = [], []
for i in range(0, len(XY)):
    if XY[i][0].shape[0] >= 300:
        Y.append(XY[i][1])  # labels
        X.append(XY[i][0][:300])  # features

X = np.array(X)
more_X = np.reshape(X, (X.shape[0], 1, X.shape[1], X.shape[2]))

Y = [[0, 1] if y == 'M' else [1, 0] for y in Y]
Y = np.array(Y)

print('X shape: %s' % str(more_X.shape))
print('y shape: %s' % str(Y.shape))

PCT_TRAIN = 0.75
last_obs_in_training = int(more_X.shape[0] * PCT_TRAIN)
X_train, X_test = more_X[:last_obs_in_training], more_X[last_obs_in_training:]
y_train, y_test = Y[:last_obs_in_training], Y[last_obs_in_training:]

print('Saving matrices...')
np.save('../matrices/X_train', X_train)
np.save('../matrices/X_test', X_test)
np.save('../matrices/y_train', y_train)
np.save('../matrices/y_test', y_test)

print('Done.')
