FROM nvcr.io/nvidia/pytorch:23.01-py3 

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p /root/.config/glymur

COPY ./glymurrc /root/.config/glymur/

COPY . /workspace

RUN chmod +x /workspace/bin/kdu_expand

RUN sed -i 's/\r//' /workspace/step*.sh