"""Ponto de entrada do guia de exame físico ortopédico."""

import logging
import tkinter as tk

from .interface import InterfaceExameFisico

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    root = tk.Tk()
    app = InterfaceExameFisico(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
