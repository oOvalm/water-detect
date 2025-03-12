import logging

def set_module_log_level(module_name, level=logging.ERROR):
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    for name, logger_obj in logging.Logger.manager.loggerDict.items():
        # print(name)
        if isinstance(logger_obj, logging.Logger) and name.startswith(module_name + '.'):
            logger_obj.setLevel(level)