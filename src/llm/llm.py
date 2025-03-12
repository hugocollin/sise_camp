"""
Ce fichier contient le module pour gérer les modèles de langage.
"""

import litellm

class LLM:
    """
    Classe pour gérer les modèles de langage.
    """
    def call_model(
        self,
        provider : str,
        model : str,
        temperature : float,
        prompt_dict : list[dict[str, str]],
    ) -> str:
        """
        Appelle le modèle de langage pour générer une réponse.

        Args:
            provider (str): Nom du fournisseur.
            model (str): Nom du modèle.
            temperature (float): Température de l'échantillonnage.
            prompt_dict (list): Liste des prompts.

        Returns:
            str: Réponse générée.
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

        Args:
            provider (str): Nom du fournisseur.
            model (str): Nom du modèle.
            temperature (float): Température de l'échantillonnage.
            prompt_dict (list): Liste des prompts.

        Returns:
            litellm.ModelResponse: Réponse générée.
        """
        response = litellm.completion(
            model=f"{provider}/{model}",
            messages=prompt_dict,
            temperature=temperature
        )
        return response
