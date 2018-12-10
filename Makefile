# Shortcut for Linux system.
re:
	@echo '-----------isort-----------'
	@python3 setup.py isort
	@echo '-----------flake8-----------'
	@python3 setup.py flake8
	@echo '-----------Test-------------'
	@python3 setup.py test