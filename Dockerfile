FROM nvcr.io/nvidia/pytorch:22.11-py3 

COPY ../miniconda3 /workspace

RUN mkdir -p /root/.config/glymur

COPY . /workspace

COPY glymurrc /root/.config/glymur/

RUN pip install -r requirements.txt
