import yaml # needed for context

import meshtastic # needed for meshtastic
import meshtastic.serial_interface # needed for physical connection to meshtastic
from pubsub import pub # needed for meshtastic connection

import time # needed for sleep
import datetime # needed for finding day of the week

from ollama import chat # needed for LLM
from ollama import ChatResponse # needed for LLM

class VillageBot:
    """
    Class to handle village chatbot
    """

    def __init__(self):
        """
        Initialization method
        """

        print("Opening context file")

        with open("./context.yaml", 'r') as ymlfile:
            context = yaml.safe_load(ymlfile)

        # The model we will be using
        self.llmModel = context["model_choice"]

        # the channel to broadcast on
        self.broadcastChannel = int(context['broadcast_channel_index'])

        # our universal personality
        self.personality = context['llm_personality']

        # context for everything going on Monday
        self.monday = context['monday_context']

        # context for everything going on Tuesday
        self.tuesday = context['tuesday_context']

        # context for everything going on Wednesday
        self.wednesday = context['wednesday_context']

        # context for everything going on Thursday
        self.thursday = context['thursday_context']

        # context for everything going on Friday
        self.friday = context['friday_context']

        # context for everything going on Saturday
        self.saturday = context['saturday_context']

        # context for everything going on Sunday
        self.sunday = context['sunday_context']

        # context to handle formating
        self.constraints = 'Keep your messages short and concise.  Do not use more than 200 characters and avoid any complex formatting or instructions.  Do not respond in any way other than text'

        # set up meshtastic threads, note only responding to text messages
        pub.subscribe(self.onReceive, "meshtastic.receive.text")
        pub.subscribe(self.onConnection, "meshtastic.connection.established")

        # The mestastic interface we will use for comms
        self.interface = meshtastic.serial_interface.SerialInterface(context['meshtastic_serial_port'])


    def onReceive(self, packet, interface):
        """
        Handles reciving and responding to messages

        Args:
            packet (_type_): _description_
            interface (_type_): _description_
        """

        #print(f"\nGot Message:\n{packet}")

        if 'channel' in packet:
            #print("Broadcast message")
            # TODO: Decide if we want to let the bot interact with channel messages too
            pass
        else: # Message was a direct message
            message = packet['decoded']['text'].strip()

            # get day of the week context
            dayContext = ""
            date = datetime.date.today().weekday()

            if date == 0: #Monday
                dayContext = self.monday
            elif date == 1: # Tuesday
                dayContext = self.tuesday
            elif date == 2: # Wednesday
                dayContext = self.wednesday
            elif date == 3: # Thursday
                dayContext = self.thursday
            elif date == 4: # Friday
                dayContext = self.friday
            elif date == 5: # Saturday
                dayContext = self.saturday
            elif date == 6: # Sunday
                dayContext = self.sunday
            else:
                print("Error, something weird with day of the week from datetime")

            response: ChatResponse = chat(model=self.llmModel, messages=[
                {"role": "system", "content": f"{str(self.personality)}"},
                {"role": "system", "content": f"{str(dayContext)}"},
                {"role": "system", "content": f"{str(self.constraints)}"},
                {"role": "system", "content": f"Given the above info, do your best to respond appropriately to the following user message:"},
                {"role": "user", "content": message}
            ])

            print(response.message.content)
            self.interface.sendText(f"{response.message.content}", destinationId=packet["from"])


    def onConnection(self, interface, topic=pub.AUTO_TOPIC): 
        """
        Called when connection or reconnecting

        Args:
            interface (obj):The meshtastic interface object
            topic (_type_, optional): _description_. Defaults to pub.AUTO_TOPIC.
        """

        print(f"Connected to device")

        # get day of the week context
        dayContext = ""
        date = datetime.date.today().weekday()

        if date == 0: #Monday
            dayContext = self.monday
        elif date == 1: # Tuesday
            dayContext = self.tuesday
        elif date == 2: # Wednesday
            dayContext = self.wednesday
        elif date == 3: # Thursday
            dayContext = self.thursday
        elif date == 4: # Friday
            dayContext = self.friday
        elif date == 5: # Saturday
            dayContext = self.saturday
        elif date == 6: # Sunday
            dayContext = self.sunday
        else:
            print("Error, something weird with day of the week from datetime")
        
        response: ChatResponse = chat(model=self.llmModel, messages=[
            {"role": "system", "content": f"{str(self.personality)}"},
            {"role": "system", "content": f"{str(dayContext)}"},
            {"role": "system", "content": f"{str(self.constraints)}"},
            {"role": "user", "content": f"Announce that you are online and do a quick intro of yourself.  "},

        ])

        print(response.message.content)
        self.interface.sendText(f"{response.message.content}", channelIndex=self.broadcastChannel)


if __name__ == "__main__":

    print("Starting Village Chatbot")
    bot = VillageBot()

    while True:
        time.sleep(1)