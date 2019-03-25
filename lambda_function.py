# -*- coding: utf-8 -*-
import sys
import random
import logging
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from datetime import datetime
now = datetime.now() # current date and time
todayDateStamp = now.strftime("%Y-%m-%d")
monthDateStamp = now.strftime("%Y-%m-01")


# =========================================================================================================================================
# TODO: SETUP YOUR DATABASE CONNECTION
# You will need to modify the connection strings to connect to your database
# if you have changed your Wordpress prefix from wp_ then you will need to update the rds_db_table value
# =========================================================================================================================================
rds_host  = "YOUR DATABASE CONNECTION STRING"
rds_username = "YOUR DATABASE USERNAME"
rds_password = "YOUR DATABASE PASSWORD"
rds_db_name = "YOUR DATABASE NAME"
rds_db_table = 'wp_posts'

# =========================================================================================================================================
# TODO: Check the queries
# These queries will count published posts only. You can modify the queries to count custom post types... such as orders
# =========================================================================================================================================
dataQuery = "select COUNT(ID) from "+rds_db_table+" P where P.post_type = 'posts' and P.post_status = 'publish' and P.post_date > '%s'"%todayDateStamp
monthDataQuery = "select COUNT(ID) from "+rds_db_table+" P where P.post_type = 'posts' and P.post_status = 'publish' and P.post_date > '%s'"%monthDateStamp


# =========================================================================================================================================
# TODO: The items below this comment need your attention.
# Customize the responses according to the post type you are counting
# =========================================================================================================================================
DAY_TEXT = 'New posts today'
MONTH_TEXT = 'Posts this month'
SKILL_NAME = "Today's Post Count"
HELP_MESSAGE = "You can say how many new posts, or, you can say exit... What can I help you with?"
HELP_REPROMPT = "What can I help you with?"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "The New Post Count skill can't help you with that.  It can tell you how many posts were created today if you say how many new posts. What can I help you with?"
FALLBACK_REPROMPT = 'What can I help you with?'
EXCEPTION_MESSAGE = "Sorry. I cannot help you with that."


# =========================================================================================================================================
# Editing below here may break the function
# =========================================================================================================================================
class DataCounter:
    def __init__(self, rds_host,rds_username,rds_password,rds_db_name,dataQuery,monthDataQuery):
        self.rds_host = rds_host
        self.rds_username = rds_username
        self.rds_password = rds_password
        self.rds_db_name = rds_db_name
        self.dataQuery = dataQuery
        self.monthDataQuery = monthDataQuery
    def getData(self):
        try:
            conn = pymysql.connect(self.rds_host, user=self.rds_username, passwd=self.rds_password, db=self.rds_db_name, connect_timeout=5)
        except:
            logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
            return "ERROR: Unexpected error: Could not connect to MySQL instance. Please try again later"

        else:
            logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

            with conn.cursor() as cur:
                logger.info("QUERY: %s"%self.dataQuery)
                cur.execute(self.dataQuery)
                cur.fetchall()
                orderCount = cur.rowcount
                logger.info("MONTHQUERY: %s"%self.monthDataQuery)
                cur.execute(self.monthDataQuery)
                cur.fetchall()
                monthOrderCount = cur.rowcount
            conn.commit()
            return ""+DAY_TEXT+": %s "%orderCount + " . "+MONTH_TEXT+":  %s"%monthOrderCount

dc = DataCounter(rds_host,rds_username,rds_password,rds_db_name,dataQuery,monthDataQuery)


# =========================================================================================================================================
# Editing anything below this line might break your skill.
# =========================================================================================================================================


from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response


sb = SkillBuilder()

# Built-in Intent Handlers
class GetCountHandler(AbstractRequestHandler):
    """Handler for Skill Launch and GetCount Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("GetCount")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetCountHandler")


        speech = dc.getData()

        handler_input.response_builder.speak(speech).set_card(
            SimpleCard(SKILL_NAME, speech))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(GetCountHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
