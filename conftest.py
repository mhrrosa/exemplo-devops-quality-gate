import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir que os módulos em src_alta e src_baixa sejam encontrados
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
