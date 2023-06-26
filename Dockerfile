FROM nvcr.io/nvidia/pytorch:23.01-py3 

COPY . /workspace

RUN mkdir -p /root/.config/glymur

COPY ./glymurrc /root/.config/glymur/

RUN pip install -r requirements.txt
