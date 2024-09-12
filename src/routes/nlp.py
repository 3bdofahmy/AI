from fastapi import FastAPI, APIRouter, status , Request
from fastapi.responses import JSONResponse
import logging
from routes.schemes.nlp import PushRequest , SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.ProjectModel import Project
from models import ResponseSignal
from controllers.NLPController import NLPController
from models.ProjectModel import ProjectModel
from stores.LLM.LLMEnum import DocumentTypeEnum
import time
import asyncio
import cohere
from cohere.errors import TooManyRequestsError




logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)


# @nlp_router.post("/index/push/{project_id}")
# async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
#     project_model = ProjectModel()
#     Chunkmodel = ChunkModel()


#     project =  project_model.get_project_or_create_one(
#         project_id=project_id
#     )

#     if not project:
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={
#                 "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
#             }
#         )
    
#     nlp_controller = NLPController(
#         vectordb_client=request.app.vectordb_client,
#         generation_client=request.app.generation_client,
#         embedding_client=request.app.embedding_client,
#     )

#     has_records = True
#     page_no = 1
#     inserted_items_count = 0
#     idx = 0

#     while has_records:
#         page_chunks = Chunkmodel.get_project_chunks(project_id=project_id, page_no=page_no)
#         if len(page_chunks):
#             page_no += 1
        
#         if not page_chunks or len(page_chunks) == 0:
#             has_records = False
#             break

#         chunks_ids =  list(range(idx, idx + len(page_chunks)))
#         idx += len(page_chunks)
        
#         is_inserted = nlp_controller.index_into_vector_db(
#             project=project,
#             chunks=page_chunks,
#             do_reset=push_request.do_reset,
#             chunks_ids=chunks_ids
#         )

#         if not is_inserted:
#             return JSONResponse(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 content={
#                     "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
#                 }
#             )
        
#         inserted_items_count += len(page_chunks)
        
#     return JSONResponse(
#         content={
#             "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
#             "inserted_items_count": inserted_items_count
#         }
#     ) 
RATE_LIMIT = 40  
TIME_WINDOW = 60 / RATE_LIMIT 
MAX_RETRIES = 5 

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = ProjectModel()
    chunk_model = ChunkModel()

    project = project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = chunk_model.get_project_chunks(project_id=project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Attempt to insert into the vector database
                is_inserted = nlp_controller.index_into_vector_db(
                    project=project,
                    chunks=page_chunks,
                    do_reset=push_request.do_reset,
                    chunks_ids=chunks_ids
                )
                if not is_inserted:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
                    )

                # Break out of the retry loop on success
                break

            except TooManyRequestsError as e:
                # If rate limit is hit, wait with exponential backoff
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

        if retries == MAX_RETRIES:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"signal": ResponseSignal.TOO_MANY_REQUESTS_ERROR.value}
            )

        inserted_items_count += len(page_chunks)

        # Sleep to respect the rate limit
        await asyncio.sleep(TIME_WINDOW)

    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = ProjectModel()


    project = project_model.get_project_or_create_one(
        project_id=project_id
    )

    
    nlp_controller = NLPController(
    vectordb_client=request.app.vectordb_client,
    generation_client=request.app.generation_client,
    embedding_client=request.app.embedding_client,
    )
    collection_info = nlp_controller.get_vector_db_collection_info (project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

# 



@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = ProjectModel()

    project = project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
         template_parser=request.app.template_parser,
        
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )


def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        

        collection_name = self.create_collection_name(project_id=project.project_id)

        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)

        if not vector or len(vector) == 0:
            return False

        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return results