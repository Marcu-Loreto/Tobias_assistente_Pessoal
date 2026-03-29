"""
core/memory.py
Duas camadas de memória do Agente Tobias:
  - RedisMemory  → memória rápida/conversacional (curto prazo, TTL controlado)
  - QdrantMemory → memória semântica (longo prazo, busca por similaridade)
"""
import json
import os
import uuid
from typing import Optional

# -------------------------------------------------------
# Dependências externas — instaladas pelo usuário
# -------------------------------------------------------
try:
    import redis as redis_lib
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from langchain_openai import OpenAIEmbeddings
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


# -------------------------------------------------------
# Configurações (via .env)
# -------------------------------------------------------
REDIS_URL     = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_TTL     = int(os.getenv("REDIS_TTL_SECONDS", 3600))   # 1 hora padrão
QDRANT_URL    = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tobias_memory")
EMBEDDING_DIM = 1536  # text-embedding-3-small / ada-002


# ═══════════════════════════════════════════════════════
# MEMÓRIA RÁPIDA — Redis (curto prazo / sessão)
# ═══════════════════════════════════════════════════════
class RedisMemory:
    """
    Armazena o histórico de mensagens da sessão no Redis.
    Cada sessão tem uma chave única com TTL configurável.
    """

    def __init__(self):
        if not REDIS_AVAILABLE:
            print("[RedisMemory] redis não instalado — memória rápida desativada.")
            self._client = None
            return
        try:
            self._client = redis_lib.from_url(REDIS_URL, decode_responses=True)
            self._client.ping()
            print("[RedisMemory] ✅ Conectado ao Redis.")
        except Exception as e:
            print(f"[RedisMemory] ⚠️  Falha na conexão: {e} — memória rápida desativada.")
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def _key(self, session_id: str) -> str:
        return f"tobias:session:{session_id}:history"

    def load(self, session_id: str) -> list[dict]:
        """Carrega o histórico da sessão do Redis como lista de dicts role/content."""
        if not self.available:
            return []
        raw = self._client.get(self._key(session_id))
        return json.loads(raw) if raw else []

    def save(self, session_id: str, messages: list[dict]) -> None:
        """Persiste o histórico completo da sessão com TTL."""
        if not self.available:
            return
        self._client.setex(self._key(session_id), REDIS_TTL, json.dumps(messages, ensure_ascii=False))

    def append(self, session_id: str, role: str, content: str) -> None:
        """Acrescenta uma única mensagem ao histórico e reseta o TTL."""
        history = self.load(session_id)
        history.append({"role": role, "content": content})
        self.save(session_id, history)

    def clear(self, session_id: str) -> None:
        """Apaga o histórico da sessão."""
        if self.available:
            self._client.delete(self._key(session_id))


# ═══════════════════════════════════════════════════════
# MEMÓRIA SEMÂNTICA — Qdrant (longo prazo / busca vetorial)
# ═══════════════════════════════════════════════════════
class QdrantMemory:
    """
    Armazena pares pergunta-resposta como vetores no Qdrant.
    A cada nova interação, busca as K memórias mais relevantes
    para injetar contexto histórico enriquecido no prompt.
    """

    def __init__(self):
        if not QDRANT_AVAILABLE:
            print("[QdrantMemory] qdrant-client não instalado — memória semântica desativada.")
            self._client = None
            self._embeddings = None
            return
        try:
            self._client = QdrantClient(url=QDRANT_URL, check_compatibility=False)
            self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            self._ensure_collection()
            print("[QdrantMemory] ✅ Conectado ao Qdrant.")
        except Exception as e:
            print(f"[QdrantMemory] ⚠️  Falha na conexão: {e} — memória semântica desativada.")
            self._client = None
            self._embeddings = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def _ensure_collection(self) -> None:
        """Garante que a collection existe no Qdrant."""
        existing = [c.name for c in self._client.get_collections().collections]
        if QDRANT_COLLECTION not in existing:
            self._client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            print(f"[QdrantMemory] Collection '{QDRANT_COLLECTION}' criada.")

    def store(self, user_input: str, assistant_response: str, metadata: Optional[dict] = None) -> None:
        """Vetoriza e armazena o par (input → resposta) no Qdrant."""
        if not self.available:
            return
        try:
            text = f"Usuário: {user_input}\nTobias: {assistant_response}"
            vector = self._embeddings.embed_query(text)
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user_input": user_input,
                    "response": assistant_response,
                    **(metadata or {}),
                },
            )
            self._client.upsert(collection_name=QDRANT_COLLECTION, points=[point])
        except Exception as e:
            print(f"[QdrantMemory] Erro ao armazenar memória: {e}")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Busca as K memórias mais semanticamente similares à query.
        Retorna lista de dicts com 'user_input', 'response' e 'score'.
        """
        if not self.available:
            return []
        try:
            vector = self._embeddings.embed_query(query)
            response = self._client.query_points(
                collection_name=QDRANT_COLLECTION,
                query=vector,
                limit=top_k,
                score_threshold=0.70,  # Só retorna se tiver >= 70% de similaridade
            )
            results = response.points
            return [
                {
                    "user_input": r.payload.get("user_input", ""),
                    "response": r.payload.get("response", ""),
                    "score": round(r.score, 3),
                }
                for r in results
            ]
        except Exception as e:
            print(f"[QdrantMemory] Erro na busca semântica: {e}")
            return []

    def format_context(self, memories: list[dict]) -> str:
        """Formata as memórias encontradas como bloco de contexto para o prompt."""
        if not memories:
            return ""
        lines = ["[MEMÓRIAS RELEVANTES DE INTERAÇÕES ANTERIORES]"]
        for i, m in enumerate(memories, 1):
            lines.append(f"{i}. Usuário perguntou: {m['user_input']}")
            lines.append(f"   Tobias respondeu: {m['response'][:300]}...")
        return "\n".join(lines)

    def reset_collection(self) -> None:
        """Deleta e recria a collection garantindo apagamento profundo de dados antigos."""
        if not self.available:
            return
        try:
            self._client.delete_collection(collection_name=QDRANT_COLLECTION)
            self._ensure_collection()
            print("[QdrantMemory] Collection recriada. Banco resetado.")
        except Exception as e:
            print(f"[QdrantMemory] Erro ao resetar banco C-Level: {e}")


# -------------------------------------------------------
# Instâncias Singleton (inicializadas uma única vez)
# -------------------------------------------------------
redis_memory  = RedisMemory()
qdrant_memory = QdrantMemory()
