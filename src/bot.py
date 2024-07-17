"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.

Description: initialize the app and listen for `message` activitys
"""

import os
import sys
import traceback
import re
from logging import Logger, StreamHandler, DEBUG

from botbuilder.core import MemoryStorage, TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.schema import Activity, ConversationParameters
from botbuilder.schema.teams import TeamsChannelData, ChannelInfo
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.ai.models import AzureOpenAIModelOptions, OpenAIModel
from teams.ai.planners import ActionPlanner, ActionPlannerOptions
from teams.ai.prompts import PromptManager, PromptManagerOptions
from teams.ai.data_sources import TextDataSource
from azure.identity import get_bearer_token_provider, DefaultAzureCredential

from config import Config
from state import AppTurnState
from cards.ai_response_card import create_ai_response_card
from cards.talk_to_expert_card import create_talk_to_expert_card
from cards.close_request_card import close_request_card

logger = Logger("teamsai:openai", DEBUG)
logger.addHandler(StreamHandler(sys.stdout))

config = Config()

if config.AZURE_OPENAI_ENDPOINT is None:
    raise RuntimeError("Missing environment variables - please check that AZURE_OPENAI_ENDPOINT is set.")

# Create AI components
model: OpenAIModel
logger = Logger("teamsai:openai", DEBUG)
logger.addHandler(StreamHandler(sys.stdout))

if config.AZURE_OPENAI_KEY:
    model = OpenAIModel(
        AzureOpenAIModelOptions(
            api_key=config.AZURE_OPENAI_KEY,
            default_model='gpt-35-turbo',
            api_version="2024-02-15-preview",
            endpoint=config.AZURE_OPENAI_ENDPOINT,
            logger=logger
        )
    )
else: 
    model = OpenAIModel(
        AzureOpenAIModelOptions(
            azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), 'https://cognitiveservices.azure.com/.default'),
            default_model='gpt-35-turbo',
            api_version="2024-02-15-preview",
            endpoint=config.AZURE_OPENAI_ENDPOINT,
            logger=logger
        )
    )

def read_database() -> str:
    """
    Read data from database files and convert it to a string.
    """

    combined_data_str = ''

    database_folder = f"{os.path.dirname(os.path.abspath(__file__))}/data"
    for filename in os.listdir(database_folder):
        file_path = os.path.join(database_folder, filename)
        with open(file_path, 'r') as file:
            data = file.read()
            combined_data_str += data + "\n"

    return combined_data_str

prompts = PromptManager(
    PromptManagerOptions(prompts_folder=f"{os.path.dirname(os.path.abspath(__file__))}/prompts"),
)

prompts = prompts.add_data_source(TextDataSource("files", read_database()))

storage = MemoryStorage()
app = Application[AppTurnState](
    ApplicationOptions(
        bot_app_id=config.APP_ID,
        storage=storage,
        adapter=TeamsAdapter(config)
    )
)

planner=ActionPlanner(ActionPlannerOptions(model=model, prompts=prompts, default_prompt="chat"))


@app.conversation_update("membersAdded")
async def on_member_added(context: TurnContext, state: AppTurnState):

    channel = context.activity.channel_data.get("settings", {}).get("selectedChannel", {}).get("id")  # type: ignore

    if (context.activity.members_added[0].id == context.activity.recipient.id and  # type: ignore
        channel == "19:NbZrm0QGDBalb7yQtQ5uu_fKf5LRTJcILRxkarAVDs41@thread.tacv2"):
        await context.send_activity("The FAQ Bot has been added to this channel.")
        return True
    
    member_added_to_channel = context.activity.channel_data.get("team") # type: ignore
    
    if (member_added_to_channel is None): 
        await context.send_activity(
            "Welcome to the FAQ Bot ! I'm here to answer your queries. To clear the conversation history, type clear in the chat."
            )
    
    return True


@app.activity("message")
async def on_message(context: TurnContext, state: AppTurnState):

    if context.activity.text and not re.match(r"clear", context.activity.text, re.IGNORECASE):
        response = await planner.complete_prompt(context, state, "chat")

        if response.status != "success":
            raise Exception(f"The request to OpenAI had the following error: {response.error}")
        if response.message is None:
            raise Exception("The response message is None")
        
        attachment = create_ai_response_card(response.message.content)
        await context.send_activity(Activity(attachments=[attachment]))

    return True


@app.message(re.compile(r"clear", re.IGNORECASE))
async def on_clear(context: TurnContext, state: AppTurnState):

    del state.conversation
    await context.send_activity(
        "New chat session started: Previous messages won't be used as context for new queries."
    )
    return True

def get_chat_history(chat_history):
    chat_items = []

    if chat_history:
        # Limit the chat history to the last 10 entries
        limited_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

        for entry in limited_history:
            role = entry.role.capitalize()
            content = entry.content
            chat_items.append(
                {
                    "type": "TextBlock",
                    "text": f"{role}: {content}",
                    "wrap": True,
                    "spacing": "small"
                }
            )

    return chat_items

def create_teams_channel_data(team_channel_id: str):
    channel_data = TeamsChannelData()
    channel_data.channel = ChannelInfo()
    channel_data.channel.id = team_channel_id
    return channel_data

async def do_nothing(tc2: TurnContext):
    return

@app.adaptive_cards.action_submit("expert")
async def on_talk_to_an_expert(context: TurnContext, state: AppTurnState, data: dict):

    print(context.activity)
    print(context.activity.conversation.id)

    member = await TeamsInfo.get_member(context, context.activity.from_property.id)  # type: ignore
    attachment = create_talk_to_expert_card(
                    member.user_principal_name, context.activity.from_property.name, # type: ignore
                    get_chat_history(state.conversation.get("chat_history")), "New"
    )

    params = ConversationParameters(
        channel_data=create_teams_channel_data('19:NbZrm0QGDBalb7yQtQ5uu_fKf5LRTJcILRxkarAVDs41@thread.tacv2'),
        bot=context.activity.recipient, is_group=True,
        activity=Activity(type="message",attachments=[attachment]))
    
    await context.adapter.create_conversation(bot_app_id=config.APP_ID,
        callback=do_nothing,
        conversation_parameters = params,
        channel_id="msteams",
        service_url=context.activity.service_url)
        
    # Send the message to the user
    await context.send_activity("I'm connecting you to an expert. In the meantime, would you like to ask me anything else?")


@app.adaptive_cards.action_submit("chat_with_user")
async def on_chat_with_user(context: TurnContext, state: AppTurnState, data: dict):

    attachment = create_talk_to_expert_card(data.get("user_principal_name"), data.get("user_name"),
                                             data.get("chat_items"), "In progress")
    await context.update_activity(Activity(id=context.activity.reply_to_id, 
                                           type="message", attachments=[attachment]))
    
    if "messageid" not in context.activity.conversation.id: # type: ignore
        custom_string = f"{context.activity.channel_data.get('channel').get('id')};messageid={context.activity.reply_to_id}"  # type: ignore
        context.activity.conversation.id = custom_string  # type: ignore

    await context.send_activity(Activity(type="message", 
                                         text=f"{context.activity.from_property.name} is resolving the request.")) # type: ignore


@app.adaptive_cards.action_submit("close_ticket")
async def on_close_ticket(context: TurnContext, state: AppTurnState, data: dict):

    attachment = close_request_card(data.get("user_name"),  data.get("chat_items"))  # type: ignore
    await context.update_activity(Activity(id=context.activity.reply_to_id, 
                                        type="message", attachments=[attachment]))
    if "messageid" not in context.activity.conversation.id:   # type: ignore
        custom_string = f"{context.activity.channel_data.get('channel').get('id')};messageid={context.activity.reply_to_id}"  # type: ignore
        context.activity.conversation.id = custom_string  # type: ignore
    await context.send_activity(f"{context.activity.from_property.name} closed the request.") # type: ignore

@app.turn_state_factory
async def turn_state_factory(context: TurnContext):
    return await AppTurnState.load(context, storage)


@app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
