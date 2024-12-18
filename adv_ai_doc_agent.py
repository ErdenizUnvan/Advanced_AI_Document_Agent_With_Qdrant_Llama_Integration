#docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
import os, logging, qdrant_client
from llama_index.llms.ollama import Ollama
from llama_index.core import StorageContext, Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
#from llama_index.readers.file.pdf import PDFReader
from llama_index.readers.file.docs.base import PDFReader
#from llama_index.node_parser.simple import SimpleNodeParser
from llama_index.core.node_parser import SimpleNodeParser
from qdrant_client.http.models import VectorParams
import litserve as ls

class DocumentChatAPI(ls.LitAPI):
    def setup(self, device):
        # Text splitting ayarları
        chunk_size = 512  # Bölüm boyutu (her bir bölümdeki karakter sayısı)
        chunk_overlap = 50  # Bölümler arasındaki çakışma

        # Llama modelinin yerel URL'sini ayarlıyoruz
        Settings.llm = Ollama(model="llama3.2", base_url="http://127.0.0.1:11434", request_timeout=120.0)

        # Embed modeli ayarlıyoruz
        Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")
        #Embedding işlemi, metinleri sayısal bir forma dönüştürmek anlamına gelir
        #Embedding'in genel amacı, metinlerin anlamlarını vektörler olarak ifade etmektir.

        # Qdrant istemcisini ayarlıyoruz
        client = qdrant_client.QdrantClient(host="192.168.56.111", port=6333)

        #BAAI/bge-large-en-v1.5 embedding modeli, her metin parçasını 1024 boyutlu bir vektöre dönüştürür.

        #Cosine: Kosinüs benzerliği mesafe ölçümü olarak.
        #Cosine genellikle vektörlerin benzerliklerini ölçmek için tercih edilir.
        #Kosinüs benzerliği iki vektör arasındaki benzerliği ölçmek için kullanılan matematiksel bir yöntemdir
        #Bu yöntem, iki vektör arasındaki açıyı hesaplar ve benzerliği bu açıya göre değerlendirir.
        #İki vektör arasındaki açı ne kadar küçükse, vektörler o kadar benzerdir
        #Kosinüs benzerliği, vektörlerin büyüklüğünü (uzunluğunu) değil, yönünü dikkate alır.
        #Örneğin, aynı içeriğe sahip uzun ve kısa bir metin arasında benzerliği doğru şekilde ölçer.
        #Kosinüs benzerliği, metin veya belgelerin benzerliğini ölçmek için çok uygundur çünkü metinler vektörlere dönüştürülür (örneğin, embedding ile).
        #Kosinüs benzerliği iki cümlenin veya belgenin semantik olarak ne kadar benzediğini ölçmek için kullanılır.
        client.recreate_collection(
            collection_name="doc_search_collection",
            vectors_config=VectorParams(size=1024, distance="Cosine")
        )
        #Bu vektörler, Qdrant vektör veri tabanlarına kaydedilir ve sorgular bu vektörlerle eşleştirilir
        #Modelin çıkış vektör boyutuyla, Qdrant'ın koleksiyonunda kullanılan vector dimension değeri aynı olmalıdır.
        #embedding modelimiz BAAI/bge-large-en-v1.5 1024 boyutlu vektör ürettiği için Qdrant'ın da bu boyutu desteklemesi gerekir.

        vector_store = QdrantVectorStore(client=client, collection_name="doc_search_collection")

        # Depolama bağlamını oluşturuyoruz
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # PDF okuyucu
        pdf_reader = PDFReader()

        # Belgeleri belirtilen dizinden yüklüyoruz
        documents = pdf_reader.load_data("C:\\Users\\Dell\\llama3_2\\documents\\1728286846_the_nestle_hr_policy_pdf_2012.pdf")

        # Node parser'ı yapılandırıyoruz
        node_parser = SimpleNodeParser(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


        # Belgelerden indeks oluşturuyoruz

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            node_parser=node_parser  #Text splitting için ayarları burada sağlıyoruz
        )
        self.query_engine = index.as_query_engine()


    def decode_request(self, request):
        return request["query"]

    def predict(self, query):
        return self.query_engine.query(query)

    def encode_response(self, output):
        return {"output": output}

if __name__ == "__main__":
    api = DocumentChatAPI()
    server = ls.LitServer(api)
    server.run(port=8000)
