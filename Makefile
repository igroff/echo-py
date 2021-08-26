.PHONY: pack-build

pack-build:
	pack build echo-py --path . --builder heroku/buildpacks
