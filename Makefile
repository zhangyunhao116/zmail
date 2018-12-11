# Shortcut for Linux system.
re: .install_dev
	@echo '-----------isort-----------'
	@python3 setup.py isort
	@echo '-----------flake8-----------'
	@python3 setup.py flake8
	@echo '-----------Test-------------'
	@python3 setup.py test

.install_dev:
	@pip3 install isort
	@pip3 install flake8