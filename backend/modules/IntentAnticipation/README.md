# extremexp-prototype
## System Architecture

The prototype is designed as a multi-server communication system, where users interact with the main application, which is hosted and executed by the **web_app server**.


The **llm server** is accessed by the main app, which sends user-inputted text for processing. This text is classified by a specific LLM into an analytical intent, which is then presented to the user within the main app.

### Store your API keys
Make sure you have ```.env``` file in the **llm folder** with your API keys stored.
  ```
  OPENAI_API_KEY=<YOUR OPENAI_API_KEY>
  LlamaAPI_KEY=<LlamaAPI_KEY>
  ```
For more information on how to obtain API Keys, refer to : [OpenAI](https://platform.openai.com/docs/quickstart) and [LLama AI](https://docs.llama-api.com/api-token).


### Adding New Functionalities to the Existing Servers

Adding new functionalities can be achieved in the same manner: 

1. **Add a New Function**: Create a new function in the `utils` module.

2. **Import the Function**: Import this function into the API script of the server.

3. **Define a New Route**: In the API script, define a new route that uses the imported function.

4. **Update the Main App**: In the main application, add a new route that makes requests to the server using the new endpoint you defined.
