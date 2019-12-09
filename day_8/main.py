from enum import IntEnum
from itertools import accumulate
from functools import reduce

class Color(IntEnum):
    BLACK = 0
    WHITE = 1
    TRANSPARENT = 2

def flatten( array ):
    return reduce(lambda a, b: a + b, array)

class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def build_layer(self, data):
        if not data:
            return []

        return [ data[:self.width] ] + self.build_layer(data[self.width:])

    def get_read_length(self):
        '''
        The total amount of items that
        are consumed on each cycle of image parsing
        '''
        return self.width * self.height

class DecodedImage(Image):
    def __init__(self, encoded):
        super().__init__(encoded.width, encoded.height)
        self.decoded = self.decode(encoded.layers, self.build_blueprint(encoded.height,encoded.width))

    def __str__(self):
        return str("\n".join([str(decoded) for decoded in self.decoded]))

    def build_blueprint(self, height, width):
        return [ [ None for step in range(width) ] for step in range(height) ]

    def map_layer_to_image(self, layer, image):
        '''
        Takes in a layer and returns a decoded image
        '''
        if not layer:
            return image

        layer_data = tuple([ int(color) for color in flatten(layer)])
        flattened_image = flatten(image)

        for index, color in enumerate(layer_data):
            color = Color(color)

            if flattened_image[index] is None:
                flattened_image[index] = Color(color)

            if flattened_image[index] == Color.TRANSPARENT:
                flattened_image[index] = Color(color)

        return self.build_layer([ int(color) for color in flattened_image])


    def decode(self, encoded_layers, decoded_image):
        if not encoded_layers:
            return decoded_image

        layer = encoded_layers[:1][0]
        rest_layers = encoded_layers[1:]

        return self.decode( rest_layers, self.map_layer_to_image( layer, decoded_image ) )

    # def present(self):
    #     return "\n".join([str(decoded) for decoded in self.decoded])

class EncodedImage(Image):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.layers = None

    def set_layers(self, data):
        self.layers = self.parse_image_data(data)

    def parse_image_data(self, image_data, layers=[]):
        '''
        Takes in a string of image data and builds layers from it
        '''
        if not image_data:
            return layers

        raw_layer = image_data[:self.get_read_length()]
        rest_of_data = image_data[self.get_read_length():]

        return self.parse_image_data(
            rest_of_data,
            layers + [ self.build_layer(raw_layer) ]
        )

def num_chars_in_layer( layer, reference, count=0 ):
    if not layer:
        return count

    layer_string = layer[:1][0]
    rest_of_layer = layer[1:]

    return num_chars_in_layer( rest_of_layer, reference, count + layer_string.count(reference))

def get_layer_index_with_least_zeroes( layers ):
    return min([(num_chars_in_layer(layer, '0'), index) for index, layer in enumerate(layers)], key=lambda item: item[0])[1]

def get_num_1s_in_layer( layer ):
    return num_chars_in_layer( layer, '1' )

def get_num_2s_in_layer( layer ):
    return num_chars_in_layer( layer, '2' )
