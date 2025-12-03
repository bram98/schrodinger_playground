This app can simulate the time dependent Schrödinger equation. Quantum mechanics can be quite abstract, so this is a nice way to get a better feel. If you change any buttons you have to press `reset` to implement the changes. Note that the energy should always be constant and any variations in this are caused by numerical innaccuracies. For questions contact b.verreussel@uu.nl

To install this run
```bash
git clone https://github.com/bram98/schrodinger_playground.git
```
in your directory of choice. You can also download the zip files. To install the right packages, start an anaconda terminal. First create a new environment
```bash
conda create -n schrodinger python=3.14
```
and activate it using
```bash
conda activate schrodinger
```
Then go to the directory where the files are downloaded.
```bash
cd ../some/place/on/my/computer/schrodinger_playground
```
Finally install all the required packages.
```bash
pip install -r requirements.txt
```
This can take a while!
Note that by default spyder is not installed in this environment. To run this code in spyder you can start spyder from your "base" environment and right click on the console. In the context menu you can find "new console in environment". The code works best if you run the entire file, instead of running by cell.

<img width="788" height="403" alt="image" src="https://github.com/user-attachments/assets/de9231da-15b3-4b48-bd41-ae14e48fbdcf" />



