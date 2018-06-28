import glob
import json

from lib.image import Image


class Builder:
    def __init__(self, manifest):
        self.manifest = json.load(open(manifest, 'r'))

        self._load_images("%s/*/Dockerfile".format(manifest['container']))

    def _load_images(self, pattern):
        images = {}
        for dockerfile in glob.glob(pattern):
            image = Image(dockerfile)
            images[image.name] = image

        self.images = images

