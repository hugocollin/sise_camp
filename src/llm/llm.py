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


    def generate_prompt_embedding(self, prompt: str) -> list[float]:
        """
        Génère un embedding pour le prompt en utilisant le modèle 'mistral-embed'.
        """
        model = "mistral/mistral-embed"
        response = litellm.embedding(model=model, input=[prompt])
        return response["data"][0]["embedding"]

    def generate_chunks_embeddings(self, chunk_list: list[tuple]) -> list[tuple]:
        """
        Génère des embeddings pour chaque chunk dans chunk_list.
        Chaque chunk est une liste de tokens, et un embedding est généré pour chaque liste.
        Retourne une liste de tuples (id_chunk, embedding).
        """
        embeddings_with_ids = []

        for chunk in chunk_list:
            # Chaque chunk est un tuple (id, list of tokens)
            chunk_id, chunk_tokens = chunk

            # Joindre les tokens en une chaîne de texte
            prompt = " ".join(chunk_tokens)

            # Utiliser la fonction generate_prompt_embedding pour obtenir l'embedding
            embedding = self.generate_prompt_embedding(prompt)

            # Ajouter un tuple (chunk_id, embedding) à la liste
            embeddings_with_ids.append((chunk_id, embedding))

        return embeddings_with_ids
