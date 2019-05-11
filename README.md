# Docker builder

A Python application which manages Docker containers. It adds support to automatically detect up- & downstream images,
build those images and push them to a Docker repository. This eases the use of automated CI / CD which needs custom 
images.

## Installation

This application should be run with Python >= 3.5 so create a venv with the correct Python version after downloading.
When pushing to registries, please make sure you're logged in to them.

## Configuration

The builder supports default configuration from a `.Dockerbuild` file. This should be located in the user's home 
directory (`~/.Dockerbuild`) and it should be in `INI` format. The following config options exist:

```ini
[core]
    push = Bool <False> (Whether to push images to an external registry after they're build) 

[logging]
    level = String <info> (The logging level, can be debug or info)
    
[registries] (Array of registries to push images to after they're build)
registry[] = registry-one 
registry[] = registry-two
...

[directories] (Array of directories which contain the Dockerfiles for the images)
directory[] = /path/to/images
directory[] = /path/to/more/images
...
```

You can also pass configuration options to the CLI which take precedence over the default configuration. To learn more
about these options, run `./builder.py -h`.

## Docker containers

The application will scan `Dockerfile`s in the configured directories, determine the dependency order and build the 
images in the resolve order. You can pass additional data to the `docker build` & `docker push` operations by providing
a `manifest.json` file in the same directory as where the `Dockerfile` resides. Options for the `manifest.json` file are:

- `"local_tag": "image:version"` (The tag used for the image the local Docker repository. When this is not present, the image will not be tagged)
- `"registry_tag": "image:other-version"` (The tag used for the image in the registries. If this tag is not present, the image will not be pushed)
- `"arguments": {}` (Arguments that are passed to the docker build command. These [options](https://docs.docker.com/engine/reference/commandline/build/#options) are supported)
- `"pre_build": []` (Commands that are executed before the image is build)
- `"post_build": []` (Commands that are executed after the image is build)

A `manifest.json` file could look like this:
```json
{
  "local_tag": "acme-container:1.0",
  "registry_tag": "container:latest",
  "arguments": {
    "--no-cache": ""
  },
  "pre_build": [
    "git clone repo"
  ],
  "post_build": [
    "rm -rf repo"
  ]
}
```
