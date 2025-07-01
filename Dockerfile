FROM ubuntu:22.04

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y curl python3-pip git
RUN pip install clearml

COPY train_model.py /train_model.py
RUN  chmod u+x /train_model.py
ENTRYPOINT ["python3",  "/train_model.py"]
