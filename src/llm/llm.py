import litellm

class LLM:
    def call_model(
        self,
        provider : str,
        model : str,
        temperature : float,
        prompt_dict : list[dict[str, str]],
    ) -> str:
        """
        Appelle le modèle de langage pour générer une réponse.
        """
        response: litellm.ModelResponse = self._generate(
            provider, model, temperature, prompt_dict=prompt_dict
        )
        response_text = str(response.choices[0].message.content)
        
        return response_text

    def _generate(
        self,
        provider : str,
        model : str,
        temperature : float,
        prompt_dict : list[dict[str, str]],
    ) -> litellm.ModelResponse:
        """
        Génère une réponse à partir des prompts donnés.
        """
        response = litellm.completion(
            model=f"{provider}/{model}",
            messages=prompt_dict,
            temperature=temperature
        )
        return response
