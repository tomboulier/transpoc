import os
import openai
from dotenv import load_dotenv

# Chargez les variables d'environnement à partir du fichier .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def map_with_llm(prompt: str) -> str:
    """Requête simple à l’API OpenAI pour retourner un code."""
    resp = openai.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role":"user","content": prompt}],
      temperature=0
    )
    message_content = resp.choices[0].message.content
    if not message_content:
        return ""
    else:
        return message_content.strip()

if __name__ == "__main__":
    for antecedent in ["Diabète de type 2",
                       "DT2",
                       "Hypertension artérielle",
                       "HTA",
                       "Asthme",
                       "Hypercholestérolémie",
                       "Maladie coronarienne",
                       "Insuffisance cardiaque",
                       "Cancer du sein",
                       "Cancer de la prostate",
                       "Broncho-pneumopathie chronique obstructive (BPCO)",
                       "BPCO",
                       "Hypertrophie bénigne de la prostate (HBP)",
                       "HBP",
                       ]:
        prompt = f"Donne-moi le code CIM-10 pour '{antecedent}'. Réponds uniquement avec le code CIM-10."
        code = map_with_llm(prompt)
        print(f"{antecedent}: {code}")
