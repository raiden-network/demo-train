start: 
	hypercorn 'webserver:build_app(config_file="raiden_config.toml")'

start_mocked:
	hypercorn 'webserver:build_app(mock="raiden arduino", config_file="raiden_config.toml")'

test:
	pytest tests/ --ignore tests/test_e2e.py
