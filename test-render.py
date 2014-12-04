import boxmaker, logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

#boxmaker.render("tmp/test.pdf",101.6,127.00001,152.4,4.7625,0.0,11.90625,True)
boxmaker.render("tmp/test.pdf",95.25,76.2,76.2,3.048,0.0,7.62,True)
