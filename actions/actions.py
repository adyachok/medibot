import asyncio
import logging
import re
from typing import Any, Text, Dict, List
import phonenumbers

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, FormValidationAction


logger = logging.getLogger(__name__)

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_reschedule_session"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'session':
                dispatcher.utter_message(text="Your session rescheduled!")
            else:
                dispatcher.utter_message(
                    text='Could you please repeat what you\'re would like?')
        return []


class ValidateReschedulingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reschedule_session_form"

    def validate_first_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value and len(value) > 1:
            return {"first_name": value}
        else:
            dispatcher.utter_message(template="utter_no_first_name")
            return {"first_name": None}

    def validate_last_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value and len(value) > 1:
            return {"last_name": value}
        else:
            dispatcher.utter_message(template="utter_no_last_name")
            return {"last_name": None}

    def validate_phone_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if type(value) == list:
            value = ' '.join(value)
        is_value_ok, phone = self._is_phone_number_valid(value)
        if is_value_ok:
            return {"phone_number": f'+{phone.country_code}{phone.national_number}'}
        else:
            dispatcher.utter_message(template="utter_no_phone_number")
            return {"phone_number": None}

    def _is_phone_number_valid(self, value):
        phone = None
        if value:
            try:
                # phonenumbers.parse(value, 'MX')
                phone = phonenumbers.parse(value, 'DE')
                return True, phone
            except phonenumbers.phonenumberutil.NumberParseException:
                logger.error(f'Cannot parse numner {value}')
        return False, phone


class ActionSubmitRescheduleSessionForm(Action):

    def name(self) -> Text:
        return "action_submit_reschedule_session"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        first_name = tracker.get_slot('first_name')
        last_name = tracker.get_slot('last_name')
        phone_number = tracker.get_slot('phone_number')
        logger.debug(f'Checking user {first_name} {last_name} with phone {phone_number} in DB.')
        dispatcher.utter_message(
                    text='Please, wait looking for possible options.')
        await asyncio.sleep(3)
        dispatcher.utter_message(
                    text='You session rescheduled.')
        return [SlotSet('first_name', None), SlotSet('last_name', None), SlotSet('phone_number', None)]