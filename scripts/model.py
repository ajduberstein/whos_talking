import glob
import sys
import numpy

from keras import backend as K

from keras.utils import np_utils  # noqa

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

if not glob.glob('/matrices/*.npy'):
    print('Generate .npy files using preprocess.py first')
    sys.exit(1)


X_test = numpy.load('/matrices/X_test.npy')
X_train = numpy.load('/matrices/X_train.npy')
y_test = numpy.load('/matrices/y_test.npy')
y_train = numpy.load('/matrices/y_train.npy')


print('Generating model...')
# Model ############


K.set_image_dim_ordering('th')


model = Sequential()

model.add(Conv2D(42, (3, 3), activation='relu', input_shape=(1, 300, 26)))
model.add(Conv2D(21, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(2, activation='softmax'))

# 8. Compile model
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# 9. Fit model on training data
model.fit(X_train, y_train,
          batch_size=32, nb_epoch=10, verbose=1)

# 10. Evaluate model on test data
print('Scoring...')
print(model.evaluate(X_test, y_test, verbose=1))

print('Saved weights.')
model.save_weights('./output/gender_weights.h5')
print('Done.')
