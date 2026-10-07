"""
Factory de LLM e Embeddings — Genera Intelligence
==================================================
Instancia o provider correto (Gemini ou OpenAI) a partir de uma referência
`provider:modelo`. Geração, embeddings e juiz são configurados de forma
independente (ver `core/config.py`), o que permite comparar modelos/providers
sem mudar código.

As configurações são lidas em tempo de chamada (nunca no import), para que a
API e o CI subam sem chave: a falha de configuração aparece, com mensagem
clara, na primeira chamada ao provider.
"""

from dataclasses import dataclass
from typing import get_args

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from core.config import Provider, settings

PROVIDERS_SUPORTADOS: tuple[str, ...] = get_args(Provider)


class ConfiguracaoLLMInvalida(ValueError):
    """Configuração de provider/modelo ausente ou inválida."""


@dataclass(frozen=True)
class ModeloRef:
    """Referência a um modelo de um provider (ex.: `gemini:gemini-3.1-flash-lite`)."""

    provider: Provider
    modelo: str

    @classmethod
    def parse(cls, texto: str) -> "ModeloRef":
        """Converte `provider:id` em `ModeloRef`, dividindo só no primeiro `:`."""
        provider, separador, modelo = texto.strip().partition(":")
        if not separador:
            raise ConfiguracaoLLMInvalida(
                f"Referência de modelo inválida: {texto!r}. Use o formato 'provider:modelo'."
            )
        provider = provider.strip().lower()
        modelo = modelo.strip()
        if provider not in PROVIDERS_SUPORTADOS:
            suportados = ", ".join(PROVIDERS_SUPORTADOS)
            raise ConfiguracaoLLMInvalida(
                f"Provider {provider!r} não suportado. Use um de: {suportados}."
            )
        if not modelo:
            raise ConfiguracaoLLMInvalida(
                f"Referência de modelo inválida: {texto!r}. O modelo não pode ser vazio."
            )
        return cls(provider=provider, modelo=modelo)

    def __str__(self) -> str:
        return f"{self.provider}:{self.modelo}"


# ═══════════════════════════════════════════
# RESOLUÇÃO DA CONFIGURAÇÃO ATIVA
# ═══════════════════════════════════════════


def _modelo_llm_legado(provider: str) -> str:
    return settings.OPENAI_MODEL if provider == "openai" else settings.GEMINI_MODEL


def modelo_ativo() -> ModeloRef:
    """Modelo de geração ativo (LLM_PROVIDER + LLM_MODEL ou o legado do provider)."""
    provider = settings.LLM_PROVIDER
    return ModeloRef(provider, settings.LLM_MODEL or _modelo_llm_legado(provider))


def embeddings_ativo() -> ModeloRef:
    """Modelo de embeddings ativo (EMBEDDINGS_* ou o legado do provider)."""
    provider = settings.EMBEDDINGS_PROVIDER
    legado = (
        settings.OPENAI_EMBEDDING_MODEL if provider == "openai" else settings.GEMINI_EMBEDDING_MODEL
    )
    return ModeloRef(provider, settings.EMBEDDINGS_MODEL or legado)


def juiz_ativo() -> tuple[ModeloRef, bool]:
    """Modelo do juiz e se ele é o mesmo modelo do LLM principal (`juiz_mesmo_modelo`).

    JUDGE_PROVIDER vazio = mesmo provider do LLM principal; JUDGE_MODEL vazio =
    modelo legado do provider do juiz (ou o LLM_MODEL, se o provider for o mesmo).
    """
    principal = modelo_ativo()
    provider = settings.JUDGE_PROVIDER or principal.provider
    if settings.JUDGE_MODEL:
        modelo = settings.JUDGE_MODEL
    elif provider == principal.provider:
        modelo = principal.modelo
    else:
        modelo = _modelo_llm_legado(provider)
    ref = ModeloRef(provider, modelo)
    return ref, ref == principal


# ═══════════════════════════════════════════
# VALIDAÇÃO
# ═══════════════════════════════════════════


def _validar(ref: ModeloRef, variavel_modelo: str) -> None:
    """Falha cedo, com mensagem clara, quando o provider não está configurado."""
    if ref.provider not in PROVIDERS_SUPORTADOS:
        raise ConfiguracaoLLMInvalida(f"Provider {ref.provider!r} não suportado.")
    if ref.provider == "openai":
        if not ref.modelo:
            raise ConfiguracaoLLMInvalida(
                f"Modelo OpenAI não definido. Defina {variavel_modelo} para usar o provider openai."
            )
        if not settings.OPENAI_API_KEY:
            raise ConfiguracaoLLMInvalida(
                "OPENAI_API_KEY não definida. Configure a chave para usar o provider openai."
            )


# ═══════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════


def build_llm(
    ref: ModeloRef | None = None,
    *,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
    """Constrói o chat model do `ref` (default: modelo ativo).

    `max_tokens`/`temperature` `None` usam LLM_MAX_TOKENS/LLM_TEMPERATURE.
    """
    ref = ref or modelo_ativo()
    _validar(ref, "LLM_MODEL (ou OPENAI_MODEL)")
    max_tokens = settings.LLM_MAX_TOKENS if max_tokens is None else max_tokens
    temperature = settings.LLM_TEMPERATURE if temperature is None else temperature

    # Hoje `temperature` é sempre enviada (LLM_TEMPERATURE é float, default 0.3).
    # O ramo sem temperature só roda se ela vier None; omiti-la para modelos que
    # a rejeitam (ex.: modelos de raciocínio) fica para o M3.
    opcionais: dict = {} if temperature is None else {"temperature": temperature}

    if ref.provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=ref.modelo,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=max_tokens,
            **opcionais,
        )

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=ref.modelo,
        google_api_key=settings.GOOGLE_API_KEY,
        max_output_tokens=max_tokens,
        convert_system_message_to_human=True,
        **opcionais,
    )


def build_embeddings(ref: ModeloRef | None = None) -> Embeddings:
    """Constrói os embeddings do `ref` (default: embeddings ativos)."""
    ref = ref or embeddings_ativo()
    _validar(ref, "EMBEDDINGS_MODEL (ou OPENAI_EMBEDDING_MODEL)")

    if ref.provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=ref.modelo, api_key=settings.OPENAI_API_KEY)

    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(
        model=ref.modelo,
        google_api_key=settings.GOOGLE_API_KEY,
        task_type="RETRIEVAL_DOCUMENT",
    )


def build_judge_llm() -> BaseChatModel:
    """Constrói o LLM-juiz (JUDGE_*; vazio = LLM principal), com temperatura 0."""
    ref, _ = juiz_ativo()
    _validar(ref, "JUDGE_MODEL (ou OPENAI_MODEL)")
    return build_llm(ref, temperature=0)


def extrair_texto_resposta(conteudo) -> str:
    """Normaliza `AIMessage.content` para string.

    Alguns providers (ex.: Gemini via langchain-google-genai, em versões
    recentes) retornam o conteúdo como uma lista de blocos estruturados
    (`[{"type": "text", "text": "..."}]`) em vez de uma string simples.
    Outros (ex.: OpenAI) já retornam string diretamente.
    """
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = [
            bloco.get("text", "")
            for bloco in conteudo
            if isinstance(bloco, dict) and bloco.get("type") == "text"
        ]
        return "".join(partes)
    return str(conteudo)
