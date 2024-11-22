SHELL := /bin/bash

out_dir=out/
gen_dir=generated/

clean-out:
	rm -rf ${out_dir}

gen-server:
	docker run --rm -v ./:/app/ openapitools/openapi-generator-cli generate \
    -i /app/auth_demo.yaml \
    -g python-flask \
    -o /app/${out_dir}

clean-gen:
	rm -rf ${gen_dir}

snap-to-gen: clean-gen
	cp -r ${out_dir} ${gen_dir}

rebuild-gen: clean-out gen-server snap-to-gen
