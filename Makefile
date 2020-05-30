.PHONY: venv-setup site-setup site-gen site-serve site-commit site-publish

venv-setup:
	python -m venv venv && . venv/bin/activate
	pip install -r requirements.txt

site-setup:
	rm -rf site
	git clone --branch gh-pages --single-branch git@github.com:berfr/fakesocial.git site

site-gen:
	python -m fakesocial --verbose -c db_file=db/data.db number_of_events=10000

site-serve:
	python -m http.server -d site

site-commit:
	git -C site add --all
	git -C site commit -m "Site update" || true

site-publish: site-commit
	git -C site push origin gh-pages
