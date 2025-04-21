from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests
import json
import os

# Configurar la API de Hugging Face
HF_API_KEY = os.getenv('HF_API_KEY')
HF_API_URL = "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"
print("Hugging Face API Key cargada:", HF_API_KEY)
if not HF_API_KEY:
    print("Error: No se encontró HF_API_KEY en las variables de entorno")

@login_required
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Guardar mensaje del usuario en la sesión
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'text': user_message, 'is_user': True})
            
            # Llamar a la API de Hugging Face
            headers = {
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            }
            # Formato del prompt para Mistral
            prompt = f"<s>[INST] Actúa como un asistente útil para una plataforma de búsqueda de empleo. Responde a: {user_message} [/INST]"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "return_full_text": False  # Evita que el prompt se incluya en la respuesta
                }
            }
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            # Extraer la respuesta (Mistral devuelve una lista con un diccionario)
            bot_response = response.json()[0]['generated_text'].strip()

            # Guardar respuesta del bot en la sesión
            chat_history.append({'text': bot_response, 'is_user': False})
            request.session['chat_history'] = chat_history

            return JsonResponse({'response': bot_response})
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP en la vista chat: {str(e)}")
            return JsonResponse({'error': f"Error al conectar con la API: {str(e)}"}, status=500)
        except Exception as e:
            print(f"Error en la vista chat: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def get_chat_history(request):
    chat_history = request.session.get('chat_history', [])
    return JsonResponse({'chat_history': chat_history})