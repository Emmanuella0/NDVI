"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget

import spectral.io.envi as envi
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")


def select_bands(output_file):
    # Ouvrir le fichier
    img = tiff.imread(output_file)
    
    # Nombre de bandes et dimensions de l'image
    b, h, w = img.shape
    
    # Affichage de toutes les bandes
    for i in range(b):
        plt.imshow(img[i], cmap='gray')
        plt.title(f"Bande {i+1}")
        plt.axis('off')
        plt.show()
    
    # Demander à l'utilisateur de selectionner une bande rouge et une bande proche infra rouge
    while True:
        red_band = int(input("Selectionnez une bande rouge (indice entre 1 et %d) : " % b))
        if red_band < 1 or red_band > b:
            print("Bande invalide. Veuillez réessayer.")
            continue
        else:
            break
            
    while True:
        nir_band = int(input("Selectionnez une bande proche infra rouge (indice entre 1 et %d) : " % b))
        if nir_band < 1 or nir_band > b:
            print("Bande invalide. Veuillez réessayer.")
            continue
        else:
            break
    
    # Extraire les bandes sélectionnées
    red = img[red_band-1]
    nir = img[nir_band-1]
    
    # Affichage des images sélectionnées
    fig, ax = plt.subplots(ncols=2, figsize=(10, 10))
    ax[0].imshow(red, cmap='gray')
    ax[0].set_title(f"Bande {red_band}")
    ax[0].axis('off')
    ax[1].imshow(nir, cmap='gray')
    ax[1].set_title(f"Bande {nir_band}")
    ax[1].axis('off')
    plt.show()
    
    # Retourner les images sélectionnées avec leur numéro de bande
    return (red, red_band), (nir, nir_band)

def calculate_ndvi(red, nir):
    # Calculer la NDVI
    ndvi = (nir - red) / (nir + red)
    
    # Afficher l'image de la NDVI avec un titre
    plt.imshow(ndvi, cmap='gray')
    plt.title("NDVI")
    plt.axis('off')
    plt.show()
    
    # Retourner l'image de la NDVI
    return ndvi


@magic_factory
def do_ndvi(image_layer: "napari.layers.Image"):
    widget = QWidget()
    layout = QHBoxLayout()
    button_select_bands = QPushButton("Select Bands")
    button_run_ndvi = QPushButton("Run NDVI")
    
    ndvi = None
    
    def select_bands_and_calculate_ndvi():
        nonlocal ndvi
        red, nir = select_bands(image_layer.data)
        ndvi = calculate_ndvi(red, nir)
    
    button_select_bands.clicked.connect(select_bands_and_calculate_ndvi)
    button_run_ndvi.clicked.connect(select_bands_and_calculate_ndvi)
    
    layout.addWidget(button_select_bands)
    layout.addWidget(button_run_ndvi)
    widget.setLayout(layout)
    
    # Ajouter le widget à la barre d'outils de Napari
    tb = image_layer.viewer.toolbar
    tb.addWidget(widget)
    
    return ndvi


