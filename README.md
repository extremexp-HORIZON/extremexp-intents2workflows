# Intents2Workflows

## Overview
This component executes the translation from user-defined intents to actionable workflows. The user starts the process by defining, on a high level, the analytical task to be executed. I2W extracts the key features from the description and maps it to a rich knowledge base. From there, it chases the dependencies indicated in the ontology to produce workflows to implement the defined task according to the specified intention. These workflows are intially encoded using RDF, which implies a high flexibility to be translated to other representations, such as the DSL required by the execution engine.

## Architectures and Features
The backbone of the project can be found in the *backend/modules* folder, where the two modules that implement the main functionalities can be found (belonging to WP3 and WP4). Besides the backend logic, we provide a frontend for an easy and intuitive interaction with the system. The frontend communicates with the backend via a main API (*backend/api*) that collects the functionalities presented by the two modules.

The *intentAnticipation* module is in charge of anticipating, capturing and processing the user-defined intent. The user defines this intent by indicating the required parameters (type of task, dataset to use, etc.). Then, the system (i) maps the intent to the concepts defined by our knowledge base and (ii) provides recommendations, extracted from past experiments, to the user regarding the definition of the intent. That is, it indicates which are the additional constraints that are recommended to define in order to optimize the workflow (e.g. which is the best algorithm to use). Optionally, the intent can be defined on an even higher-level via natural language, which is processed by LLMs to extract the required elements.

The *IntentSpecification2WorkflowGenerator* module generates, once the intent has been captured, the corresponding workflow. This is done in a series of steps:
1. Data annotation: the data is annotated following the concepts represented in the knowledge base. This allows us to understand the characteristics of the data and provide the appropiate operations to adequately work with them.
2. Abstract plans: the first proposed workflows are very abstract instantions of the pipeline to encode. These include high level tasks that provide a general orientation regarding how to define the workflow. One of these plans is created by each of the algorithms that can be employed for the task. The user has to select at least one of these plans.
3. Logical plans: the abstract plans are mapped to specific workflows where all the necessary tasks to execute the intent cna be found. These plans explore all the potential variability points regarding the needs of the intent, pruning those paths that are deemed less relevant (in order not to bombard the user with too many, indistinguishable alternatives). These are divided by algorithms and specific implementations of these algorithms (e.g. neural networks -> LSTM networks, convolutional networks, etc.). The user selects, at least, one of these plans.
4. Workflow representation: once the definitive list of workflows has been selected, these can be visualized, stored in the system for later use or exported in RDF format. Alternatively, we offer the possibility of directly converting the workflows to the DSL language required by the experimentation engine.


## Repository Structure

```
📁 Project Root  
├── 📁 backend/                                          — Backend source code  
│    └── 📁 api/                                         — API-related code  
│    └── 📁 modules/                                     — Backend submodules   
│         └── 📁 intentAnticipation/                     — Submodule to anticipate, capture and process intents (WP4)
│         └── 📁 IntentSpecification2WorkflowGenerator/  — Submodule to generate the workflows from user's intents (WP3)
├── 📁 frontend/                                         — Frontend source code  
├── 📄 .gitignore                                        — Git ignore rules  
├── 📄 .gitattributes                                    — Git rules to handle files  
├── 📄 LICENSE                                           — Project license  
├── 📄 README.md                                         — Project documentation  
├── 📄 start_apis.bat                                    — Script to easily initiate the system (Windows)  
├── 📄 start_apis.sh                                     — Script to easily initiate the system (Linux) 
```

## Getting Started

### Prerequisites <a name="prerequisites"></a>

Before you begin, ensure that you have the following prerequisites installed:

- [Node.js](https://nodejs.org/) (version 18.20.6)
- [NPM](https://docs.npmjs.com/cli/v8/commands/npm-install) (version >=6.14.12)
- [Yarn](https://classic.yarnpkg.com/lang/en/docs/install/#windows-stable) You can install it using `npm install -g yarn` (or on a macOS install it using Homebrew using `brew install yarn`)
- [Quasar](https://quasar.dev/) (CLI >= 2.0) You can install it using `npm install -g @quasar/cli`

Then, clone the repository:

   ```bash
   git clone https://github.com/dtim-upc/Intents2Workflows.git
   cd Intents2Workflows
   ```
   
### Installation <a name="installation"></a>

Lets ensemble everything to be able to compile and make run the code.

#### Backend <a name="backend-installation"></a>

1. Go to `Intents2Workflows/backend/api`. Install all the required libraries with the following command:

   ```bash
   pip install -r requirements.txt    
   ```

#### Intents modules <a name="intents-installation"></a>
The intent-generation functionalities are separated into two different modules, which can be found in the backend folder. 
1. Go to `Intents2Workflows/modules/IntentSpecification2WorkflowGenerator`. Install all the required libraries with the following command:
   
   ```bash
   pip install -r requirements.txt    
   ```

2. Go to `Intents2Workflows/modules/IntentAnticipation`. Install all the required libraries with the following command:
   
   ```bash
   pip install -r requirements.txt    
   ```

#### Frontend <a name="frontend-installation"></a>

1. Open in the terminal the `Intents2Workflows/frontend` folder.

2. Execute `npm install --force`.

3. Then, execute `yarn install` (on macOS it is possible you need to run `yarn install --ignore-engines`).

### Execution <a name="execution"></a>

We provide two script to easily deploy the system (*start_apis*, in the root folder): one for Windows (*.bat*) and another for Linux (*.sh*). Simply execute the corresponding file regarding your system and both the frontend and all the necessary APIs will be launched (please note the potential error that can be triggered with Quasar; see below).

Alternatively, you can manually launch all the necessary processes.

1. Go to `Intents2Workflows/backend/api`. Launch the main backend API with the following line:

   ```bash
   uvicorn main:app --port=8080     
   ```
2. Go to `Intents2Workflows/modules/IntentSpecification2WorkflowGenerator`. Launch the intent to workflows API with the following line:

   ```bash
   flask --app api\api_main.py run --port=8000
   ```
3. Go to `Intents2Workflows/modules/IntentAnticipation`. Launch the intent capturing APIs (there are two) with the following line:

   ```bash
   python .\start_apis.py  
   ```
4. Go to `Intents2Workflows/frontend`. To launch the frontend execute `quasar dev` (or on a macOS do it from the `node_modules` directory using `node_modules/@quasar/app-vite/bin/quasar dev`. This will open your browser with the URL http://localhost:9000/#/projects.

_Note: that you must have Quasar CLI as it's mentioned in the Prerequisites section. If there's an error like `Global Quasar CLI • ⚠️   Error  Unknown command "dev"`, it's because you are not in the correct path, or you don't have Quasar CLI installed._ 

## Development Process/Roadmap  <a name="Development"></a>
Current Implementation:
- Analytical Intent Capturing
- Recommendation through Knowledge Graph Embeddings (KGE)
- Workflow generation based on user’s input

Future Implementation: 
- Mapping annotated experiments to KG (M28)
- KGE recommendation improvement (KGE dynamic updates) (M30)
- Constraints/Preferences Capturing (M30)
- Considering user’s constraints/preferences when generating the workflows (M30)

## Demo  <a name="Demo"></a>
The following video showcases a demo of the Intents to Workflows component
<div style="text-align: center;">
  <video width="800" controls src="demo_I2W.mp4" title="Title"></video>
</div>

## License  <a name="License"></a>
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details. 

## Contact  <a name="Contact"></a>
For any questions or suggestions, feel free to open an issue or contact the maintainers at [ marc.maynou@upc.edu, gerard.pons.recasens@upc.edu ]