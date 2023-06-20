from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from llama_index import (
    BeautifulSoupWebReader,
    LLMPredictor,
    PromptHelper,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index import GPTVectorStoreIndex


# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

BASE_URL = "./indices/"


def get_service_context():
    # define LLM
    max_input_size = 4096
    num_output = 2048  # 2048に拡大
    # max_chunk_overlap = 20
    prompt_helper = PromptHelper(max_input_size, num_output)
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(model_name="gpt-4", temperature=0, max_tokens=2048)
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )
    return service_context


def create_index_from_urls(urls, index_name) -> None:
    # llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, max_tokens=2048))
    service_context = get_service_context()

    documents = BeautifulSoupWebReader().load_data(urls=urls)
    index = GPTVectorStoreIndex.from_documents(
        documents, service_context=service_context
    )
    index.storage_context.persist(persist_dir=BASE_URL + index_name)


def create_index_from_files(file_paths, index_name):
    # define LLM
    service_context = get_service_context()

    documents = SimpleDirectoryReader(input_files=file_paths).load_data()
    index = GPTVectorStoreIndex.from_documents(
        documents, service_context=service_context
    )
    index.as_chat_engine()
    index.storage_context.persist(persist_dir=BASE_URL + index_name)


def get_chat_engine(index_name, chat_history):
    index = load_index_from_storage(
        StorageContext.from_defaults(persist_dir=BASE_URL + index_name)
    )
    chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, chat_history=chat_history
    )
    return chat_engine


def query(query, index_name, chat_history):
    index = load_index_from_storage(
        StorageContext.from_defaults(persist_dir=BASE_URL + index_name)
    )
    chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, chat_history=chat_history
    )
    return chat_engine.chat(query)


if __name__ == "__main__":
    load_dotenv()

    ### Create index

    # title = 'okx'
    # title = 'okx2'
    # article_urls = ['https://www.okx.com/docs-v5/en/']

    # title = 'osouji'
    # article_urls = ['https://www.osoujihonpo.com/house-cleaning/faq']
    # create_index_from_urls(article_urls, './indices/' + title)

    # title = 'superchat'
    # file_paths = ['/Users/kokinakamura/git/superchat/static/js/webflow.js', '/Users/kokinakamura/git/superchat/templates/index.html']
    # create_index_from_files(file_paths, './indices/' + title)

    # title = "superchat2"
    # file_paths = [
    #     "/Users/kokinakamura/git/superchat/static/js/webflow.js",
    #     "/Users/kokinakamura/git/superchat/templates/model.html",
    # ]
    # create_index_from_files(file_paths, "./indices/" + title)

    # # title = "llama_index"

    # title = "05851012-bb3b-4c2e-bf59-e1c02b694dd2"

    ### Query
    # index = load_index_from_storage(
    #     StorageContext.from_defaults(persist_dir=BASE_URL + title)
    # )
    # query_engine = index.as_query_engine()
    # # answer = query_engine.query("how to get latest btc price?")

    # trial()
