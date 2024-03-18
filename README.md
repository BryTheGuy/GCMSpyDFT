# GCMSpyDFT

## Required dependences
- openbabel
- py2opsin

## Install dependences
1) setup new env `conda create --name {myenv}`
2) activate new env `conda activate {myenv}`
3) install openbabel python bindings `conda install -c conda-forge openbabel`
4) install py2opsin `pip install py2opsin`

## Running GCMSpyDFT
1) Download package `git clone https://github.com/BryTheGuy/GCMSpyDFT.git`
2) Navigate to install location. `cd GCMSpyDFT`
3) Make sure you are in the correct environmnt `conda activate {myenv}`
4) Optionally you can create the config file `python3 config.py`
5) Run GCMSpyDFT.py `python3 GCMSpyDFT.py {input file}`

## Licenses
 - [Openbabel](https://openbabel.org/) is under the GLP-2.0 license
 - [Py2Opsin](https://github.com/JacksonBurns/py2opsin) is under the MIT license
 - [Opsin](https://opsin.ch.cam.ac.uk/) which py2opsin uses is also under the MIT license
