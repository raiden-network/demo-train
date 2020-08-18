.PHONY: start start_mocked test arduino

start: 
	hypercorn 'webserver:build_app(config_file="raiden_config.toml")'

start_mocked:
	hypercorn 'webserver:build_app(mock="raiden arduino", config_file="raiden_config.toml")'

test:
	pytest tests/ --ignore tests/test_e2e.py

arduino:
	arduino-cli compile --fqbn Intel:arc32:arduino_101 arduino/track_control/
	arduino-cli upload -p /dev/ttyACM0 --fqbn Intel:arc32:arduino_101 arduino/track_control/
