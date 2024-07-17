"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

from botbuilder.core import CardFactory
from botbuilder.schema import Attachment


def create_ai_response_card(ai_content) -> Attachment:
    return CardFactory.adaptive_card(
        {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5",
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": ai_content,
                    "wrap": True,
                    "weight": "Bolder",
                    "spacing": "small"
                },
                {
                    "type": "ActionSet",
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Talk to an Expert",
                            "data": {"verb": "expert"},
                            "spacing": "small",
                            "padding": "None"
                        }
                    ],
                    "spacing": "Small",
                    "padding": "None"             
                }
            ],
            "padding": "None"
        }
    )