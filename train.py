import cv2
import numpy as np
import glob
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard
import random

SHAPES = (129, 124)
classes = ["no", "on", "go", "up", "stop", "off", "left", "right", "down", "yes","<UNK>"]

# def load_data(path, nb_classes):
#     images = []
#     labels = []
#     not_same = 0
#     same = 0
#     ims = glob.glob(path + '/*.png')
#     random.shuffle(ims)
#     nb_unk = 0
#     for im in ims:
#         if nb_unk<3100 or im.split('label')[1].split('_')[0] not in ['0']:
#             if im.split('label')[1].split('_')[0] in ['0']:
#                 nb_unk += 1
#             image = cv2.imread(im, 0)
#             if image.shape[0] != 129:
#                 print("SHAPE0:", image.shape[0], im)
#             if image.shape[1] != 124:
#                 #print("SHAPE1:", image.shape[1], im)
#                 not_same +=1
#             else:
#                 same += 1
#                 img = np.asarray(cv2.imread(im, 0))
#                 images.append(img)
#                 lab = np.zeros((nb_classes,), dtype=int)
#                 lab[int(im.split('label')[1].split('_')[0])] = 1
#                 labels.append(lab)

#                 #print(lab, im)

#             if same%1000==0:
#                 print(same, not_same)


#     images = np.asarray(images)
#     labels = np.asarray(labels)

#     sep = -len(images)//10
#     train_images = images[:sep].reshape(sep, 129, 124, 1)
#     train_labels = labels[:sep]
#     test_images = images[sep:].reshape(len(images[sep:]), 129, 124, 1)
#     test_labels = labels[sep:]

#     return train_images, train_labels, test_images, test_labels

def load_data(path, nb_classes):
    images = []
    labels = []
    not_same = 0
    same = 0
    ims = glob.glob(path + '/*.png')
    random.shuffle(ims)
    count_class = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
    for im in ims:
            image = cv2.imread(im, 0)
            if image.shape[0] != 129:
                print("SHAPE0:", image.shape[0], im)
            if image.shape[1] != 124:
                #print("SHAPE1:", image.shape[1], im)
                not_same +=1
            else:
                same += 1
                img = np.asarray(image)
                images.append(img)
                lab = [0,0,0,0,0,0,0,0,0,0]
                lbl = int(im.split('\\')[-1].split('_')[0])
                lab[lbl] = 1
                lab = np.asarray(lab)
                count_class[str(lbl)] += 1
                labels.append(lab)

                #print(lab, im)

            if same%1000==0:
                print(same, not_same)


    images = np.asarray(images)
    labels = np.asarray(labels)

    sep = -len(images)//10
    train_images = images[:sep].reshape(sep, 129, 124, 1)
    train_labels = labels[:sep]
    test_images = images[sep:].reshape(len(images[sep:]), 129, 124, 1)
    test_labels = labels[sep:]

    print(count_class)

    return train_images, train_labels, test_images, test_labels




train_images, train_labels, test_images, test_labels = load_data('spectro_F', 10)
print(len(train_images),len(train_labels),len(test_images),len(test_labels))

model = Sequential()

model.add(Conv2D(input_shape=(129, 124, 1),filters=34, kernel_size=(11,11), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
model.add(Dropout(rate=0.15))
model.add(Conv2D(filters=22, kernel_size=(11,11), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
model.add(Dropout(rate=0.15))
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(rate=0.10))
model.add(Dense(130, activation='relu'))
model.add(BatchNormalization())
model.add(Dense(84, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(rate=0.15))
model.add(Dense(54, activation='relu'))
model.add(BatchNormalization())
model.add(Dense(10, activation='softmax'))

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

model.summary()

history = model.fit(train_images, train_labels, batch_size=64, epochs=10, validation_split=0.2)

loss, accuracy = model.evaluate(x=test_images, y=test_labels, verbose=0)
print("Données de test - Perte: %2.2f - Précision: %2.2f" %(loss, 100*accuracy))

model.save("modelNN.h5")
