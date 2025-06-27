import configparser

config = configparser.ConfigParser()
config.read("config.ini")

secret_key              = config["config"]["secret_key"]
credentials_username    = config["credentials"]["username"]
credentials_password    = config["credentials"]["password"]
session_timeout         = config["session"]["timeout"]
limiter_limit           = config["limiter"]["limit"]
log_file                = config["files"]["log"]
monitor_file            = config["files"]["monitor"]