import base64
import os
from openai import OpenAI
import streamlit as st

# Function to encode the image to base64
def encode_image(image_file):
  return base64.b64encode(image_file.getvalue()).decode("utf-8")


# Streamlit page setup
st.set_page_config(
    page_title="Análisis de Imagen",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Header Title
st.title("Análisis de Imagen 🤖🏞️")
st.caption(
    "Suba una imagen y consulte detalles o contexto en tiempo real con GPT-4o Vision"
)

# Sidebar setup for API Key and instructions
with st.sidebar:
  st.header("⚙️ Configuración")
  ke = st.text_input(
      "Ingresa tu Clave de OpenAI", type="password", help="Tu API Key de OpenAI"
  )
  if ke:
    os.environ["OPENAI_API_KEY"] = ke
    st.success("API Key cargada", icon="🔑")
  else:
    st.warning("Por favor ingresa tu API key.")

  st.markdown("---")
  st.markdown(
      "**Instrucciones:**\n1. Ingresa tu API Key.\n2. Sube una imagen"
      " (JPG/PNG).\n3. Activa preguntas específicas si necesitas context"
      " extra.\n4. Haz clic en **Analizar la imagen**."
  )

# Retrieve the OpenAI API Key from secrets / environment
api_key = os.environ.get("OPENAI_API_KEY", "")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key) if api_key else None

# File uploader section
uploaded_file = st.file_uploader(
    "Sube tu imagen aquí", type=["jpg", "png", "jpeg"]
)

if uploaded_file:
  with st.expander("🖼️ Vista previa de la imagen", expanded=True):
    st.image(
        uploaded_file, caption=uploaded_file.name, use_container_width=True
    )

st.markdown("---")

# Toggle for showing additional details input
show_details = st.toggle(
    "❓ Pregunta algo específico sobre la imagen", value=False
)

additional_details = ""
if show_details:
  additional_details = st.text_area(
      "Adiciona contexto de la imagen aquí:",
      placeholder="Ej. ¿Qué tipo de planta es esta? / ¿Qué texto dice en el cartel?",
      disabled=not show_details,
  )

# Button to trigger the analysis
analyze_button = st.button("🚀 Analiza la imagen", type="primary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

  with st.spinner("Analizando la imagen con GPT-4o..."):
    # Encode the image
    base64_image = encode_image(uploaded_file)

    prompt_text = "Describe what you see in the image in spanish"

    if show_details and additional_details:
      prompt_text += (
          f"\n\nAdditional Context Provided by the User:\n{additional_details}"
      )

    # Create the payload for the completion request - CORRECTED FORMAT
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt_text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                },
            },
        ],
    }]

    # Make the request to the OpenAI API
    try:
      st.markdown("### 📝 Resultado del Análisis:")
      result_container = st.container(border=True)
      with result_container:
        full_response = ""
        message_placeholder = st.empty()
        for completion in client.chat.completions.create(
            model="gpt-4o", messages=messages, max_tokens=1200, stream=True
        ):
          # Check if there is content to display
          if completion.choices[0].delta.content is not None:
            full_response += completion.choices[0].delta.content
            message_placeholder.markdown(full_response + "▌")
        # Final update to placeholder after the stream ends
        message_placeholder.markdown(full_response)

    except Exception as e:
      st.error(f"An error occurred: {e}")
else:
  # Warnings for user action required
  if not uploaded_file and analyze_button:
    st.warning("Please upload an image.")
  if not api_key and analyze_button:
    st.warning("Por favor ingresa tu API key.")
