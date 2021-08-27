.PHONY: pack-build run

pack-build:
	pack build -t igroff/$$(basename $$(pwd)) $$(basename $$(pwd)) --path . --builder heroku/buildpacks

run:
	docker run -p 8080:8080 $$(basename $$(pwd))
