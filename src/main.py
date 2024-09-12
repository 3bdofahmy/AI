from fastapi import FastAPI
from routes import base , data ,nlp
from helpers.config import get_settings
from stores.LLM.LLMProvideFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.LLM.templates.template_parser import TemplateParser
import uvicorn
from pyngrok import ngrok


app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)



settings = get_settings()


llm_provider_factory = LLMProviderFactory(settings)
vectordb_provider_factory = VectorDBProviderFactory(settings)


    # generation client
app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
app.vectordb_client.connect()    

app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )
    

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)

NGROK_AUTH = settings.NGROK_AUTH
port = settings.NGROK_port
ngrok.set_auth_token(NGROK_AUTH)
tunnel = ngrok.connect(port ,domain="closing-insect-tough.ngrok-free.app")
print("puplic Ip :" ,tunnel.public_url) 

