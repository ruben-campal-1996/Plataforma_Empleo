from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests
import json
import os

# Configurar la API de Hugging Face
HF_API_KEY = os.getenv('HF_API_KEY')
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-7B-Instruct-v0.2"
print("Hugging Face API Key cargada:", HF_API_KEY[:5] + "..." if HF_API_KEY else "No encontrada")
print("Hugging Face API URL:", HF_API_URL)

@login_required
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            print("Mensaje recibido:", user_message)

            # Guardar mensaje del usuario en la sesión
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'text': user_message, 'is_user': True})
            
            # Llamar a la API de Hugging Face
            headers = {
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            }
            prompt = f"<s>[INST] Actúa como un asistente útil para una plataforma de búsqueda de empleo. Responde a: {user_message} [/INST]"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,  # Cambiado a max_new_tokens para Mixtral
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            print("Enviando solicitud a Hugging Face:", HF_API_URL)
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            print("Respuesta cruda de la API:", response.text)

            # Extraer la respuesta
            bot_response = response.json()[0]['generated_text'].strip()
            print("Respuesta del modelo:", bot_response)

            # Guardar respuesta del bot en la sesión
            chat_history.append({'text': bot_response, 'is_user': False})
            request.session['chat_history'] = chat_history

            return JsonResponse({'response': bot_response})
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP en la vista chat: {str(e)}")
            return JsonResponse({'error': f"Error al conectar con la API: {str(e)}"}, status=500)
        except KeyError as e:
            print(f"Error de formato en la respuesta de la API: {str(e)}")
            return JsonResponse({'error': f"Formato de respuesta inesperado: {str(e)}"}, status=500)
        except Exception as e:
            print(f"Error en la vista chat: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def get_chat_history(request):
    chat_history = request.session.get('chat_history', [])
    return JsonResponse({'chat_history': chat_history})