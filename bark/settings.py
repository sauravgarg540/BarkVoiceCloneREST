import os

ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT_DIR, "models")
DEFAULT_SPEAKER_DIR = os.path.join(ROOT_DIR, "bark", "assets", "prompts")
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

USE_GPU = os.getenv('USE_GPU', "True").lower() not in ('false', 'f', '0', 'off', 'n', 'no')
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_DIR = os.getenv("EMBEDDINGS_DIR", os.path.join(CUR_PATH, "assets", "prompts"))

DEFAULT_PORT = os.getenv("DEFAULT_PORT", 8009)  # determines the port of the fastapi server


# Defining the getters and setters like this, allows a change of the env variable at runtime for other modules
# This is useful for the server, where the user can change the settings without restarting the server
# Required in cloud environments for example when a volume is mounted after the server is started
def set_embeddings_dir(path):
    global EMBEDDINGS_DIR
    EMBEDDINGS_DIR = path

def get_embeddings_dir():
    global EMBEDDINGS_DIR
    return EMBEDDINGS_DIR


# These settings are used in generation.py and are used in inference
def _cast_bool_env_var(s):
    return s.lower() in ('true', '1', 't')


USE_SMALL_MODELS = _cast_bool_env_var(os.environ.get("SUNO_USE_SMALL_MODELS", "False"))
GLOBAL_ENABLE_MPS = _cast_bool_env_var(os.environ.get("SUNO_ENABLE_MPS", "False"))
OFFLOAD_CPU = _cast_bool_env_var(os.environ.get("SUNO_OFFLOAD_CPU", "False"))
