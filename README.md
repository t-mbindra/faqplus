# FAQBot

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=829777713&devcontainer_path=.devcontainer%2Fdevcontainer.json&resume=1)

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

## Setting up the app in Github Codespaces

1. Click Open in GitHub Codespaces badge above to create a codespace for the sample app. Wait for the codespace to be setup, it may take a couple of minutes.
2. Using the Teams Toolkit extension, sign in to your Microsoft 365 account and Azure account under ```ACCOUNTS```.
3. Deploy [Azure AI resources](#deploy-azure-ai-resources)
4. Deploying locally:
   Press **Ctrl+Shift+D** to open the ```Run and Debug``` menu. Select ```Debug``` and press ```F5``` or click on the play button.
   Download the zip file ```appPackage/build/appPackage.local.zip``` and [sideload the app to Teams personal chat](#sideloading-the-app-to-teams-personal-chat) and  [sideload the app to Teams Channel](#sideloading-the-app-to-teams-channel)
5. Alternatively, deploy the app to Azure:
   Using the Teams Toolkit Extension tab, click on ```Provision``` followed by ```DEPLOY``` under ```LIFECYCLE```.
   Download the zip file ```appPackage/build/appPackage.dev.zip``` and [sideload the app to Teams personal chat](#sideloading-the-app-to-teams-personal-chat)  and  [sideload the app to Teams Channel](#sideloading-the-app-to-teams-channel)

## Setting up the app locally

1. Clone the repository
   ```git clone https://github.com/t-mbindra/faqplus.git```
2. Install [Python 3.12](https://www.python.org/downloads/), [Node.js](https://nodejs.org/) and [Rust](https://www.rust-lang.org/tools/install).
4. Install  [Poetry](https://python-poetry.org/docs/#installation) and [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
5. Open the project folder in [Visual Studio Code](https://code.visualstudio.com/download).
6. Install the [Teams Toolkit](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.ms-teams-vscode-extension) and [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extensions.
8. Run
   ```poetry install```
9. Run
   ```poetry build```
10. Deploy [Azure AI resources](#deploy-azure-ai-resources). This only needs to be done once.
11. Using the Teams Toolkit extension, sign in to your Microsoft 365 account and Azure account under ```ACCOUNTS```.
12. Deploying locally:
   Press **Ctrl+Shift+D** to open the ```Run and Debug``` menu. Press ```F5``` or click on the play button. Also, [sideload the app to Teams Channel](#sideloading-the-app-to-teams-channel)
14. Alternatively, deploy the app to Azure:
    Using the Teams Toolkit Extension tab, click on ```Provision``` followed by ```DEPLOY``` under ```LIFECYCLE```.
    Using the zip file ```appPackage/build/appPackage.dev.zip```, [sideload the app to Teams personal chat](#sideloading-the-app-to-teams-personal-chat) and [sideload the app to Teams Channel](#sideloading-the-app-to-teams-channel)

## Deploy Azure AI Resources
1. Run```sh deploy.sh``` in the terminal. You will be prompted to login to Azure and select a subscription.
3. Populate the ```SECRET_AZURE_OPENAI_KEY, SECRET_AZURE_OPENAI_ENDPOINT``` variables from the [Azure portal](https://ms.portal.azure.com/) in the ```env/.env.local.user``` file or ```env/.env.dev.user``` file according to environment.

## Sideloading the app to Teams Personal Chat:
1. Go to your Teams app and click on the ```Apps``` icon. Select ```Manage your apps``` followed by ```Upload an app```.
2. Select ```Upload a custom app``` and open the relevant zip file. Click on ```Add``` when prompted.

## Sideloading the app to Teams Channel:
1. Go to the channel where you want to raise requests for help. Click on the ```Apps``` icon. Select ```Got more apps``` followed by ```Manage your apps```.
2. Click on ```Upload an app``` and open the relevant zip file.  Click on ```Add``` when prompted. Select the correct channel and click on ```Go```

>[!Note]
> Check the status of all your local bots on [Microsoft Bot Framework](https://dev.botframework.com/bots).
> Check the status of all your Teams apps on [Teams Developer Portal](https://dev.teams.microsoft.com/apps).
> Check the status of all Azure resources on [Azure Portal](https://portal.azure.com/#home) by navigating to the relevant resource group.

> If you do not have permission to upload custom apps (sideloading), Teams Toolkit will recommend creating and using a Microsoft 365 Developer Program account - a free program to get your own dev environment sandbox that includes Teams.
