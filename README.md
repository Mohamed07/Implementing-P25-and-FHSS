# Implementing-P25-and-FHSS
Impelememtation of P25 Communication protocol with Frequency Hopping spread spectrum technique for secure transmisson

In This Repository, you will find a baseband transmission of P25 Communication Protocol. This is implemented in the file named 
"Baseband_op25_Tx_Rx.grc".

Also you will find the Transmiiter and Reciever of the Frequency Hopping Spread Spectrum Technique. Besides the Python codes of some blocks. 

"FHSS_Txer.grc" : In this file we have implemented the transmitter of FHSS, using a defined block of inserting Tags to the downstream.

"hopper.py" : This file is python code of Frequency hopping block that insert tags.
"FHSS_hopper.xml" : This file is the XML of the Hopping Block.

"sync_final_800Khz.grc" : This GRC file is the synchronization in the receiving side to detect the start of transmission.
"FHSS_Rxer_Synthesizer.grc" : This grc file is to generate the oscillator of  changable frequency using VCO to generate the frequency hopping sequence list.

"Rx.py" : This file is python code for the synthesizer at the reciver side.
"FHSS_Receiver_Rx.xml" : The XML file for the receiver synthesizer.

"ED_Hier.grc" : This GRC file is a hierarchical block of energy detection using fourier analysis.

"framing_tx_rx.grc" : Replaces the vocoder with built framing to reduce the processing time. Before you run this file modify the path of the input and output files.

"encoded_voice.txt" : This file is an encoded voice using AMBE kit.
