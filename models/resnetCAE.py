from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.layers import (
    Add,
    ReLU,
    Conv2D,
    Conv2DTranspose,
    MaxPooling2D,
    BatchNormalization,
    Activation,
)
from resnet.resnet import build_resnet
from resnet.decoder import Decoder
from resnet.encoder import Encoder
from src import config

encoded_dim = config.ENCODED_DIM
img_size = config.IMG_SIZE


def build_model(model: str, color_mode: str):
    color_list = ["rgb", "gray"]
    model_type = ["resnet18", "resnet34", "resnet50", "resnet101", "resnet152"]
    assert model in model_type, f"Specified model type doesn't exist. These types of resnet are available: {model_type}"

    assert color_mode in color_list, \
        f"Specified color mode: '{color_mode}' is not available, These color modes are available: {color_list}"

    # set channels
    if color_mode == "gray":
        channels = 1
    if color_mode == "rgb":
        channels = 3

    input_shape = (4, img_size, img_size, channels)
    resnet = build_resnet(model, input_shape, encoded_dim)

    encoder = Encoder(resnet)
    decoder = Decoder(channels)
    cae = ResnetCAE(encoder, decoder)
    # cae.build(input_shape=input_shape)

    return cae


class ResnetCAE(keras.Model):
    def __init__(self, encoder, decoder):
        super(ResnetCAE, self).__init__()
        self.encoder = encoder
        self.decoder = decoder

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)

        return decoded

cae = build_model("resnet18", "rgb")
inputs = tf.random.uniform(shape=(4, 256, 256, 3))
outputs = cae(inputs)
print(outputs)
cae.save("./saved_model/cae_resnet18.pb", save_format="tf")


