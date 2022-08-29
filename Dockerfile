FROM python:3

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY script.py /script.py

COPY microprint_generator.py /microprint_generator.py

ADD /fonts/ /fonts/

CMD ["python", "/script.py"] 
