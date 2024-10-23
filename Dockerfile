FROM python:3.10-slim

ADD requirements.txt .

RUN pip install torch~=2.5.0 --index-url https://download.pytorch.org/whl/cpu torchaudio~=2.5.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]